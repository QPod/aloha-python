#! /bin/sh
set -ex

SCRIPT_PWD=$(dirname "$0")
. "$SCRIPT_PWD/run_common.sh"
. "$SCRIPT_PWD/run_config.sh"

export ENVIRONMENT=$1
shift 1
echo "Run deploy job for environment ${ENVIRONMENT}"

echo '*****' | docker login --username='*****' ${PREFIX} --password-stdin
docker_pull "${IMAGE_NAME}" "${IMAGE_TAG}"

docker_compose_prepare
docker_compose_deploy "${ENVIRONMENT}"
