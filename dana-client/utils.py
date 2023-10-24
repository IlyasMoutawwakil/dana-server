import re
import json
import logging
from pathlib import Path
from requests import Session
from typing import Any, Dict, Optional

import shutil
import coloredlogs
import pandas as pd
from omegaconf import OmegaConf

AVERAGE_RANGE = 5  # 5 percent
AVERAGE_MIN_COUNT = 3  # 3 samples

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("dana-client")
coloredlogs.install(level="INFO", logger=LOGGER)


def add_new_project(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    project_description: str = "",
    override: bool = False,
) -> None:
    dana_project_url = f"{dana_url}/admin/addProject"
    project_payload = {
        "projectId": project_id,
        "description": project_description,
        "users": "admin",
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_project_url,
        bearer_token=bearer_token,
        payload=project_payload,
    )


def add_new_optimum_build(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    build_id: str,
    build_hash: str,
    build_abbrev_hash: str,
    build_author_name: str,
    build_author_email: str,
    build_subject: str,
    build_url: str,
    override: bool = False,
) -> None:
    dana_build_url = f"{dana_url}/apis/addBuild"
    build_payload = {
        "projectId": project_id,
        "build": {
            "buildId": build_id,
            "infos": {
                "hash": build_hash,
                "abbrevHash": build_abbrev_hash,
                "authorName": build_author_name,
                "authorEmail": build_author_email,
                "subject": build_subject,
                "url": build_url,
            },
        },
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_build_url,
        bearer_token=bearer_token,
        payload=build_payload,
    )


def add_new_optimum_series(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    series_id: str,
    average_range: int,
    average_min_count: int,
    series_description: Optional[str] = None,
    better_criterion: str = "lower",
    override: bool = False,
) -> None:
    dana_series_url = f"{dana_url}/apis/addSerie"
    series_payload = {
        "projectId": project_id,
        "serieId": series_id,
        "analyse": {
            "benchmark": {
                "range": average_range,
                "required": average_min_count,
                "trend": better_criterion,
            }
        },
        "override": override,
    }

    if series_description is not None:
        series_payload["description"] = series_description

    post_to_dana(
        session=session,
        dana_url=dana_series_url,
        bearer_token=bearer_token,
        payload=series_payload,
    )


def add_new_sample(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    build_id: str,
    series_id: str,
    sample_value: int,
    override: bool = False,
) -> None:
    dana_sample_url = f"{dana_url}/apis/addSample"
    sample_payload = {
        "projectId": project_id,
        "serieId": series_id,
        "sample": {"buildId": build_id, "value": sample_value},
        "override": override,
    }

    post_to_dana(
        session=session,
        dana_url=dana_sample_url,
        bearer_token=bearer_token,
        payload=sample_payload,
    )


def authenticate(
    session: Session,
    dana_url: str,
    username: str,
    password: str,
) -> Session:
    if dana_url.startswith("http://"):
        session.post(
            f"{dana_url}/login",
            data=json.dumps({"username": username, "password": password}),
            headers={"Content-Type": "application/json"},
        )

    return session


def post_to_dana(
    session: Session,
    dana_url: str,
    bearer_token: str,
    payload: Dict[str, Any],
) -> None:
    data = json.dumps(payload)

    response = session.post(
        dana_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        },
    )

    code = response.status_code
    LOGGER.info(f"API response code: {code}")

    if code != 200:
        raise RuntimeError("API request failed")


def publish_build(
    session: Session,
    dana_url: str,
    bearer_token: str,
    project_id: str,
    build_id: int,
    build_info: Dict[str, str],
    build_folder: Path,
) -> None:
    LOGGER.info(f" + Publishing build {build_id}")
    add_new_optimum_build(
        session=session,
        dana_url=dana_url,
        bearer_token=bearer_token,
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
        series_description = OmegaConf.to_yaml(OmegaConf.load(configs[0]))

        # Latency series
        series_id = f"{series_foler.name}_latency(ms)"
        LOGGER.info(f"\t + Publishing series {series_id}")
        try:
            add_new_optimum_series(
                session=session,
                bearer_token=bearer_token,
                dana_url=dana_url,
                project_id=project_id,
                series_id=series_id,
                series_description=series_description,
                better_criterion="lower",
                average_range=AVERAGE_RANGE,
                average_min_count=AVERAGE_MIN_COUNT,
                override=True,
            )
        except RuntimeError:
            LOGGER.info(f"\t + Series {series_id} already exists")

        add_new_sample(
            session=session,
            dana_url=dana_url,
            bearer_token=bearer_token,
            project_id=project_id,
            build_id=build_id,
            series_id=series_id,
            sample_value=latency_ms,
            override=True,
        )

        # # Memory series
        # series_id = f"{series_foler.name}_memory(MB)"
        # LOGGER.info(f"\t + Publishing series {series_id}")
        # try:
        #     add_new_optimum_series(
        #         session=session,
        #         dana_url=dana_url,
        #         bearer_token=bearer_token,
        #         project_id=project_id,
        #         series_id=series_id,
        #         series_description=series_description,
        #         better_criterion="lower",
        #         average_range=AVERAGE_RANGE,
        #         average_min_count=AVERAGE_MIN_COUNT,
        #         override=True,
        #     )
        # except RuntimeError:
        #     LOGGER.info(f"\t + Series {series_id} already exists")

        # add_new_sample(
        #     session=session,
        #     dana_url=dana_url,
        #     bearer_token=bearer_token,
        #     project_id=project_id,
        #     build_id=build_id,
        #     series_id=series_id,
        #     sample_value=memory_mb,
        #     override=True,
        # )
