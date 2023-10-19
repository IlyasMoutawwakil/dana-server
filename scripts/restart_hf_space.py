from huggingface_hub import HfApi
import time
import os


api = HfApi()
HF_TOKEN = os.environ.get("HF_TOKEN")

# restart space
api.restart_space(repo_id="IlyasMoutawwakil/dana", token=HF_TOKEN)

# wait for the space to be ready
while True:
    runtime = api.get_space_runtime(repo_id="IlyasMoutawwakil/dana", token=HF_TOKEN)

    if runtime.stage in ["RUNNING"]:
        break

    elif runtime.stage in ["BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"]:
        raise RuntimeError(f"Error in the space: {runtime.stage}")

    print(f"Space is in stage {runtime.stage}, waiting for it to be ready...")
    time.sleep(5)
