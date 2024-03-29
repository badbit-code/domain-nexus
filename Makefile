.PHONY: help, ci-black, ci-flake8, ci-test, isort, black, docs, dev-start, dev-stop

## Ensure this is the same name as in docker-compose.yml file
CONTAINER_NAME="{{ cookiecutter.package_name }}_develop_${USER}"

PROJECT={{ cookiecutter.package_name }}

PROJ_DIR="/mnt/{{ cookiecutter.package_name }}"
VERSION_FILE:=VERSION
COMPOSE_FILE=docker/docker-compose.yml
TAG:=$(shell cat ${VERSION_FILE})

# takes advantage of the makefile structure (command; ## documentation)
# to generate help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

git-tag:  ## Tag in git, then push tag up to origin
	git tag $(TAG)
	git push origin $(TAG)


ci-black: dev-start ## Test lint compliance using black. Config in pyproject.toml file
	docker exec -t $(CONTAINER_NAME) black --check $(PROJ_DIR)


ci-flake8: dev-start ## Test lint compliance using flake8. Config in tox.ini file
	docker exec -t $(CONTAINER_NAME) flake8 $(PROJ_DIR)


ci-test: dev-start ## Runs unit tests using pytest
	docker exec -t $(CONTAINER_NAME) pytest $(PROJ_DIR)


ci-test-interactive: dev-start ## Runs unit tests with interactive IPDB session at the first failure
	docker exec -it $(CONTAINER_NAME) pytest $(PROJ_DIR)  -x --pdb --pdbcls=IPython.terminal.debugger:Pdb


ci-mypy: dev-start ## Runs mypy type checker
	docker exec -t $(CONTAINER_NAME) mypy --ignore-missing-imports --show-error-codes $(PROJ_DIR)


ci: ci-black ci-flake8 ci-test ci-mypy ## Check black, flake8, and run unit tests
	@echo "CI successful"


format: isort black ## Formats repo by running black and isort on all files
	@echo "Formatting complete"


.env: ## make an .env file
	touch .env

dev-start: .env ## Primary make command for devs, spins up containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) up -d --no-recreate


dev-stop: ## Spin down active containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) down


# Useful when Dockerfile/requirements are updated)
dev-rebuild: .env ## Rebuild images for dev containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) up -d --build


clean: ## Clean out temp/compiled python files
	find . -name __pycache__ -delete
	find . -name "*.pyc" -delete