"""Generate the fixed-stack ideology definitions and identity compatibility copies.

Pass --game-root GAME --upstream CMF --upstream TECHRES --upstream FIREFALL.
Only exact ideology reads/adds/removes change in compatibility objects. --check
also detects source drift and stale generated files; it never updates sources.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from check_north_america_preflight import TOKEN

# Source suffix -> (target IG, target suffix, approved changes).
MAPPINGS = {
    'paternalistic': ('landowners', 'property_conservatism', {
        'law_monarchy': 'approve', 'law_presidential_republic': 'approve',
        'law_theocracy': 'neutral', 'law_oligarchy': 'strongly_approve',
        'law_autocracy': 'approve', 'law_wealth_voting': 'approve',
        'law_census_voting': 'neutral', 'law_hereditary_bureaucrats': 'neutral',
        'law_appointed_bureaucrats': 'approve', 'law_traditionalism': 'neutral',
        'law_interventionism': 'approve', 'law_laissez_faire': 'neutral',
        'law_isolationism': 'neutral', 'law_protectionism': 'approve'}),
    'hierarchic': ('landowners', 'hierarchic', {
        'law_serfdom': 'neutral', 'law_tenant_farmers': 'strongly_approve',
        'law_commercialized_agriculture': 'approve'}),
    'laissez_faire': ('industrialists', 'developmentalism', {
        'law_interventionism': 'approve', 'law_free_trade': 'strongly_approve',
        'law_protectionism': 'neutral', 'law_child_labor_allowed': 'disapprove',
        'law_restricted_child_labor': 'approve', 'law_compulsory_primary_school': 'neutral',
        'law_regulatory_bodies': 'approve', 'law_worker_protections': 'disapprove'}),
    'reactionary': ('petty_bourgeoisie', 'republican_conservatism', {
        'law_presidential_republic': 'approve', 'law_parliamentary_republic': 'approve',
        'law_monarchy': 'neutral', 'law_social_monarchy': 'neutral', 'law_theocracy': 'disapprove'}),
    'patriotic': ('petty_bourgeoisie', 'civil_patriotism', {
        'law_dedicated_police': 'strongly_approve', 'law_militarized_police': 'approve'}),
    'isolationist': ('rural_folk', 'rural_autonomy', {
        'law_isolationism': 'disapprove', 'law_protectionism': 'strongly_approve',
        'law_closed_borders': 'neutral'}),
    'moralist': ('devout', 'moralist', {'law_monarchy': 'neutral'}),
    'proletarian': ('trade_unions', 'proletarian', {'law_command_economy': 'neutral'}),
}
PREFIX = 'zzzz_ffpa_global_ig_compat'
DEFINITIONS = Path('common/ideologies/ffpa_global_ig_ideologies.txt')
REPORT = Path('docs/global-ig-compatibility.json')
CATEGORIES = {'events', *('common/' + name for name in (
    'ideologies', 'amendments', 'customizable_localization', 'decisions',
    'journal_entries', 'on_actions', 'parties', 'political_lobbies',
    'political_movements', 'scripted_effects', 'scripted_progress_bars', 'scripted_triggers'))}


def target(source):
    return 'ideology_ffpa_global_ig_' + MAPPINGS[source][1]


def tokens(text):
    return [m for m in TOKEN.finditer(text) if not m[0].isspace() and not m[0].startswith('#')]


def objects(text):
    """Top-level braced objects, retaining raw text, strings and comments."""
    ts = tokens(text.lstrip('\ufeff'))
    text = text.lstrip('\ufeff')
    i = 0
    while i < len(ts):
        if i + 2 < len(ts) and ts[i + 1][0] == '=' and ts[i + 2][0] == '{':
            start = i
            i += 3
            depth = 1
            while depth:
                assert i < len(ts), 'Unclosed source object'
                depth += (ts[i][0] == '{') - (ts[i][0] == '}')
                i += 1
            yield ts[start][0], text[ts[start].start():ts[i - 1].end()]
        else:
            i += 1


def edits(text, replacements):
    for start, end, replacement in sorted(replacements, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def adapt(text):
    """Only rewrite executable scalar commands, never comments or strings."""
    ts = tokens(text)
    changes = []
    counts = defaultdict(int)
    for a, eq, value in zip(ts, ts[1:], ts[2:]):
        command = a[0]
        if command not in ('has_ideology', 'add_ideology', 'remove_ideology') or eq[0] != '=':
            continue
        source = value[0].removeprefix('ideology:').removeprefix('ideology_')
        if source not in MAPPINGS:
            continue
        verb = command.split('_')[0]
        changes.append((a.start(), value.end(), f'ffpa_global_ig_{verb}_{source} = yes'))
        counts[command] += 1
    return edits(text, changes), dict(counts)


def source_files(roots):
    """Virtual-file shadowing and metadata replace_paths before object resolution."""
    files = {}
    labels = []
    for index, root in enumerate(roots):
        metadata = root / '.metadata/metadata.json'
        meta = json.loads(metadata.read_text()) if metadata.exists() else {}
        label = meta.get('id') or ('game' if index == 0 else root.name)
        assert label not in labels, f'Duplicate source {label}'
        labels.append(label)
        for directory in meta.get('game_custom_data', {}).get('replace_paths', []):
            files = {p: v for p, v in files.items() if not p.startswith(directory.rstrip('/') + '/')}
        for category in ('common', 'events'):
            for path in sorted((root / category).rglob('*.txt')):
                files[path.relative_to(root).as_posix()] = (index, label, path)
    return files


def helpers():
    """Small, IG-scoped identity adapters and country-scoped normalization."""
    special = {
        'paternalistic': ['ideology_ffpa_provincial_compact'],
        'laissez_faire': ['ideology_ffpa_tur_state_developmentalism',
                         'ideology_ffpa_mediterranean_developmentalism', 'ideology_neoliberism',
                         'ideology_ffpa_usa_continental_market'],
        'reactionary': ['ideology_ffpa_anatolian_civic_statism', 'ideology_ffpa_new_rome_civicism',
                        'ideology_ffpa_usa_local_constitutionalism'],
        'moralist': ['ideology_ffpa_imperial_symphonia'],
    }
    header = '# Generated by tools/generate_global_ig_compat.py. IG scope unless stated otherwise.\n\n'
    triggers, effects, normalize = header, header, ''
    for source, (ig, _, _) in MAPPINGS.items():
        old, new = 'ideology_' + source, target(source)
        triggers += f'ffpa_global_ig_has_{source} = {{\n\tOR = {{\n\t\thas_ideology = ideology:{old}\n\t\thas_ideology = ideology:{new}\n\t}}\n}}\n\n'
        effects += f'ffpa_global_ig_remove_{source} = {{\n'
        for key in (old, new):
            effects += f'\tif = {{\n\t\tlimit = {{ has_ideology = ideology:{key} }}\n\t\tremove_ideology = {key}\n\t}}\n'
        effects += '}\n\n'
        effects += f'ffpa_global_ig_add_{source} = {{\n\tif = {{\n\t\tlimit = {{ is_interest_group_type = ig_{ig} }}\n'
        effects += f'\t\tif = {{\n\t\t\tlimit = {{ has_ideology = ideology:{old} }}\n\t\t\tremove_ideology = {old}\n\t\t}}\n'
        if source in special:
            guard = '\n'.join(f'\t\t\t\t\thas_ideology = ideology:{key}' for key in special[source])
            effects += f'\t\tif = {{\n\t\t\tlimit = {{\n\t\t\t\tOR = {{\n{guard}\n\t\t\t\t}}\n\t\t\t}}\n\t\t\tffpa_global_ig_remove_{source} = yes\n\t\t}}\n\t\telse_if = {{\n'
        else:
            effects += '\t\tif = {\n'
        effects += f'\t\t\tlimit = {{ NOT = {{ has_ideology = ideology:{new} }} }}\n\t\t\tadd_ideology = {new}\n\t\t}}\n\t}}\n\telse = {{\n\t\tadd_ideology = {old}\n\t}}\n}}\n\n'
        normalize += f'\tig:ig_{ig} ?= {{\n\t\tif = {{\n\t\t\tlimit = {{ has_ideology = ideology:{old} }}\n\t\t\tffpa_global_ig_add_{source} = yes\n\t\t}}\n\t}}\n'
    effects += '# Country scope. Eight bounded mappings; no population/state/building traversal.\n'
    effects += 'ffpa_global_ig_ensure_positions_v1 = {\n' + normalize + '}\n'
    return {Path('common/scripted_triggers/ffpa_global_ig_triggers.txt'): triggers,
            Path('common/scripted_effects/ffpa_global_ig_effects.txt'): effects}


def build(roots):
    files = source_files(roots)
    database = {}
    injections = []
    special = []
    skipped = []
    for rel, (index, label, path) in sorted(files.items(), key=lambda item: (item[1][0], item[0])):
        category = str(Path(rel).parent) if rel.startswith('common/') else 'events'
        text = path.read_text(encoding='utf-8-sig')
        if rel.startswith('common/interest_groups/'):
            # Native initializers run before our startup normalization. Do not
            # replace on_enable or population/leader weights to rename identities.
            if adapt(text)[1]:
                skipped.append({'source': label, 'file': rel, 'reason': 'native IG bootstrap; no IG overrides'})
            continue
        if rel.startswith('common/history/'):
            continue
        if rel == 'common/customizable_localization/99_ru_custom_loc.txt':
            # Russian grammatical name selectors are outside the supported en/zh
            # localization contract. Copying them would add ~20,000 unrelated lines.
            skipped.append({'source': label, 'file': rel, 'reason': 'Russian-only grammatical localization'})
            continue
        if rel.startswith(('common/coat_of_arms/template_lists/', 'common/on_actions/')):
            adapted, counts = adapt(text)
            if counts:
                special.append((rel, label, text, adapted, counts))
            continue
        if category not in CATEGORIES:
            assert not adapt(text)[1], f'Unreviewed ideology consumer: {label}/{rel}'
            continue
        for key, body in objects(text):
            operation, _, plain = key.partition(':')
            if operation not in ('INJECT', 'REPLACE'):
                operation, plain = '', key
            identity = category, plain
            if operation == 'INJECT':
                injections.append((identity, label, rel, body))
                continue
            database[identity] = (label, rel, body, operation)

    # Check after resolution too: injections can precede an affected object and
    # ideology injections can change laws without any has/add/remove command.
    for identity, label, rel, body in injections:
        old = database.get(identity)
        if (identity[0] == 'common/ideologies' and identity[1].removeprefix('ideology_') in MAPPINGS
                or adapt(body)[1] or old and adapt(old[2])[1]):
            raise AssertionError(f'Needs explicit injection merge: {label}/{rel} {identity[1]}')

    outputs = helpers()
    manifest = {'sources': [], 'objects': [], 'excluded': skipped}
    for root in roots:
        meta = root / '.metadata/metadata.json'
        if meta.exists():
            d = json.loads(meta.read_text())
            manifest['sources'].append({k: d.get(k) for k in ('name', 'id', 'version')})
        else:
            settings = root.parent / 'launcher/launcher-settings.json'
            manifest['sources'].append({'name': 'Victoria 3', 'version': json.loads(settings.read_text())['version']})

    # Definitions preserve the source body except the approved scalar changes.
    ideology_text = '# Generated by tools/generate_global_ig_compat.py; do not hand-edit.\n\n'
    for source, (_, _, changes) in MAPPINGS.items():
        label, rel, body, _ = database['common/ideologies', 'ideology_' + source]
        body = re.sub(r'^(?:REPLACE:)?ideology_\w+', target(source), body, count=1)
        ts = tokens(body)
        replacements = []
        seen = set()
        for a, eq, value in zip(ts, ts[1:], ts[2:]):
            if a[0] in changes and eq[0] == '=':
                assert a[0] not in seen, (source, a[0])
                seen.add(a[0])
                replacements.append((value.start(), value.end(), changes[a[0]]))
        assert seen == changes.keys(), (source, seen, changes.keys())
        body = edits(body, replacements)
        if source == 'isolationist':
            body = body[:-1] + '\n\tlawgroup_bureaucracy = {\n\t\tlaw_elected_bureaucrats = approve\n\t\tlaw_appointed_bureaucrats = neutral\n\t\tlaw_hereditary_bureaucrats = disapprove\n\t}\n}'
        ideology_text += f'# Source: {label}/{rel} :: ideology_{source}\n{body}\n\n'
    outputs[DEFINITIONS] = ideology_text

    grouped = defaultdict(list)
    for (category, plain), (label, rel, body, operation) in sorted(database.items()):
        if category == 'common/ideologies':
            assert not adapt(body)[1], f'Unreviewed ideology condition: {label}/{rel} {plain}'
            continue
        adapted, counts = adapt(body)
        if not counts:
            continue
        assert operation != 'INJECT'
        # Existing namespaces are kept in one generated file per namespace.
        if category == 'events':
            namespace = plain.rsplit('.', 1)[0]
            out = Path('events') / f'{PREFIX}_{namespace}.txt'
            prefix = f'namespace = {namespace}\n\n'
        else:
            out = Path(category) / f'{PREFIX}.txt'
            prefix = ''
        # Same-key overrides follow the repository's existing event/JE pattern;
        # an explicit upstream REPLACE remains explicit in the final stack.
        grouped[out].append((prefix, f'# Source: {label}/{rel} :: {plain}\n{adapted}\n'))
        manifest['objects'].append({'output': str(out), 'source': label, 'file': rel,
                                    'key': plain, 'source_sha256': hashlib.sha256(body.encode()).hexdigest(),
                                    'commands': counts})
    for out, blocks in grouped.items():
        outputs[out] = '# Generated identity compatibility; only ideology commands differ from upstream.\n' + blocks[0][0] + '\n'.join(body for _, body in blocks)
    for rel, label, original, adapted, counts in special:
        # Template buckets merge; on_actions prohibit duplicate effect blocks
        # (_on_actions.md). Exact virtual paths preserve both native contracts.
        outputs[Path(rel)] = '# Generated identity compatibility; same-path file shadow.\n' + adapted
        manifest['objects'].append({'output': rel, 'source': label, 'file': rel, 'key': '(whole file)',
                                    'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
                                    'commands': counts})
    outputs[REPORT] = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    # Normalize only copied whitespace defects; parsed source equivalence is
    # checked separately, including all non-ideology content in whole files.
    for path, text in outputs.items():
        text = re.sub(r'(?m)^[ \t]+', lambda m: m[0].expandtabs(4) if ' \t' in m[0] else m[0], text)
        outputs[path] = '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
    return outputs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--game-root', type=Path, required=True)
    p.add_argument('--upstream', type=Path, action='append', default=[])
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    outputs = build([args.game_root, *args.upstream])
    tracked = {p.relative_to(ROOT) for directory in ('common', 'events') for p in (ROOT / directory).rglob(PREFIX + '*.txt')}
    if (ROOT / REPORT).exists():
        tracked.update(Path(o['output']) for o in json.loads((ROOT / REPORT).read_text())['objects'])
    stale = tracked - outputs.keys()
    assert not stale, f'Stale generated files require review: {sorted(map(str, stale))}'
    for rel, text in outputs.items():
        path = ROOT / rel
        if args.check:
            assert path.exists() and path.read_text(encoding='utf-8-sig') == text, f'Source/output drift: {rel}'
        else:
            assert not path.exists() or rel in tracked or rel in (REPORT, DEFINITIONS) or rel in helpers(), f'Refusing unrelated file: {rel}'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(f'{"CHECK" if args.check else "GENERATED"}: {len(outputs)} files, {len(json.loads(outputs[REPORT])["objects"])} compatibility objects')


if __name__ == '__main__':
    main()
