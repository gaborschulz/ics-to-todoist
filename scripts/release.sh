#!/bin/zsh

start=$(date +%s)
VERSION_BUMPED=0

RED="\033[1;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
PURPLE="\033[1;35m"
CYAN="\033[1;36m"
WHITE="\033[1;37m"
RESET="\033[0m"

QUESTION_FLAG="${GREEN}?"
WARNING_FLAG="${YELLOW}!"
NOTICE_FLAG="${CYAN}❯"

load_env() {
    if [ -f .env ]; then
        echo "Loading .env file"
        export $(cat .env | xargs)
    fi

    echo "Project: $PROJECT_NAME"
}

run_test() {
    pytest -s && \
    coverage-badge -o coverage.svg -f
}

cleanup() {
    find . -type d -name "@eaDir" -print0 | xargs -0 rm -rf
}

bump_version() {
    echo "Argument: $1 / $#"
    if [[ "$#" -eq 0 ]]; then
        echo "No version bump"
        NEW_VERSION=$(cat VERSION) && \
        echo "New version: $NEW_VERSION" && \
        return 0
    fi

    bump2version $1 && \

    NEW_VERSION=$(cat VERSION) && \
    echo "New version: $NEW_VERSION" && \
    git push --tags -u origin $(git branch --show-current) && \
    gh release create v$NEW_VERSION --generate-notes
}

push() {
    git push && \
    git push origin v$(poetry version --short)
}

release_to_pypi() {
    if [[ $VERSION_BUMPED == 0 ]]; then
        echo "No PyPI release without version bump"
    fi

    pdm publish
    gh release create v$(poetry version --short) --generate-notes
}

load_env &&
cleanup &&
run_test &&
bump_version $1 &&
push &&
release_to_pypi

end=$(date +%s)
runtime=$((end - start))

echo "Elapsed time: $runtime s"
