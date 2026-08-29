.PHONY: test sample clean

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

sample:
	PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli build-source \
	  --translations tests/fixtures/translations.jsonl --forms tests/fixtures/forms.jsonl

clean:
	rm -rf build dist data/processed
