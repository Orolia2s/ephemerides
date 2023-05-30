SHELL         := /bin/bash

YAML_ICDS     != find GPS BeiDou Galileo -name '*.yaml'
MARKDOWN      := $(YAML_ICDS:.yaml=.md)

VENV_NAME     := ephemerides
VENV_PATH     := .ephem_env
VENV_ACTIVATE := $(VENV_PATH)/bin/activate

.ONESHELL: # Keep the environment across lines

markdown: $(MARKDOWN)

run: | $(VENV_ACTIVATE)
	test -z "${VIRTUAL_ENV}" && source $|
	sudo -E $(VENV_PATH)/bin/python -m gnss_parser GPS/LNAV-L.yaml -s /dev/ttyACM0 -v

clean:
#	$(RM) -r $(VENV_PATH)
	$(RM) $(MARKDOWN)

.PHONY: markdown clean

$(MARKDOWN): %.md: %.yaml | $(VENV_ACTIVATE)
	test -z "${VIRTUAL_ENV}" && source $|
	python -m gnss_parser $< -o md > $@

$(VENV_ACTIVATE): requirements.txt
	test -d $(VENV_PATH) || python3 -m venv --prompt $(VENV_NAME) --upgrade-deps $(VENV_PATH)
	source $@
	pip install --requirement $<
