UV            ?= uv
TYPST         ?= typst
PORT          ?= /dev/ttyACM0
BAUDRATE      ?= 115200
ARGS          ?= --serial

YAML_ICDS     := $(shell find GPS BeiDou Galileo GLONASS -name '*.yaml')
MARKDOWN      := $(YAML_ICDS:.yaml=.md)
ZIG_FILE      := generated.zig
RUN           := $(UV) run icd-manager
TYPST_SOURCE  := ephemerides.typ
PDF           := $(TYPST_SOURCE:%.typ=%.pdf)

.DEFAULT_GOAL := markdown

markdown: $(MARKDOWN)

pdf: $(PDF)

zig: $(ZIG_FILE)

parse: $(YAML_ICDS)
	$(RUN) $(addprefix -I ,$^) parse $(PORT) --baudrate $(BAUDRATE) $(ARGS)

clean:
	$(RM) $(MARKDOWN) $(PDF)

full_clean: clean
	$(RM) $(ZIG_FILE)

.PHONY: markdown pdf zig parse clean full_clean

$(MARKDOWN): %.md: %.yaml
	$(RUN) --verbose --icd $< translate md > $@

$(PDF): %.pdf: %.typ
	$(TYPST) compile $< $@

$(ZIG_FILE): $(YAML_ICDS)
	$(RUN) --verbose $(addprefix -I ,$^) translate zig > $@
