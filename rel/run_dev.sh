#! /bin/sh
set -ex

docker-compose -f rel/deploy/profile_DEV/docker-compose.yml down || true
docker-compose -f rel/deploy/profile_DEV/docker-compose.yml up --build -d

docker-compose -f rel/deploy/profile_DEV/traefik-docker-compose.yml down || true
docker-compose -f rel/deploy/profile_DEV/traefik-docker-compose.yml up -d
