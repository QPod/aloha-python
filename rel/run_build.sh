#! /bin/sh
set -ex

SCRIPT_PWD=$(dirname "$0")
. "${SCRIPT_PWD}/run_common.sh"
. "${SCRIPT_PWD}/run_config.sh"

docker_build "${IMAGE_NAME}" "${IMAGE_TAG}" tool/Dockerfile
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE}"

docker_push "${IMAGE_NAME}"
