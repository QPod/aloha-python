#! /bin/sh
set -ex

docker_build() {
  IMAGE_NAME=$1
  IMAGE_TAG=$2
  DOCKERFILE=$3
  shift 3
  IMAGE_TAG=${IMAGE_TAG:-"latest"}
  TIMESTAMP=$(date +'%Y-%m%d-%H%M')
  DOCKERFILE=${DOCKERFILE:-"Dockerfile"}

  # build the docker image and tag as timestamp
  docker build --rm -t "${IMAGE_NAME}:${IMAGE_TAG}" -f "${DOCKERFILE}" .
  docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_NAME}:${TIMESTAMP}"
  docker images | grep "${IMAGE_NAME}"
}

docker_push() {
  IMAGE_NAME=$1
  shift 1
  echo "Pushing docker image: ${IMAGE_NAME}"
  while
    timeout -k 605s 600s bash -c "docker push ${IMAGE_NAME}"
    [ $? = 124 ]
  do
    ehco "Timeout pushing docker image, retrying..."
    sleep 2
  done
}

docker_destroy() {
  CONTAINER_NAME=$1
  shift 1
  (docker stop "${CONTAINER_NAME}") || true
  (docker rm "${CONTAINER_NAME}") || true
}

docker_pull() {
  IMAGE_NAME=$1
  IMAGE_TAG=$2
  shift 2
  IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
  TIMESTAMP=$(date +'%Y-%m%d-%H%M')

  docker tag "${IMAGE}" "${IMAGE_NAME}:bak-${TIMESTAMP}" || true
  docker rmi "${IMAGE}" || true

  echo "Pulling new docker image: ${IMAGE}"
  while
    timeout -k 185s 180s bash -c "docker pull ${IMAGE_NAME}"
    [ $? = 124 ]
  do
    echo "Timeout pulling docker image, retrying..."
    sleep 2
  done

  docker images | grep "${IMAGE_NAME}"
}

docker_compose_prepare() {
  python3 -m pip install -Uq \
    docker-compose pip

  alias docker-compose='python3 -m compose '
  docker-compose version
}

docker_compose_deploy() {
  ENVIRONMENT=$1
  shift
  echo "Deploy containers for environment ${ENVIRONMENT}"
  rm -rf ./config ./*.yml || true
  /bin/cp -r ./deploy/profile_${ENVIRONMENT}/* ./

  if [ -f "traefik-docker-compose.yml" ]; then
    echo "Found traefik docker-compose file, restarting svc-traefik..."
    (docker-compose -f traefik-docker-compose.yml down --remove-orphans || true) && docker-compose -f traefik-docker-compose.yml up -d
  else
    echo "Ignore traefik svc since no `traefik-docker-compose.yml` file found..."
  fi
  (docker-compose down || true) && docker-compose up -d

  docker ps -a

  echo "Removing old docker images..."
  docker images | grep 'days ago\|weeks ago\|months ago\|years ago' | awk '{print $1":"$2}' | xargs docker rmi || true
}
