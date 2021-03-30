#!/bin/sh
ACTION=$1
IMAGE=$2
REGISTRY_USER=user
REGISTRY_PASSWORD=password
REGISTRY_SERVER=registry.example.com

usage() {
cat << EOF
Usage:
  $0 list_images                  : list docker images in registry
  $0 show_image_tags <image>      : show all existing tags for a specific image
EOF
}

list_images() {
  curl -k --anyauth --user ${REGISTRY_USER}:${REGISTRY_PASSWORD} https://${REGISTRY_SERVER}/v2/_catalog
}

show_image_tags() {
  if [ "${IMAGE:=none}" = "none" ]
  then
    usage
  else
    curl -k --anyauth --user ${REGISTRY_USER}:${REGISTRY_PASSWORD} https://${REGISTRY_SERVER}/v2/${IMAGE}/tags/list
  fi
}

case ${ACTION} in
  list_images)        list_images ;;
  show_image_tags)    show_image_tags ;;
  *)                  usage ;;
esac
