PROJECT_ID="ROCm-Nightly"

BENCHMARKS_REPO_URL="https://github.com/huggingface/optimum-amd" # can be optimum-subpackage or transformers
BENCHMARKS_REPO_FOLDER="optimum-amd" # can be optimum-subpackage or transformers

BUILD_REPO_URL="https://github.com/huggingface/transformers" # can be optimum-subpackage or transformers
BUILD_REPO_FOLDER="transformers" # can be optimum-subpackage or transformers

# Install build repository from source
git clone $BUILD_REPO_URL
cd $BUILD_REPO_FOLDER
pip install -e .

# get transformers build info
BUILD_ID=$(git rev-list --count HEAD)
BUILD_HASH=$(git rev-parse HEAD)
BUILD_ABBREV_HASH=$(git rev-parse --short HEAD)
BUILD_AUTHOR_NAME=$(git show -s --format='%an' HEAD)
BUILD_AUTHOR_EMAIL=$(git show -s --format='%ae' HEAD)
BUILD_SUBJECT=$(git show -s --format='%s' HEAD)
BUILD_URL=$BUILD_REPO_URL/commit/$BUILD_HASH
cd ..

# Get configs from optimum-amd
git clone $BENCHMARKS_REPO_URL
cd $BENCHMARKS_REPO_FOLDER

# Run the benchmarks
for file in benchmarks/*.yaml; do
    config=$(basename $file .yaml)

    # skip base_config
    if [ "$config" = "_base_" ]; then
        continue
    fi

    echo "Running benchmark for $config"
    optimum-benchmark --config-dir benchmarks --config-name $config --multirun
done

python scripts/publish_build.py --build-id $BUILD_ID \
                                --project-id $PROJECT_ID \
                                --build-folder experiments \
                                --build-hash $BUILD_HASH \
                                --build-abbrev-hash $BUILD_ABBREV_HASH \
                                --build-author-name $BUILD_AUTHOR_NAME \
                                --build-author-email $BUILD_AUTHOR_EMAIL \
                                --build-subject $BUILD_SUBJECT \
                                --build-url $BUILD_URL \