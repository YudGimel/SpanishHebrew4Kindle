# Data provenance and redistribution

## Selected source

The production pipeline is designed for the **English Wiktionary** and
**Spanish Wiktionary** JSONL exports produced by
[Wiktextract/Kaikki](https://kaikki.org/). English entries supply Spanish and
Hebrew translations paired within the same source sense. Spanish entries supply
attested forms of those Spanish lemmas. The small files in `tests/fixtures` are
hand-written test inputs and are not the distributable dictionary.

Wiktionary page text is offered under the Creative Commons
Attribution-ShareAlike license and the GNU Free Documentation License. A
distributed lexical database or dictionary derived from it must carry the
required attribution, source revision information, and applicable license; this
project elects **CC BY-SA 4.0** for derived lexical output. The MIT license in
the repository covers the software only and does not relicense lexical data.

Before publishing a full build, replace both placeholder snapshot and checksum
values in `config/sources.json`. Retain a copy of the download manifest and the
Wiktionary attribution/link in the release. The configured URLs are convenience
exports, not a new commercial dictionary source. Kaikki/Wiktextract should also
be credited as the extraction software. No commercial dictionary may be added.

## Restrictions and attribution checklist

* Preserve attribution to the relevant Wiktionary projects and contributors.
* Link to or include the CC BY-SA 4.0 license with redistributed derived data.
* State that the output was modified, including normalization, sense pairing,
  merging, and inflection indexing.
* Distribute adapted lexical content under the same or a compatible license.
* Pin the source date and SHA-256; an unpinned live export is development-only.
* Do not imply endorsement by Wikimedia, Kaikki, or Amazon.

This document is an engineering compliance record, not legal advice.
