SHELL = /bin/sh

test-integration:
	pytest -s -v -m integration

test-all:
	python -m modules.pipeline prepare_symlinks examples/example_pipeline_config.yml
	pytest -s -v
