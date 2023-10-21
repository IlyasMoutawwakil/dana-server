import os
import random
from requests import Session

from utils import (
    LOGGER,
    authenticate,
    add_new_project,
    add_new_optimum_build,
    add_new_optimum_series,
    add_new_sample,
)

HF_TOKEN = os.environ.get("HF_TOKEN", None)
USERNAME = os.environ.get("USERNAME", "admin")
PASSWORD = os.environ.get("PASSWORD", "admin")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "secret")

DANA_SPACE_URL = "http://localhost:7000"

if __name__ == "__main__":
    project_id = "Dummy-Project"
    series_id = "Dummy-Series"

    session = Session()

    LOGGER.info(" + Authenticating to DANA dashboard")
    authenticate(
        session=session,
        dana_url=DANA_SPACE_URL,
        username=USERNAME,
        password=PASSWORD,
    )

    LOGGER.info(" + Publishing project")
    add_new_project(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
        project_id=project_id,
        project_description="Dummy Dummy Dummy",
        override=True,
    )

    LOGGER.info(" + Publishing series")
    add_new_optimum_series(
        session=session,
        dana_url=DANA_SPACE_URL,
        bearer_token=BEARER_TOKEN,
        project_id=project_id,
        series_id=series_id,
        average_range=5,
        average_min_count=3,
        series_description="Dummy series",
        better_criterion="lower",
        override=True,
    )

    build_info = {
        "build_hash": "build_hash",
        "build_abbrev_hash": "build_abbrev_hash",
        "build_author_name": "build_author_name",
        "build_author_email": "build_author_email",
        "build_subject": "build_subject",
        "build_url": "build_url",
    }

    for _ in range(10):
        LOGGER.info(" + Publishing build")
        build_id = random.randint(0, 1000000)
        sample_value = random.randint(0, 100)

        add_new_optimum_build(
            session=session,
            dana_url=DANA_SPACE_URL,
            bearer_token=BEARER_TOKEN,
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

        LOGGER.info(" + Publishing sample")
        add_new_sample(
            session=session,
            dana_url=DANA_SPACE_URL,
            bearer_token=BEARER_TOKEN,
            project_id=project_id,
            series_id=series_id,
            build_id=build_id,
            sample_value=sample_value,
            override=True,
        )
