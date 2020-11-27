#!/bin/bash
#
# manage-luks-volumes - mount or unmount luks volumes

ACTION=$1 # mount / umount

shift
VOLUMES=$*

case $ACTION in
    mount)
        for volume in ${VOLUMES[*]}
        do
            printf "Mounting %s...\n" "${volume}"
            sudo cryptsetup open "$HOME/encrypted/${volume}.img" "${volume}"
            sudo mount "/dev/mapper/${volume}" "/mnt/${volume}"
        done
        ;;
    umount)
        for volume in ${VOLUMES[*]}
        do
            printf "Unmounting %s...\n" "${volume}"
            sudo umount "/mnt/${volume}"
            sudo cryptsetup close "${volume}"
        done
        ;;
    *)
        echo "Usage: $0 [mount|umount] <volume 1> [<volume 2> ...]"
esac
