import os
import json
import shutil


def create_project_files(project: str):
    """
    Create project files for a new project.

    Args:
        project (str): Name of the project to create.
    """

    try:
        shutil.copytree(
            "www/views/projects/DummyProject", f"www/views/projects/{project}"
        )
    except FileExistsError:
        print("Files already exist")

    # replace "DummyProject" placeholder with project name
    for file in os.listdir(f"www/views/projects/{project}"):
        with open(f"www/views/projects/{project}/{file}", "r") as f:
            content = f.read()
        with open(f"www/views/projects/{project}/{file}", "w") as f:
            f.write(content.replace("DummyProject", project))

    # add project to projects.json
    with open("configs/db/admin/projects.json", "r") as f:
        projects = json.load(f)
        projects[project] = {
            "description": f"Benchmarks for {project}",
            "infos": "",
            "users": "",
            "useBugTracker": True,
        }

    with open("configs/db/admin/projects.json", "w") as f:
        json.dump(projects, f, indent=4)

    # add project to globalStats.json
    with open("configs/db/admin/globalStats.json", "r") as f:
        globalStats = json.load(f)
        globalStats["projects"][project] = {"numSamples": 0, "numSeries": 0}

    with open("configs/db/admin/globalStats.json", "w") as f:
        json.dump(globalStats, f, indent=4)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument(
        "--project",
        "-p",
        type=str,
        required=True,
        help="Name of the project to create.",
    )

    args = parser.parse_args()
    create_project_files(args.project)
