SHELL         := /bin/bash

YAML_ICDS     != find GPS BeiDou Galileo GLONASS -name '*.yaml'
MARKDOWN      := $(YAML_ICDS:.yaml=.md)

VENV_NAME     := ephemerides
VENV_PATH     := .ephem_env
VENV_ACTIVATE := $(VENV_PATH)/bin/activate

ZIG_FOLDER    := generated/zig/src
ZIG_FILE      := $(ZIG_FOLDER)/main.zig

.ONESHELL: # Keep the environment across lines

markdown: $(MARKDOWN)

run: $(YAML_ICDS) | $(VENV_ACTIVATE)
	test -z "${VIRTUAL_ENV}" && source $|
	sudo -E $(VENV_PATH)/bin/python -m gnss_parser --verbose $(addprefix -I ,$^) parse /dev/ttyACM0 --serial

test: $(YAML_ICDS) | $(VENV_ACTIVATE)
	@test -z "${VIRTUAL_ENV}" && source $|
	@$(VENV_PATH)/bin/python -m gnss_parser -v $(addprefix -I ,$^) parse test/two.ubx --dump

zig: $(ZIG_FILE)

clean:
	$(RM) $(MARKDOWN) $(ZIG_FILE)

full_clean: clean
	$(RM) -r $(VENV_PATH)

.PHONY: markdown clean run full_clean test

$(MARKDOWN): %.md: %.yaml | $(VENV_ACTIVATE)
	test -z "${VIRTUAL_ENV}" && source $|
	python -m gnss_parser --verbose --icd $< translate md > $@

$(VENV_ACTIVATE): requirements.txt
	test -d $(VENV_PATH) || python3 -m venv --prompt $(VENV_NAME) --upgrade-deps $(VENV_PATH)
	source $@
	pip install --requirement $<

$(ZIG_FOLDER):
	mkdir -p $@

.SECONDEXPANSION:

$(ZIG_FILE): $(YAML_ICDS) | $(VENV_ACTIVATE) $$(@D)
	test -z "${VIRTUAL_ENV}" && source $|
	python -m gnss_parser --verbose $(addprefix -I ,$^) translate zig > $@
