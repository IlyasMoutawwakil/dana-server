import os
import json
from pathlib import Path
from requests import Session

from huggingface_hub import HfApi
from dana_client.utils import LOGGER, authenticate, publish_build

HF_TOKEN = os.environ.get("HF_TOKEN", None)
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "secret")

DANA_SPACE_ID = "IlyasMoutawwakil/dana-space"
DANA_DATASET_ID = "IlyasMoutawwakil/dana-dataset"
DANA_SPACE_URL = "https://ilyasmoutawwakil-dana-space.hf.space"


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
        username=USERNAME,
        password=PASSWORD,
    )

    LOGGER.info(" + Publishing build to DANA dashboard")
    publish_build(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
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
