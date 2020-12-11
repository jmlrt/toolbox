.DEFAULT_GOAL := help

REPO := jmlrt
IMAGE := $(shell basename "$$PWD")

TAGGED_IMAGE=$(REPO)/$(IMAGE):$(TAG)
LATEST_IMAGE=$(REPO)/$(IMAGE):latest

.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n\nTargets:\n"} \
				/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m\t%s\n", $$1, $$2 }' \
				$(MAKEFILE_LIST) | column -s$$'\t' -t

.PHONY: docker-build
docker-build: ## Build the Docker image
	docker build -t $(IMAGE) .

.PHONY: docker-tag
docker-tag: docker-build ## Tag the Docker image
	docker tag $(IMAGE) $(TAGGED_IMAGE)
	docker tag $(IMAGE) $(LATEST_IMAGE)

.PHONY: docker-push
docker-push: docker-tag ## Push the Docker image to the registry
	docker push $(TAGGED_IMAGE)
	docker push $(LATEST_IMAGE)
