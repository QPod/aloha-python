#!/bin/bash
set -xu

export NAMESPACE="docker.io"

build_image() {
    echo "$@" ;
    IMG=$1; TAG=$2; FILE=$3; shift 3; VER=$(date +%Y.%m%d.%H%M);
    docker build --squash --compress --force-rm=true -t "${IMG}:${TAG}" -f "$FILE" --build-arg "BASE_NAMESPACE=${NAMESPACE}" "$@" . ;
    docker tag "${IMG}:${TAG}" "${IMG}:${VER}" ;
}

build_image_no_tag() {
    echo "$@" ;
    IMG=$1; TAG=$2; FILE=$3; shift 3;
    docker build --squash --compress --force-rm=true -t "${IMG}:${TAG}" -f "$FILE" --build-arg "BASE_NAMESPACE=${NAMESPACE}" "$@" . ;
}

build_image_common() {
    echo "$@" ;
    IMG=$1; TAG=$2; FILE=$3; shift 3; VER=$(date +%Y.%m%d.%H%M);
    docker build --compress --force-rm=true -t "${IMG}:${TAG}" -f "$FILE" --build-arg "BASE_NAMESPACE=${NAMESPACE}" "$@" . ;
    docker tag "${IMG}:${TAG}" "${IMG}:${VER}" ;
}

alias_image() {
    IMG_1=$1; TAG_1=$2; IMG_2=$3; TAG_2=$4; shift 4; VER=$(date +%Y.%m%d.%H%M);
    docker tag "${IMG_1}:${TAG_1}" "${IMG_2}:${TAG_2}" ;
    docker tag "${IMG_2}:${TAG_2}" "${IMG_2}:${VER}" ;
}

push_image() {
    KEYWORD="${1:-second}";
    docker image prune --force && docker images | sort;
    IMAGES=$(docker images | grep "${KEYWORD}" | awk '{print $1 ":" $2}') ;
    echo "$DOCKER_REGISTRY_PASSWORD" | docker login "${REGISTRY_URL}" -u "$DOCKER_REGISTRY_USER" --password-stdin ;
    for IMG in $(echo "${IMAGES}" | tr " " "\n") ;
    do
      docker push "${IMG}";
      status=$?;
      echo "[${status}] Image pushed > ${IMG}";
    done
}

clear_images() {
    KEYWORD=${1:-'days ago\|weeks ago\|months ago\|years ago'}; # if no keyword is provided, clear all images build days ago
    IMGS_1=$(docker images | grep "${KEYWORD}" | awk '{print $1 ":" $2}') ;
    IMGS_2=$(docker images | grep "${KEYWORD}" | awk '{print $3}') ;

    for IMG in $(echo "$IMGS_1 $IMGS_2" | tr " " "\n") ; do
      docker rmi "${IMG}" || true; status=$?; echo "[${status}] image removed > ${IMG}";
    done
    docker image prune --force && docker images ;
}


remove_folder() {
    sudo du -h -d1 "$1" || true ;
    sudo rm -rf "$1" || true ;
}

free_diskspace() {
    remove_folder /usr/share/dotnet
    remove_folder /usr/local/lib/android
    # remove_folder /var/lib/docker
    df -h
}
