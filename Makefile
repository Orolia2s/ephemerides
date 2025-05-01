UV            ?= uv
TYPST         ?= typst

YAML_ICDS     := $(shell find GPS BeiDou Galileo GLONASS -name '*.yaml')
MARKDOWN      := $(YAML_ICDS:.yaml=.md)
ZIG_FILE      := generated.zig
RUN           := $(UV) run icd-manager
TYPST_SOURCE  := ephemerides.typ
PDF           := $(TYPST_SOURCE:%.typ=%.pdf)

markdown: $(MARKDOWN)

pdf: $(PDF)

zig: $(ZIG_FILE)

clean:
	$(RM) $(MARKDOWN) $(PDF)

full_clean: clean
	$(RM) $(ZIG_FILE)

.PHONY: markdown pdf zig clean full_clean

$(MARKDOWN): %.md: %.yaml
	$(RUN) --verbose --icd $< translate md > $@

$(PDF): %.pdf: %.typ
	$(TYPST) compile $< $@

$(ZIG_FILE): $(YAML_ICDS)
	$(RUN) --verbose $(addprefix -I ,$^) translate zig > $@
