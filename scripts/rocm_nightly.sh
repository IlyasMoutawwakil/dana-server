# A script to run the benchmarks in $BENCHMARKS_FOLDER for the last $NUM_COMMITS
# commits in $BUILD_FOLDER and publish the results to $PROJECT_ID on DANA server.

NUM_COMMITS=10
PROJECT_ID="ROCm-Nightly"
BUILD_FOLDER="transformers"     # can be optimum-subpackage or transformers
BENCHMARKS_FOLDER="optimum-amd" # can be optimum-subpackage or transformers
BUILD_REPO="https://github.com/huggingface/transformers"

# Install some requirements
pip install -e optimum-benchmark[peft,diffusers]
pip install -r dana-client/requirements.txt

# Get the target commits from the build repository
cd $BUILD_FOLDER
TARGET_COMMITS=$(git rev-list --max-count=$NUM_COMMITS HEAD)
cd ..

# Run the benchmarks for each commit
for target_commit in $TARGET_COMMITS; do
    # Get the build's ID
    cd $BUILD_FOLDER
    BUILD_ID=$(git rev-list --count $target_commit)
    cd ..

    # Check if the build is already published
    if python dana-client/check_build.py --project-id "$PROJECT_ID" --build-id "$BUILD_ID"; then
        echo "Build $BUILD_ID already published"
        continue
    fi

    # Install the library from the target_commit
    cd $BUILD_FOLDER
    git checkout $target_commit
    pip install -e .
    # Get additional information about the build
    BUILD_HASH=$(git rev-parse $target_commit)
    BUILD_ABBREV_HASH=$(git rev-parse --short $target_commit)
    BUILD_AUTHOR_NAME=$(git show -s --format='%an' $target_commit)
    BUILD_AUTHOR_EMAIL=$(git show -s --format='%ae' $target_commit)
    BUILD_SUBJECT=$(git show -s --format='%s' $target_commit)
    BUILD_URL=$BUILD_REPO/commit/$BUILD_HASH
    cd ..

    # Run the benchmarks
    for config_file in $BENCHMARKS_FOLDER/benchmarks/*.yaml; do
        config_name=$(basename $config_file .yaml)

        # skip base_config
        if [ "$config_name" = "_base_" ]; then
            continue
        fi

        echo "Running benchmark for $config_name"
        optimum-benchmark --config-dir $BENCHMARKS_FOLDER/benchmarks --config-name $config_name --multirun
    done

    # Publish the results to DANA server (and backup dataset)
    python dana-client/publish_build.py --build-id "$BUILD_ID" \
        --project-id "$PROJECT_ID" \
        --build-folder "experiments" \
        --build-hash "$BUILD_HASH" \
        --build-abbrev-hash "$BUILD_ABBREV_HASH" \
        --build-author-name "$BUILD_AUTHOR_NAME" \
        --build-author-email "$BUILD_AUTHOR_EMAIL" \
        --build-subject "$BUILD_SUBJECT" \
        --build-url "$BUILD_URL"

    # Remove the results
    rm -rf experiments
done
