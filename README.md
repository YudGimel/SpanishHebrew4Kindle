# Spanish → Hebrew lookup dictionary for Kindle Oasis

This project builds a real indexed Kindle dictionary source from legally
redistributable Wiktionary data. A long press on an inflected Spanish word can
resolve to a concise Hebrew definition. It is not an ordinary dictionary ebook,
and the project does not claim that Send to Kindle turns its source EPUB layout
into a registered lookup dictionary.

## Status

The reproducible importer, morphology attachment, partitioned Kindle source
generator, audit report, deterministic source archive, validator, and automated
representative tests are implemented. A full release requires pinned Wiktionary
snapshots and a lawful Amazon dictionary compiler.
The repository includes no proprietary Amazon software and no copyrighted
commercial dictionary data. See [data licensing](docs/DATA-LICENSE.md) and the
[toolchain record](docs/KINDLE-TOOLCHAIN.md).

## Architecture

1. Stream the English Wiktextract JSONL export.
2. Within each individual sense, pair `es` and `he` translations. This avoids
   mechanically joining translations belonging to unrelated senses.
3. Merge duplicate Spanish headwords and Hebrew translations deterministically.
4. Stream Spanish Wiktextract records and attach source-attested inflected forms
   to matching lemmas. Romanizations, misspellings, and nonstandard forms are
   excluded.
5. Validate nonempty Hebrew definitions, duplicates, Unicode, and collisions.
6. Generate UTF-8 XHTML with `idx` lookup markup and Spanish/Hebrew OPF metadata.

Definitions carry `lang="he" dir="rtl"`; Hebrew remains in logical Unicode
order. Spanish is normalized to NFC, so accented forms such as `habló` and
`todavía` are preserved rather than accent-folded.

## Development and tests

Python 3.10 or later is sufficient; runtime code has no third-party dependency.

```console
make test
make sample
PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli validate
```

The sample is deliberately only a test fixture. It verifies `casa/casas`,
`hablar/hablo/habló/hablando`, `tener/tuvo`, `hacer/hizo`, `ser/fue`,
`mejor/mejores`, `todavía`, `aunque`, and `desarrollar`. `fue` correctly keeps
both `ser` and `ir` analyses rather than discarding a valid ambiguity.

## Full build

First make an explicitly unpinned audit download, verify its provenance and
record the printed hashes in `config/sources.json`; a release must never rely on
the moving placeholders. Then rerun without the override:

```console
python3 scripts/download_sources.py --allow-unpinned
# edit config/sources.json with snapshot dates and printed SHA-256 values
rm -rf data/raw
python3 scripts/download_sources.py
PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli build-source \
  --translations data/raw/translations.jsonl \
  --forms data/raw/spanish_forms.jsonl
PYTHONPATH=src python3 -m spanish_hebrew_kindle.cli validate
```

The build also writes `build/reports/audit.json`, including requested-word
resolutions, coverage counts, part-of-speech counts, and ambiguity counts. It
partitions large dictionaries into 5,000-entry XHTML files and creates the
deterministic compiler-input artifact
`dist/SpanishHebrew-kindle-source.zip`.

The intermediate OPF is `build/kindle-source/OEBPS/dictionary.opf`. Compile
it using the one manual command documented in
`docs/KINDLE-TOOLCHAIN.md`. The expected final artifact is
`dist/SpanishHebrew.mobi`. Until that compilation succeeds, no installable final
artifact exists.

The build prints unique headword and attached-form counts. Lookup collisions are
retained because a Spanish form can legitimately resolve to several lemmas.

## Install on a Kindle Oasis from Windows

1. Compile `dist/SpanishHebrew.mobi` and validate that KindleGen reported no
   errors.
2. Connect the unlocked Oasis to the Windows PC using a data-capable USB cable.
3. In File Explorer, open the Kindle drive and copy the MOBI into `documents`.
4. Safely eject the Kindle and wait for it to index the file.
5. On the Oasis, open **Settings → Language & Dictionaries → Dictionaries**.
6. Under Spanish, select **Diccionario español-hebreo abierto**.
7. Open an ebook whose language metadata is Spanish and long-press `casas` or
   `habló`. A book incorrectly tagged with another language will not invoke the
   Spanish dictionary.

Firmware menus can vary. If the title is visible as a book but absent from the
Spanish dictionary selector, compilation did not preserve dictionary metadata;
re-copying an ordinary EPUB will not fix that. Remove the old MOBI before
sideloading a rebuild with the same identifier. Full RTL popup rendering must be
confirmed on the target firmware.

## Limitations

* Translation coverage is limited to senses containing both Spanish and Hebrew
  translations in the selected Wiktionary export.
* Source-attested morphology gives much broader and safer coverage than a small
  hand-written conjugator, but incomplete Wiktionary paradigms remain incomplete.
* Sense pairing does not guarantee dictionary-editor quality. Multiple Hebrew
  terms are retained so users are not shown one arbitrarily selected translation.
* The build environment returned HTTP 403 for all attempted Kaikki downloads,
  so snapshot hashes and full-build statistics remain release gates rather than
  fabricated values. Run the documented commands on a network that permits the
  configured source hosts.
* Kindle compilation and popup behavior require the proprietary/manual step and
  a physical-device check described above.

## Updating

Change the two pinned snapshot URLs and SHA-256 values, delete `data/raw`, rerun
the download and build commands, review count changes and malformed records,
run `make test`, then compile and device-test a new MOBI. Preserve attribution
and CC BY-SA notices with every redistributed build.
