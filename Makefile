# Reference Sites:
# https://www.dinotools.de/en/2019/12/23/use-python-with-virtualenv-in-makefiles/
# https://earthly.dev/blog/python-makefile/
# https://ljvmiranda921.github.io/notebook/2021/05/12/how-to-manage-python-envs/

# Misc
.DEFAULT_GOAL = help
VENV_NAME?=venv
PYTHON=${VENV_NAME}/bin/python

## ———————————————— General RSYNC Backup 🖖 ————————————————
## Activate Virtual Environment: . ./venv/bin/activate
## Deactivate Virtual Environment: deactivate
## —————————————————————————————————————————————————————————

help: ## Outputs this help screen.
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

build: ## Automatically downloads all build dependencies.
	pip install --upgrade build

setup: build ## This will setup the project using PIP installing all requirements.
	python -m build
	pip install -e .

pip-compile: ## This compiles a new requirements.txt file using pip-tools (pip-compile).
	pip-compile

freeze: ## Gives an output of all the installed packages and there versions.
	pip freeze

venv-setup: ## Creates the VENV when the project is freshly checked out from source control.
	python3 -m venv ${VENV_NAME}

venv-upgrade-pip: # This upgrades the version of PIP installed in the VENV.
	pip install --upgrade pip

venv-update: ## Updates the VENV with a new Python version.
	mv venv/ venv_old/
	python3 -m venv venv/

test: ## Run UNIT and Functional Tests with PyTest.
	pytest tests --cov -s

lint: ## Run a code style linter (flake8) over the app code.
	flake8 src/

clean:
	find . -name '.coverage' -delete
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '.pytest_cache' -type d | xargs rm -rf
	find . -name '__pycache__' -type d | xargs rm -rf
	find . -name '.ipynb_checkpoints' -type d | xargs rm -rf
