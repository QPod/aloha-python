#! /bin/sh
set -ex

export PREFIX=${DOCKER_PREFIX:-"docker.io/"}
export NAMESPACE="qpod"
export IMAGE="aloha-app"

export IMAGE_TAG="latest"
export IMAGE_NAME="${PREFIX}${NAMESPACE}/${IMAGE}"
