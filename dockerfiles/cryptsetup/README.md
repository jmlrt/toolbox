# CRYPTSETUP

This container is used to open cryptsetup container (can be used in MacOS with Docker for MacOS for example).

## Getting started

```bash
# Build the container
make docker-build

# Run the container
docker run --rm -it --privileged -v $PATH_OF_CRYPTSETUP_CONTAINER:/data.img cryptsetup bash

# Open the encrypted file
cryptsetup luksOpen /data.img datatmp
mount /dev/mapper/datatmp /mnt

# Navigate inside the encrypted container
cd /mnt
