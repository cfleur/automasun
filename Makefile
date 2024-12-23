SHELL = /bin/sh

test-integration:
	export PIPELINE_CONFIG_FILE=examples/example_pipeline_config.yml
	pytest -s -v -m integration

test-all: test-integration
	python -m modules.pipeline prepare_symlinks examples/example_pipeline_config.yml
	pytest -s -v
