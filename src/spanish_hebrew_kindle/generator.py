from __future__ import annotations

from html import escape
from pathlib import Path
import shutil

from .model import Entry

OPF = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
 <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Diccionario español-hebreo abierto</dc:title>
  <dc:language>es</dc:language><dc:identifier id="uid">sh4k-open-1</dc:identifier>
  <dc:type>dictionary</dc:type>
  <x-metadata>
   <output encoding="utf-8" content-type="text/x-oeb1-document"/>
   <DictionaryInLanguage>es</DictionaryInLanguage>
   <DictionaryOutLanguage>he</DictionaryOutLanguage>
  </x-metadata>
 </metadata>
 <manifest><item id="dictionary" href="dictionary.xhtml" media-type="application/xhtml+xml"/></manifest>
 <spine><itemref idref="dictionary"/></spine>
</package>
'''

CSS = '''body{font-family:serif} .hw{font-weight:bold;font-size:1.1em}
.definition{direction:rtl;text-align:right;unicode-bidi:embed} .pos{color:#555;font-size:.85em}
'''


def _entry(number: int, entry: Entry) -> str:
    forms = "".join(f'<idx:iform value="{escape(form, quote=True)}"/>' for form in sorted(entry.forms))
    pos = ", ".join(sorted(entry.pos))
    senses = "".join(f'<div class="definition" lang="he" dir="rtl">{escape(sense)}</div>' for sense in entry.senses)
    return (f'<idx:entry name="default" scriptable="yes" spell="yes" id="e{number}">'
            f'<idx:orth value="{escape(entry.headword, quote=True)}">{forms}</idx:orth>'
            f'<div class="hw" lang="es">{escape(entry.headword)}</div>'
            + (f'<div class="pos">{escape(pos)}</div>' if pos else "") + senses + '</idx:entry>')


def generate(entries: dict[str, Entry], output: Path) -> Path:
    if output.exists():
        shutil.rmtree(output)
    (output / "OEBPS").mkdir(parents=True)
    (output / "META-INF").mkdir()
    body = "\n".join(_entry(i, entries[word]) for i, word in enumerate(sorted(entries, key=str.casefold), 1))
    xhtml = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:idx="http://www.mobipocket.com/idx">
<head><meta charset="utf-8"/><title>Diccionario español-hebreo</title><link rel="stylesheet" href="dictionary.css"/></head>
<body>{body}</body></html>'''
    (output / "mimetype").write_text("application/epub+zip", encoding="ascii")
    (output / "META-INF" / "container.xml").write_text('''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/dictionary.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''', encoding="utf-8")
    (output / "OEBPS" / "dictionary.opf").write_text(OPF, encoding="utf-8")
    (output / "OEBPS" / "dictionary.css").write_text(CSS, encoding="utf-8")
    (output / "OEBPS" / "dictionary.xhtml").write_text(xhtml, encoding="utf-8")
    return output
