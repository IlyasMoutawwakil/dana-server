from huggingface_hub import HfApi
import os

api = HfApi()

# update space
api.restart_space(
    repo_id="IlyasMoutawwakil/dana",
    token=os.environ.get("HF_TOKEN")
)