import os
import json
import shutil
from typing import Dict
from pathlib import Path
from requests import Session

from huggingface_hub import HfApi
from omegaconf import OmegaConf
import pandas as pd

from dana_constants import DANA_SPACE_URL, DANA_DATASET_ID
from dana_utils import (
    LOGGER,
    authenticate,
    add_new_sample,
    add_new_build,
    add_new_series,
)


ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
API_TOKEN = os.environ.get("API_TOKEN", None)
HF_TOKEN = os.environ.get("HF_TOKEN", None)

AVERAGE_RANGE = 5  # 5 percent
AVERAGE_MIN_COUNT = 3  # 3 samples


def publish_build(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: int,
    build_info: Dict[str, str],
    build_folder: Path,
) -> None:
    LOGGER.info(f" + Publishing build {build_id}")
    add_new_build(
        session=session,
        dana_url=dana_url,
        api_token=api_token,
        project_id=project_id,
        build_id=build_id,
        build_url=build_info["build_url"],
        build_hash=build_info["build_hash"],
        build_abbrev_hash=build_info["build_abbrev_hash"],
        build_author_name=build_info["build_author_name"],
        build_author_email=build_info["build_author_email"],
        build_subject=build_info["build_subject"],
        override=True,
    )

    for series_foler in build_folder.iterdir():
        if not series_foler.is_dir():
            continue

        configs = list(series_foler.glob("*/hydra_config.yaml"))
        inference_results = list(series_foler.glob("*/inference_results.csv"))

        if len(inference_results) != 1 or len(configs) != 1:
            LOGGER.info(f" + Skipping {series_foler.name}")
            shutil.rmtree(series_foler)
            continue

        inference_results = pd.read_csv(inference_results[0]).to_dict(orient="records")
        latency_ms = inference_results[0]["forward.latency(s)"] * 1000
        memory_mb = inference_results[0]["forward.peak_memory(MB)"]
        if "generate.throughput(tokens/s)" in inference_results[0]:
            throughput_tok_s = inference_results[0]["generate.throughput(tokens/s)"]
        else:
            throughput_tok_s = None
        series_description = OmegaConf.to_yaml(OmegaConf.load(configs[0]))

        # Latency series
        series_id = f"{series_foler.name}_latency(ms)"
        LOGGER.info(f"\t + Publishing series {series_id}")
        add_new_series(
            session=session,
            api_token=api_token,
            dana_url=dana_url,
            project_id=project_id,
            series_id=series_id,
            series_description=series_description,
            better_criterion="smaller",
            average_range=AVERAGE_RANGE,
            average_min_count=AVERAGE_MIN_COUNT,
            override=True,
        )

        LOGGER.info(
            f"\t + Publishing sample for series {series_id} and build {build_id}"
        )
        add_new_sample(
            session=session,
            dana_url=dana_url,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
            series_id=series_id,
            sample_value=latency_ms,
            override=True,
        )

        # Memory series
        series_id = f"{series_foler.name}_memory(MB)"
        LOGGER.info(f"\t + Publishing series {series_id}")
        add_new_series(
            session=session,
            dana_url=dana_url,
            api_token=api_token,
            project_id=project_id,
            series_id=series_id,
            series_description=series_description,
            better_criterion="smaller",
            average_range=AVERAGE_RANGE,
            average_min_count=AVERAGE_MIN_COUNT,
            override=True,
        )

        LOGGER.info(
            f"\t + Publishing sample for series {series_id} and build {build_id}"
        )
        add_new_sample(
            session=session,
            dana_url=dana_url,
            api_token=api_token,
            project_id=project_id,
            build_id=build_id,
            series_id=series_id,
            sample_value=memory_mb,
            override=True,
        )

        # Throughput series
        if throughput_tok_s is not None:
            series_id = f"{series_foler.name}_throughput(tokens/s)"
            LOGGER.info(f"\t + Publishing series {series_id}")
            add_new_series(
                session=session,
                dana_url=dana_url,
                api_token=api_token,
                project_id=project_id,
                series_id=series_id,
                series_description=series_description,
                better_criterion="higher",
                average_range=AVERAGE_RANGE,
                average_min_count=AVERAGE_MIN_COUNT,
                override=True,
            )

            LOGGER.info(
                f"\t + Publishing sample for series {series_id} and build {build_id}"
            )
            add_new_sample(
                session=session,
                dana_url=dana_url,
                api_token=api_token,
                project_id=project_id,
                build_id=build_id,
                series_id=series_id,
                sample_value=throughput_tok_s,
                override=True,
            )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--build-id", type=int, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-folder", type=Path, required=True)

    parser.add_argument("--build-hash", type=str, required=True)
    parser.add_argument("--build-abbrev-hash", type=str, required=True)
    parser.add_argument("--build-author-name", type=str, required=True)
    parser.add_argument("--build-author-email", type=str, required=True)
    parser.add_argument("--build-subject", type=str, required=True)
    parser.add_argument("--build-url", type=str, required=True)

    args = parser.parse_args()

    build_id = args.build_id
    project_id = args.project_id
    build_folder = args.build_folder

    build_info = {
        "build_hash": args.build_hash,
        "build_abbrev_hash": args.build_abbrev_hash,
        "build_author_name": args.build_author_name,
        "build_author_email": args.build_author_email,
        "build_subject": args.build_subject,
        "build_url": args.build_url,
    }

    session = Session()

    LOGGER.info(" + Authenticating to DANA dashboard")
    authenticate(
        session=session,
        dana_url=DANA_SPACE_URL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        auth_token=HF_TOKEN,
    )

    LOGGER.info(" + Publishing build to DANA dashboard")
    publish_build(
        session=session,
        dana_url=DANA_SPACE_URL,
        api_token=API_TOKEN,
        project_id=project_id,
        build_id=build_id,
        build_info=build_info,
        build_folder=build_folder,
    )

    LOGGER.info(" + Saving build info")
    with open(build_folder / "build_info.json", "w") as f:
        json.dump(build_info, f)

    LOGGER.info(" + Uploading experiments folder to backup dataset")
    HfApi().upload_folder(
        repo_id=DANA_DATASET_ID,
        folder_path="experiments",
        path_in_repo=f"{project_id}/{build_id}",
        delete_patterns="*",  # to rewrite the folder
        repo_type="dataset",
        token=HF_TOKEN,
    )
