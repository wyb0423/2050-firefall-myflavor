"""Run with python3 tests/validate_localization.py [--game-root GAME --upstream MOD ...].

Checks the project's single-line localization format, rich text, bilingual keys,
and scope-independent concept links. This does not test the in-game layout.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r' ([\w.-]+):\d* "((?:[^"\\]|\\[n"\\])*)"')
TAG = re.compile(r'#!|#([A-Za-z_]+) ')
STYLES = {'bold', 'b', 'v', 'p', 'n', 'r', 'italic', 'lore'}
CONCEPT = re.compile(r'\[(concept_[\w-]+)\]|\[Concept\(\'(concept_[\w-]+)\',')


def parse(text, language):
    lines = text.splitlines()
    assert lines[0] == f'l_{language}:', 'Invalid language header'
    entries = {}
    for number, line in enumerate(lines[1:], 2):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = ROW.fullmatch(line)
        assert match, f'Line {number}: malformed entry, quote or escape'
        key, value = match.groups()
        assert key not in entries, f'Duplicate key: {key}'
        depth = 0
        for tag in TAG.finditer(value):
            if tag[0] == '#!':
                depth -= 1
                assert depth >= 0, f'{key}: unmatched closing tag'
            else:
                assert tag[1] in STYLES, f'{key}: unverified style {tag[1]}'
                depth += 1
        assert depth == 0, f'{key}: unclosed rich-text tag'
        assert '#' not in TAG.sub('', value), f'{key}: malformed rich-text tag'
        assert value.count('[') == value.count(']'), f'{key}: unbalanced reference'
        assert value.count('$') % 2 == 0, f'{key}: unbalanced localization reference'
        assert r'\\n' not in value, f'{key}: double-escaped line break'
        entries[key] = value
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path)
    parser.add_argument('--upstream', type=Path, action='append', default=[])
    args = parser.parse_args()
    json.loads((ROOT / '.metadata/metadata.json').read_text(encoding='utf-8-sig'))
    # Ensure the check actually rejects the editing errors it is meant to catch.
    for bad in [' x: "#bold open"', ' x: "close#!"', ' x: "bad "quote""',
                ' x: "line\nbreak"', r' x: "bad\q"', r' x: "literal\\n"']:
        try:
            parse('l_english:\n' + bad, 'english')
        except AssertionError:
            pass
        else:
            raise AssertionError(f'Invalid sample was accepted: {bad}')
    catalogs = {}
    for language in ['english', 'simp_chinese']:
        catalogs[language] = {}
        for path in sorted((ROOT / 'localization' / language).glob('*.yml')):
            raw = path.read_bytes()
            assert raw.startswith(b'\xef\xbb\xbf'), f'{path}: missing UTF-8 BOM'
            entries = parse(raw.decode('utf-8-sig'), language)
            assert not catalogs[language].keys() & entries.keys(), f'{path}: duplicate across files'
            catalogs[language].update(entries)
            other_language = 'simp_chinese' if language == 'english' else 'english'
            counterpart = ROOT / 'localization' / other_language / path.name.replace(language, other_language)
            other = parse(counterpart.read_text(encoding='utf-8-sig'), other_language)
            assert entries.keys() == other.keys(), f'{path}: bilingual key mismatch'
    for language, entries in catalogs.items():
        for key, value in entries.items():
            for reference in re.findall(r'\$(ffpa_[\w.-]+|je_ffpa_[\w.-]+)\$', value):
                assert reference in entries, f'{key}: unresolved local reference {reference}'
    if args.game_root:
        concepts = set()
        for source in [args.game_root, *args.upstream]:
            assert (source / 'common').is_dir(), f'Missing game/mod root: {source}'
            for path in (source / 'common/game_concepts').glob('*.txt'):
                concepts.update(re.findall(r'^\s*(concept_[\w-]+)\s*=\s*\{', path.read_text(encoding='utf-8-sig'), re.M))
        for entries in catalogs.values():
            for key, value in entries.items():
                for pair in CONCEPT.findall(value):
                    reference = pair[0] or pair[1]
                    assert reference in concepts, f'{key}: unknown concept {reference}'
    print(f'PASS: all localization files, {len(catalogs["english"])} keys per language; encoding, syntax, tags and references')


if __name__ == '__main__':
    main()
