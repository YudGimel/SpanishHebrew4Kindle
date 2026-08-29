.PHONY: test sample full clean

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

sample:
	PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli build-source \
	  --translations tests/fixtures/translations.jsonl --forms tests/fixtures/forms.jsonl

full:
	PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli build-source \
	  --translations data/raw/translations.jsonl --forms data/raw/spanish_forms.jsonl

clean:
	rm -rf build data/processed
	find dist -mindepth 1 ! -name .gitkeep -delete 2>/dev/null || true
