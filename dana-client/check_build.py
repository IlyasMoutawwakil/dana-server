import os
import json
import argparse
from requests import Session

from dana_utils import authenticate
from dana_constants import DANA_SPACE_URL


ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
API_TOKEN = os.environ.get("API_TOKEN", None)
HF_TOKEN = os.environ.get("HF_TOKEN", None)


def check_project(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
):
    response = session.get(
        f"{dana_url}/apis/getBuild",
        data=json.dumps({"projectId": project_id, "buildId": 0}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(f"Failed to get project {project_id}")

    return response.json()


def check_build(
    session: Session,
    dana_url: str,
    api_token: str,
    project_id: str,
    build_id: int,
):
    out = session.get(
        f"{dana_url}/apis/getBuild",
        data=json.dumps({"projectId": project_id, "buildId": build_id}),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
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
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        auth_token=HF_TOKEN,
    )

    project = check_project(
        session=session,
        dana_url=DANA_SPACE_URL,
        api_token=API_TOKEN,
        project_id=project_id,
    )

    build = check_build(
        session=session,
        dana_url=DANA_SPACE_URL,
        api_token=API_TOKEN,
        project_id=project_id,
        build_id=build_id,
    )
