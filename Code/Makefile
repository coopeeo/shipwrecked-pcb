MPY_CROSS ?= mpy-cross
MPREMOTE ?= mpremote
BUILD_DIR := build
PORT ?= auto

PY_FILES := $(shell find . -path ./$(BUILD_DIR) -prune -o -type f -name "*.py" ! -path "./main.py" -print)
MPY_FILES := $(patsubst ./%, $(BUILD_DIR)/%, $(PY_FILES:.py=.mpy))
OTHER_FILES := $(shell find . -path ./$(BUILD_DIR) -prune -o -type f ! -name "*.py" ! -name "*.mpy" -print)
COPY_FILES := $(patsubst ./%, $(BUILD_DIR)/%, $(OTHER_FILES))

.PHONY: all clean upload run

all: $(MPY_FILES) $(COPY_FILES)

$(BUILD_DIR)/%.mpy: %.py
	@echo "Compiling $<"
	@mkdir -p $(dir $@)
	@$(MPY_CROSS) -march=armv6m $< -o $@
	@touch $@

$(BUILD_DIR)/%: %
	@echo "Copying $< -> $@"
	@mkdir -p $(dir $@)
	@cp $< $@

clean:
	@echo "Cleaning build directory and .pyc files..."
	@rm -rf $(BUILD_DIR)
	@find . -path ./$(BUILD_DIR) -prune -o -name "*.pyc" -exec rm {} \;

upload: all
	cp ./main.py $(BUILD_DIR)/main.py
	cd $(BUILD_DIR) && $(MPREMOTE) connect $(PORT) cp -r . :/

run: upload
	$(MPREMOTE) connect $(PORT) run main.py
