# Kindle dictionary toolchain status

Kindle lookup dictionaries are not ordinary ebooks. Their source contains
`idx:entry`, `idx:orth`, and `idx:iform` indexes and OPF
`DictionaryInLanguage`/`DictionaryOutLanguage` metadata. Merely uploading an
EPUB through Send to Kindle does not promise preservation or registration of
those indexes.

The generator emits legacy OEB/Kindle dictionary source using the Mobipocket
`idx` namespace, Spanish input metadata (`es`), and Hebrew output metadata
(`he`). This is the source form historically accepted by Amazon KindleGen.

As of this repository's initial environment audit (2026-08-29), KindleGen,
Kindle Previewer, Calibre, and EPUBCheck were not installed. Amazon has retired
public KindleGen distribution, and current Kindle Previewer workflows do not
provide a documented, automatable way here to export a sideloadable personal
lookup dictionary. Calibre can create ebook containers, but that alone is not
proof that Oasis dictionary indexes survive. Therefore this repository does
**not** rename an EPUB to `.mobi` or call its source output installable.

## Remaining manual compilation step

On a machine where a lawfully obtained KindleGen installation already exists:

```console
kindlegen build/kindle-source/OEBPS/dictionary.opf -c2 -o SpanishHebrew.mobi
mkdir -p dist
mv build/kindle-source/OEBPS/SpanishHebrew.mobi dist/SpanishHebrew.mobi
```

Then inspect the log for errors and test the resulting file on a Kindle Oasis.
Do not download KindleGen from an unofficial mirror and do not redistribute its
binary. The generated directory under `build/kindle-source` is complete even
when the proprietary compilation step cannot run.

Physical-device validation remains essential: XML validation proves source
structure, but only an Oasis test proves popup registration and firmware RTL
rendering.
