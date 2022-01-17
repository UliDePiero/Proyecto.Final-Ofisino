build:
	docker build . --tag ofisino_backend:latest

ci: build test
	@echo "✅  CI Passed"

run:
	docker run -it --rm -p 8000:8000 ofisino_backend

shell:
	docker run -it --rm -p 8000:8000 ofisino_backend /bin/bash

CONTAINERS = $(shell docker ps --all --quiet)
fixusedport:
	# used when port is allocated
	docker stop $(CONTAINERS)

.PHONY: build test run shell fixusedport
