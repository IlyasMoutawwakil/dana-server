import os
import random
from requests import Session

from dana_constants import DANA_SPACE_URL
from dana_utils import (
    LOGGER,
    authenticate,
    add_new_build,
    add_new_series,
    add_new_sample,
)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
API_TOKEN = os.environ.get("API_TOKEN", None)
HF_TOKEN = os.environ.get("HF_TOKEN", None)

if __name__ == "__main__":
    project_id = "Dummy-Project"
    series_id = "Dummy-Series"

    session = Session()

    LOGGER.info(" + Authenticating to DANA dashboard")
    authenticate(
        session=session,
        dana_url=DANA_SPACE_URL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )

    LOGGER.info(" + Publishing series")
    add_new_series(
        session=session,
        dana_url=DANA_SPACE_URL,
        api_token=API_TOKEN,
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

        add_new_build(
            session=session,
            dana_url=DANA_SPACE_URL,
            api_token=API_TOKEN,
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
            api_token=API_TOKEN,
            project_id=project_id,
            series_id=series_id,
            build_id=build_id,
            sample_value=sample_value,
            override=True,
        )
