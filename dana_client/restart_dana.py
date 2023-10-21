import os
import time
import json
from pathlib import Path
from requests import Session

from huggingface_hub import snapshot_download, HfApi
from dana_client.utils import LOGGER, authenticate, publish_build, add_new_project


HF_TOKEN = os.environ.get("HF_TOKEN", None)
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "secret")

DANA_SPACE_ID = "IlyasMoutawwakil/dana-space"
DANA_DATASET_ID = "IlyasMoutawwakil/dana-dataset"
DANA_SPACE_URL = "https://ilyasmoutawwakil-dana-space.hf.space"


def restart_space(
    space_id: str,
    hf_token: str,
) -> None:
    LOGGER.info(f"Restarting Space {space_id}")
    HfApi().restart_space(repo_id=space_id, token=hf_token, factory_reboot=True)

    while True:
        runtime = HfApi().get_space_runtime(repo_id=space_id, token=hf_token)

        if runtime.stage == "RUNNING":
            break

        elif runtime.stage in ["BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"]:
            raise RuntimeError(f"Space is in stage {runtime.stage}")

        LOGGER.info(f"Space is in stage {runtime.stage}, waiting for it to be ready...")
        time.sleep(5)

    LOGGER.info("Space is running!")


def publish_backup(
    session: Session,
    dana_url: str,
    bearer_token: str,
    backup_path: Path,
) -> None:
    for project_path in backup_path.iterdir():
        if not project_path.is_dir():
            continue

        project_id = project_path.name
        LOGGER.info(f" + Publishing project {project_id}")
        add_new_project(
            session=session,
            dana_url=dana_url,
            bearer_token=bearer_token,
            project_id=project_id,
            override=True,
        )

        for build_path in project_path.iterdir():
            if not build_path.is_dir():
                continue

            build_info = json.load(open(build_path / "build_info.json"))

            build_id = int(build_path.name)
            LOGGER.info(f" + Publishing build {build_id}")
            publish_build(
                session=session,
                dana_url=dana_url,
                bearer_token=bearer_token,
                project_id=project_id,
                build_id=build_id,
                build_info=build_info,
                build_folder=build_path,
                override=True,
            )


if __name__ == "__main__":
    restart_space(
        space_id=DANA_SPACE_ID,
        hf_token=HF_TOKEN,
    )

    LOGGER.info("Downloading backup dataset")
    dataset_path = Path(
        snapshot_download(
            repo_id=DANA_DATASET_ID,
            repo_type="dataset",
            token=HF_TOKEN,
        )
    )

    session = Session()
    LOGGER.info(" + Authenticating")
    authenticate(
        session=session,
        dana_url=DANA_SPACE_URL,
        username=USERNAME,
        password=PASSWORD,
    )

    LOGGER.info("Publishing backup dataset")
    publish_backup(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
        backup_path=dataset_path,
    )
    LOGGER.info("Finished publishing backup dataset")
