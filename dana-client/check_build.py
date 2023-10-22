import os
import json
import argparse
from requests import Session

from utils import LOGGER, authenticate

HF_TOKEN = os.environ.get("HF_TOKEN", None)
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "secret")

DANA_SPACE_ID = "IlyasMoutawwakil/dana-space"
DANA_DATASET_ID = "IlyasMoutawwakil/dana-dataset"
DANA_SPACE_URL = "https://ilyasmoutawwakil-dana-space.hf.space"


def get_project(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
):
    response = session.get(
        f"{dana_url}/apis/getBuild",
        data=json.dumps({"projectId": project_id, "buildId": 0}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"Failed to get project {project_id}")

    return response.json()


def get_build(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    build_id: int,
):
    out = session.get(
        f"{dana_url}/apis/getBuild",
        data=json.dumps({"projectId": project_id, "buildId": build_id}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        },
    )

    if len(out.json()) == 0:
        raise RuntimeError(f"Failed to get build {build_id}")

    return out.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--build-id", type=int, required=True)

    args = parser.parse_args()

    build_id = args.build_id
    project_id = args.project_id

    session = Session()

    session = authenticate(
        session=session,
        dana_url=DANA_SPACE_URL,
        username=USERNAME,
        password=PASSWORD,
    )

    project = get_project(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
        project_id=project_id,
    )

    build = get_build(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
        project_id=project_id,
        build_id=build_id,
    )
