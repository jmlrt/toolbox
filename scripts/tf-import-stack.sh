#!/usr/bin/env bash

# List terraform resources in the current directory and ask their arn to import them into terraform state

RESOURCES_LIST=$(awk -F\" '/^resource "/ {print $2"."$4}' *.tf)
WORKSPACE=$(terraform workspace show)

for resource in ${RESOURCES_LIST}
do
    read -p "Enter ARN for resource ${resource} in workspace ${WORKSPACE} (type none to not import it): " arn
    if [[ ${arn} != "none" ]]
    then
        terraform import ${resource} ${arn}
    fi
done
