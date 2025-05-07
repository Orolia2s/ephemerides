UV            ?= uv
TYPST         ?= typst
PORT          ?= /dev/ttyACM0
BAUDRATE      ?= 115200
ARGS          ?= --serial

YAML_ICDS     := $(shell find GPS BeiDou Galileo GLONASS -name '*.yaml')
MARKDOWN      := $(YAML_ICDS:.yaml=.md)
ZIG_FILE      := zig/generated.zig
RUN           := $(UV) run icd-manager
TYPST_SOURCE  := ephemerides.typ
PDF           := $(TYPST_SOURCE:%.typ=%.pdf)
SOURCES       := $(shell find src -type f -name '*.py')
EXECUTABLE    := zig/zig-out/bin/ephemerides

.DEFAULT_GOAL := markdown

markdown: $(MARKDOWN)

pdf: $(PDF)

zig: $(EXECUTABLE)

parse: $(YAML_ICDS)
	$(RUN) $(addprefix -I ,$^) parse $(PORT) --baudrate $(BAUDRATE) $(ARGS)

clean:
	$(RM) $(MARKDOWN) $(PDF) $(ZIG_FILE)

.PHONY: markdown pdf zig parse clean

$(MARKDOWN): %.md: %.yaml $(SOURCES)
	$(RUN) --verbose --icd $< translate md > $@

$(PDF): %.pdf: %.typ
	$(TYPST) compile $< $@

$(ZIG_FILE): $(YAML_ICDS) $(SOURCES)
	$(RUN) --verbose $(addprefix -I ,$(YAML_ICDS)) translate zig | zig fmt --stdin > $@

$(EXECUTABLE): $(ZIG_FILE)
	( cd zig && zig build )
