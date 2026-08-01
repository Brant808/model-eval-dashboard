PY := python3
DATA_DIR := data
DOCS_DIR := docs
OUT := $(DOCS_DIR)/model-eval-monitor.html

.PHONY: fetch build check test publish all clean

# fetch: run collectors for today's snapshot, then materialize data/latest.json.
# Phase 0 form: offline materialize from the newest dated snapshot (collectors
# arrive in Phase 7 and take over via collectors/run.py).
fetch:
	$(PY) -m collectors.run

build:
	$(PY) site/render.py --data $(DATA_DIR)/latest.json --out $(OUT)
	cp $(OUT) $(DOCS_DIR)/index.html

check:
	$(PY) tools/check_invariants.py

test:
	$(PY) -m pytest -q tests

# publish: gate for deploy — a fully built, linted page. The actual deploy is
# GitHub Actions (Phase 7/8); locally this just proves the artifact is shippable.
publish: build check
	@echo "publish gate OK: $(OUT) is built and invariant-clean"

all: fetch build check test

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache
