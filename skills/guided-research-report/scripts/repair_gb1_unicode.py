#!/usr/bin/env python3
"""Attach an installed Adobe-GB1-UCS2 CMap to unmapped GB1 Identity-H fonts.

Requires pypdf. Not OCR; only the explicit Adobe GB1 CID encoding is supported.
Supply a legitimate installed CMap; its copyright/license stays in the stream.
Never modifies the input or existing ToUnicode maps. Inspect render and extraction.
"""
import argparse
from pathlib import Path
import re


def main():
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, NameObject
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--cmap', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    data = a.cmap.read_bytes()
    if b'/CMapName /Adobe-GB1-UCS2' not in data or b'beginbfrange' not in data:
        p.error('Expected Adobe-GB1-UCS2 CMap with Unicode ranges')
    supplement = re.search(rb'/Supplement\s+(\d+)\s+def', data)
    if not supplement:
        p.error('CMap supplement missing')
    w = PdfWriter()
    w.clone_document_from_reader(PdfReader(a.input))
    seen, patched = set(), 0

    def visit(resources):
        nonlocal patched
        if not resources:
            return
        resources = resources.get_object()
        for ref in resources.get('/Font', {}).values():
            font = ref.get_object()
            if id(font) in seen:
                continue
            seen.add(id(font))
            if '/ToUnicode' in font or font.get('/Encoding') != '/Identity-H':
                continue
            descendants = font.get('/DescendantFonts', [])
            if not descendants:
                continue
            info = descendants[0].get_object().get('/CIDSystemInfo', {})
            if str(info.get('/Registry')) != 'Adobe' or str(info.get('/Ordering')) != 'GB1':
                continue
            if int(info.get('/Supplement', 0)) > int(supplement[1]):
                raise ValueError('Font supplement exceeds supplied CMap coverage')
            stream = DecodedStreamObject(); stream.set_data(data)
            font[NameObject('/ToUnicode')] = w._add_object(stream)
            patched += 1
        for ref in resources.get('/XObject', {}).values():
            obj = ref.get_object()
            if id(obj) in seen:
                continue
            seen.add(id(obj)); visit(obj.get('/Resources'))

    for page in w.pages:
        visit(page.get('/Resources'))
    if not patched:
        p.error('No eligible missing GB1 mappings; no output written')
    with a.output.open('xb') as out:
        w.write(out)
    print(f'Patched {patched} font mappings; verify extraction and rendered pages: {a.output}')


if __name__ == '__main__':
    main()
