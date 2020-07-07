DOCKER_FILE := debian.dockerfile
DOCKER_IMAGE := jmlrt/debian-tools
DOCKER_TAG := 0.1
WORK_DIR := $(shell pwd)

.PHONY: docker-build
docker-build:
	sudo docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f $(DOCKER_FILE) .

.PHONY: docker-run
docker-run:
	sudo docker run -it -v $(WORK_DIR):/data -w /data $(DOCKER_IMAGE):$(DOCKER_TAG) bash

.PHONY: docker-push
docker-push: docker-build
	sudo docker push $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-push-latest
docker-push-latest: docker-push
	sudo docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest
	sudo docker push $(DOCKER_IMAGE):latest