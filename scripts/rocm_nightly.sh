PROJECT_ID="ROCm-Nightly"

BUILD_REPO_FOLDER="transformers"     # can be optimum-subpackage or transformers
BENCHMARKS_REPO_FOLDER="optimum-amd" # can be optimum-subpackage or transformers

# Install optimum-benchmark for rocm from source
cd optimum-benchmark
pip install -e .[peft,diffusers]
cd ..

# Install build repository from source
cd $BUILD_REPO_FOLDER
pip install -e .
# Get latest build info
BUILD_ID=$(git rev-list --count HEAD)
BUILD_HASH=$(git rev-parse HEAD)
BUILD_ABBREV_HASH=$(git rev-parse --short HEAD)
BUILD_AUTHOR_NAME=$(git show -s --format='%an' HEAD)
BUILD_AUTHOR_EMAIL=$(git show -s --format='%ae' HEAD)
BUILD_SUBJECT=$(git show -s --format='%s' HEAD)
BUILD_URL=$BUILD_REPO_URL/commit/$BUILD_HASH
cd ..

# Get configs from benchmarks repo
cd $BENCHMARKS_REPO_FOLDER
# temporary fix until we merge amd-benchmarks into optimum-amd
git checkout amd-benchmarks
# Run the benchmarks
for config_file in $BENCHMARKS_REPO_FOLDER/benchmarks/*.yaml; do
    config_name=$(basename $config_file .yaml)

    # skip base_config
    if [ "$config_name" = "_base_" ]; then
        continue
    fi

    echo "Running benchmark for $config_name"
    optimum-benchmark --config-dir $BENCHMARKS_REPO_FOLDER/benchmarks --config-name $config_name --multirun
done
cd ..

# Publish the results
python dana-client/publish_build.py --build-id "$BUILD_ID" \
    --project-id "$PROJECT_ID" \
    --build-folder "experiments" \
    --build-hash "$BUILD_HASH" \
    --build-abbrev-hash "$BUILD_ABBREV_HASH" \
    --build-author-name "$BUILD_AUTHOR_NAME" \
    --build-author-email "$BUILD_AUTHOR_EMAIL" \
    --build-subject "$BUILD_SUBJECT" \
    --build-url "$BUILD_URL"
