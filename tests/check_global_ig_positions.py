"""Fixed-stack source and actual-script subset checks; not an engine simulation.

python3 tests/check_global_ig_positions.py --game-root GAME \
    --upstream CMF --upstream TECHRES --upstream FIREFALL
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

from check_north_america_preflight import ROOT, definitions, fields, one, parse
from check_cmf_presentation import entries

sys.path.insert(0, str(ROOT / 'tools'))
import generate_global_ig_compat as gen


def source_checks(roots):
    outputs = gen.build(roots)
    for rel, expected in outputs.items():
        assert (ROOT / rel).read_text(encoding='utf-8-sig') == expected, f'Drift: {rel}'
    manifest = json.loads(outputs[gen.REPORT])
    # A generated upstream copy must not accidentally shadow our own content.
    covered = {(str(Path(item['output']).parent), item['key']) for item in manifest['objects']
               if item['key'] != '(whole file)'}
    for category in {category for category, _ in covered}:
        for path in (ROOT / category).glob('*.txt'):
            if path.relative_to(ROOT) in outputs: continue
            for key, _ in gen.objects(path.read_text(encoding='utf-8-sig')):
                assert (category, key.removeprefix('REPLACE:')) not in covered, (path, key)
    sources = gen.source_files(roots)
    for item in manifest['objects']:
        original = sources[item['file']][2].read_text(encoding='utf-8-sig')
        actual = (ROOT / item['output']).read_text(encoding='utf-8-sig')
        if item['key'] != '(whole file)':
            original = next(body for key, body in gen.objects(original)
                            if key.removeprefix('REPLACE:') == item['key'])
            actual = next(body for key, body in gen.objects(actual)
                          if key.removeprefix('REPLACE:') == item['key'])
        assert hashlib.sha256(original.encode()).hexdigest() == item['source_sha256']
        for source in gen.MAPPINGS:
            for verb in ('has', 'add', 'remove'):
                value = ('ideology:' if verb == 'has' else '') + 'ideology_' + source
                actual = re.sub(r'\bffpa_global_ig_' + verb + '_' + source + r'\s*=\s*yes\b',
                                verb + '_ideology = ' + value, actual)
        assert parse(actual) == parse(original), f'Unrelated override change: {item["key"]}'
    sample = '# has_ideology = ideology:ideology_moralist\nx = "add_ideology = ideology_patriotic"'
    assert gen.adapt(sample) == (sample, {})

    # Read approved values independently from the design's tables, not MAPPINGS.
    spec = (ROOT / 'docs/superpowers/specs/2026-09-22-global-interest-group-positions-design.md').read_text()
    sections = [('paternalistic', '### 4.1', '### 4.2'),
                ('hierarchic', '### 4.2', '## 5.'),
                ('laissez_faire', '## 5.', '## 6.'),
                ('reactionary', '### 6.1', '### 6.2'),
                ('patriotic', '### 6.2', '## 7.'),
                ('isolationist', '## 7.', '## 8.')]
    approved = {}
    for source, start, end in sections:
        section = spec.split(start, 1)[1].split(end, 1)[0]
        approved[source] = dict(re.findall(r'\| `(law_\w+)` \| [^|]+ \| (\w+) \|', section))
        assert approved[source], source
    approved.update(moralist={'law_monarchy': 'neutral'}, proletarian={'law_command_economy': 'neutral'})
    old_definitions = {}
    for rel, (_, _, path) in sorted(sources.items(), key=lambda x: (x[1][0], x[0])):
        if rel.startswith('common/ideologies/'):
            old_definitions.update({k.removeprefix('REPLACE:'): v for k, v in definitions(path, allow_duplicates=True).items()})
    actual = definitions(ROOT / gen.DEFINITIONS)
    assert set(actual) == {gen.target(s) for s in approved}
    for source, values in approved.items():
        expected = deepcopy(old_definitions['ideology_' + source])
        if source == 'isolationist':
            expected += parse('lawgroup_bureaucracy = { law_elected_bureaucrats = approve law_appointed_bureaucrats = neutral law_hereditary_bureaucrats = disapprove }')
        seen = set()
        def patch(block):
            for i in range(len(block) - 2):
                if isinstance(block[i], str) and block[i] in values and block[i + 1] == '=':
                    seen.add(block[i]); block[i + 2] = values[block[i]]
            for child in block:
                if isinstance(child, list): patch(child)
        patch(expected)
        assert seen == values.keys(), source
        assert actual[gen.target(source)] == expected, f'Unapproved stance or metadata: {source}'
        icon = one(expected, 'icon').strip('"')
        assert any((root / icon).exists() for root in roots), icon
    for lang in ('english', 'simp_chinese'):
        path = ROOT / f'localization/{lang}/ffpa_global_ig_l_{lang}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        keys = re.findall(r'^ (\w+):', path.read_text(encoding='utf-8-sig'), re.M)
        assert len(keys) == 16 and set(keys) == {key + suffix for key in actual for suffix in ('', '_desc')}
    assert not list((ROOT / 'common/interest_groups').glob('*global*'))
    print(f'PASS: eight approved definitions, bilingual keys/icons, {len(manifest["objects"])} source-equivalent compatibility copies.')


def script_checks():
    effects = definitions(ROOT / 'common/scripted_effects/ffpa_global_ig_effects.txt')
    effects.update(definitions(ROOT / 'common/scripted_effects/ffpa_eastern_mediterranean_effects.txt'))
    effects.update(definitions(ROOT / 'common/scripted_effects/ffpa_north_american_identity.txt'))
    effects.update(definitions(ROOT / 'common/scripted_effects/zzzz_ffpa_global_ig_compat.txt'))
    triggers = definitions(ROOT / 'common/scripted_triggers/ffpa_global_ig_triggers.txt')

    # Deliberately only this feature's executed subset; unknown operations fail.
    def condition(block, country, ig=None):
        results = []
        for key, op, value in entries(block):
            assert op == '=', (key, op)
            if key in ('AND', 'OR', 'NOT'):
                children = [condition([k, o, v], country, ig) for k, o, v in entries(value)]
                result = any(children) if key == 'OR' else not all(children) if key == 'NOT' else all(children)
            elif key == 'ROOT': result = condition(value, country)
            elif key == 'has_ideology': result = value.removeprefix('ideology:') in country['igs'][ig]
            elif key == 'is_interest_group_type': result = ig == value
            elif key == 'country_definition': result = country['tag'] == value.removeprefix('cd:')
            elif key == 'has_variable': result = value in country['vars']
            elif key == 'BPM_is_active_trigger': result = value == 'no'
            elif key in triggers: result = condition(triggers[key], country, ig) == (value == 'yes')
            else: raise AssertionError(('Unsupported condition', key))
            results.append(result)
        return all(results)

    def run(block, country, ig=None):
        taken = False
        for key, op, value in entries(block):
            if key == 'limit': continue
            if key in ('if', 'else_if', 'else'):
                if key == 'if': taken = False
                if not taken and (key == 'else' or condition(one(value, 'limit'), country, ig)):
                    run(value, country, ig); taken = True
            elif key.startswith('ig:'):
                group = key.removeprefix('ig:')
                assert group in country['igs'] or op == '?=', group
                if group in country['igs']: run(value, country, group)
            elif key == 'every_interest_group':
                for group in country['igs']:
                    if not fields(value, 'limit') or condition(one(value, 'limit'), country, group):
                        run(value, country, group)
            elif key == 'add_ideology':
                country['igs'][ig].add(value); country['writes'] += 1
            elif key == 'remove_ideology':
                country['igs'][ig].discard(value); country['writes'] += 1
            elif key == 'set_variable':
                assert isinstance(value, str)
                country['vars'].add(value); country['writes'] += 1
            elif key == 'set_interest_group_name':
                country.setdefault('names', {})[ig] = value; country['writes'] += 1
            elif key in effects:
                assert value == 'yes'; run(effects[key], country, ig)
            else: raise AssertionError(('Unsupported effect', key))

    def country(tag='USA'):
        state = {'tag': tag, 'vars': {'existing_save_marker'}, 'writes': 0,
                 'igs': {f'ig_{s}': set() for s in ('landowners', 'industrialists', 'petty_bourgeoisie', 'rural_folk', 'devout', 'trade_unions', 'armed_forces', 'intelligentsia')}}
        for source, (group, _, _) in gen.MAPPINGS.items():
            state['igs']['ig_' + group].add('ideology_' + source)
        state['igs']['ig_armed_forces'] = {'ideology_jingoist', 'ideology_patriotic'}
        state['igs']['ig_intelligentsia'] = {'ideology_liberal'}
        return state

    normalize = effects['ffpa_global_ig_ensure_positions_v1']
    state = country(); run(normalize, state)
    for source, (group, _, _) in gen.MAPPINGS.items():
        assert gen.target(source) in state['igs']['ig_' + group]
        assert 'ideology_' + source not in state['igs']['ig_' + group]
    assert state['igs']['ig_armed_forces'] == {'ideology_jingoist', 'ideology_patriotic'}
    assert state['igs']['ig_intelligentsia'] == {'ideology_liberal'}
    saved = deepcopy(state); run(normalize, state); assert state == saved
    for source, (group, _, _) in gen.MAPPINGS.items():
        for initial in (set(), {'ideology_other_country'}, {gen.target(source)}, {gen.target(source), 'ideology_' + source}):
            state = country(); state['igs']['ig_' + group] = set(initial)
            run(normalize, state)
            assert state['igs']['ig_' + group] == initial - {'ideology_' + source}
            saved = deepcopy(state); run(normalize, state); assert state == saved
        state = country(); del state['igs']['ig_' + group]; run(normalize, state)
        state = country(); state['igs']['ig_intelligentsia'] = {'ideology_' + source}
        run(normalize, state)
        assert state['igs']['ig_intelligentsia'] == {'ideology_' + source}
        run(effects['ffpa_global_ig_add_' + source], state, 'ig_intelligentsia')
        assert state['igs']['ig_intelligentsia'] == {'ideology_' + source}

    # Known national and late-tech replacements always outrank default identity.
    specials = {'paternalistic': ['ideology_ffpa_provincial_compact'],
                'laissez_faire': ['ideology_ffpa_tur_state_developmentalism', 'ideology_ffpa_mediterranean_developmentalism', 'ideology_neoliberism', 'ideology_ffpa_usa_continental_market'],
                'reactionary': ['ideology_ffpa_anatolian_civic_statism', 'ideology_ffpa_new_rome_civicism', 'ideology_ffpa_usa_local_constitutionalism'],
                'moralist': ['ideology_ffpa_imperial_symphonia']}
    for source, targets in specials.items():
        for special in targets:
            state = country(); group = 'ig_' + gen.MAPPINGS[source][0]
            state['igs'][group] = {'ideology_' + source, gen.target(source), special}
            run(normalize, state); assert state['igs'][group] == {special}
            run(effects['ffpa_global_ig_add_' + source], state, group)
            assert state['igs'][group] == {special}

    packages = [('TUR', 'ffpa_apply_tur_formation_ideologies_v1', 'ffpa_tur_formation_ideologies_v1'),
                ('BYZ', 'ffpa_apply_byz_formation_ideologies_v1', 'ffpa_byz_formation_ideologies_v1'),
                ('TUR', 'ffpa_apply_tur_provincial_compact_v1', 'ffpa_tur_provincial_compact_ideology_v1'),
                ('BYZ', 'ffpa_apply_byz_imperial_symphonia_v1', 'ffpa_byz_imperial_symphonia_v1')]
    for tag, effect, old_marker in packages:
        outcomes = []
        for global_first in (False, True):
            state = country(tag); state['vars'].add(old_marker)  # old save
            if global_first: run(normalize, state)
            run(effects[effect], state); run(normalize, state)
            expected = {
                'ffpa_apply_tur_formation_ideologies_v1': ('ig_industrialists', 'ideology_ffpa_tur_state_developmentalism'),
                'ffpa_apply_byz_formation_ideologies_v1': ('ig_industrialists', 'ideology_ffpa_mediterranean_developmentalism'),
                'ffpa_apply_tur_provincial_compact_v1': ('ig_landowners', 'ideology_ffpa_provincial_compact'),
                'ffpa_apply_byz_imperial_symphonia_v1': ('ig_devout', 'ideology_ffpa_imperial_symphonia'),
            }[effect]
            assert expected[1] in state['igs'][expected[0]], effect
            assert gen.target('hierarchic') in state['igs']['ig_landowners']
            assert gen.target('patriotic') in state['igs']['ig_petty_bourgeoisie']
            assert old_marker in state['vars'] and 'existing_save_marker' in state['vars']
            assert any('global_ig_bridge' in key for key in state['vars'])
            saved = deepcopy(state); run(effects[effect], state); run(normalize, state); assert state == saved
            outcomes.append((state['igs'], state['vars']))
        assert outcomes[0] == outcomes[1], effect
        state = country('USA'); saved = deepcopy(state); run(effects[effect], state); assert state == saved

    state = country(); run(normalize, state)
    state['igs']['ig_industrialists'].add('ideology_individualist')
    run(effects['ztr_apply_late_progressist_ideologies'], state)
    assert 'ideology_neoliberism' in state['igs']['ig_industrialists']
    assert gen.target('laissez_faire') not in state['igs']['ig_industrialists']
    assert 'ideology_individualist' in state['igs']['ig_industrialists']
    saved = deepcopy(state); run(normalize, state); assert state == saved
    print('PASS: actual effect subset: bounded allocation, repeats, missing IGs/sources, national/late-tech precedence and both formation orders.')

    identity = effects['ffpa_usa_ensure_identity_v1']
    name_marker, ideology_marker = 'ffpa_usa_flavor_names_v1', 'ffpa_usa_flavor_ideologies_v1'
    expected = {
        'armed_forces': {'ideology_ffpa_usa_federal_defense', 'ideology_patriotic'},
        'industrialists': {'ideology_ffpa_usa_continental_market', 'ideology_individualist'},
        'intelligentsia': {'ideology_ffpa_usa_civic_republicanism', 'ideology_ffpa_usa_civic_liberalism', 'ideology_anti_clerical', 'ideology_anti_slavery'},
        'petty_bourgeoisie': {'ideology_ffpa_usa_local_constitutionalism', gen.target('patriotic'), 'ideology_meritocratic'},
    }
    # Old vanilla, globally normalized and late-tech saves converge; unrelated
    # ideology slots and all pre-existing save markers survive the conversion.
    outcomes = []
    for source in ('vanilla', 'global', 'late'):
        for global_first in (False, True):
            state = country()
            state['igs']['ig_industrialists'].add('ideology_individualist')
            state['igs']['ig_petty_bourgeoisie'].add('ideology_meritocratic')
            state['igs']['ig_intelligentsia'].update({'ideology_republican', 'ideology_anti_clerical', 'ideology_anti_slavery'})
            if source == 'global': run(normalize, state)
            if source == 'late':
                state['igs']['ig_industrialists'].discard('ideology_laissez_faire')
                state['igs']['ig_industrialists'].add('ideology_neoliberism')
                state['igs']['ig_intelligentsia'].discard('ideology_liberal')
                state['igs']['ig_intelligentsia'].add('ideology_liberal_modern')
            untouched = deepcopy(state['igs'])
            if global_first: run(normalize, state)
            run(identity, state); run(normalize, state)
            for group, ideologies in expected.items(): assert state['igs']['ig_' + group] == ideologies, (source, group)
            baseline = country(); baseline['igs'] = untouched; run(normalize, baseline)
            for group in ('landowners', 'rural_folk', 'devout', 'trade_unions'):
                assert state['igs']['ig_' + group] == baseline['igs']['ig_' + group]
            assert state['vars'] == {'existing_save_marker', name_marker, ideology_marker}
            assert len(state['names']) == 8 and len(set(state['names'].values())) == 8
            saved = deepcopy(state); run(identity, state); run(normalize, state); assert state == saved
            outcomes.append((state['igs'], state['names'], state['vars']))
    assert all(outcome == outcomes[0] for outcome in outcomes)

    # Native later technological changes still execute, but a national economic
    # slot is not a default laissez-faire source and must not be overwritten.
    run(effects['ztr_apply_late_progressist_ideologies'], state)
    assert 'ideology_ffpa_usa_continental_market' in state['igs']['ig_industrialists']
    assert 'ideology_neoliberism' not in state['igs']['ig_industrialists']
    assert 'ideology_neoliberal_progressist' in state['igs']['ig_industrialists']
    saved = deepcopy(state); run(identity, state); run(normalize, state); assert state == saved
    # Later events own subsequent changes; monthly recovery is not enforcement.
    state['names']['ig_devout'] = 'later_name'
    state['igs']['ig_intelligentsia'] = {'later_ideology'}
    saved = deepcopy(state); run(identity, state); assert state == saved
    state['tag'] = 'CAN'; run(identity, state); state['tag'] = 'USA'
    run(identity, state); assert state == saved

    for marker in (name_marker, ideology_marker):
        state = country(); state['vars'].add(marker)
        state['names'] = {'ig_devout': 'existing_name'}
        before = deepcopy(state); run(identity, state)
        if marker == name_marker: assert state['names'] == before['names']
        else: assert state['igs'] == before['igs']
        assert {name_marker, ideology_marker} <= state['vars']
    for group in country()['igs']:
        state = country(); del state['igs'][group]; run(identity, state)
        assert group not in state['igs'] and group not in state['names']
    for tag in ('CAN', 'TUR', 'BYZ', 'ZZZGEORGIA'):
        state = country(tag); before = deepcopy(state); run(identity, state); assert state == before
    for ideologies in (set(), {'ideology_other_country'}):
        state = country(); state['igs'] = {g: set(ideologies) for g in state['igs']}
        before = deepcopy(state['igs']); run(identity, state); assert state['igs'] == before
    hooks = definitions(ROOT / 'common/on_actions/ffpa_north_american_on_actions.txt')
    for wrapper in ('ffpa_na_on_country_formed_v1', 'ffpa_usa_charter_monthly_action_v1'):
        assert one(one(hooks[wrapper], 'effect'), 'ffpa_usa_ensure_identity_v1') == 'yes'
    print('PASS: USA known sources, eight names/five ideologies, both hook orders, partial old-save markers, foreign/missing groups, no monthly reset and late-tech coexistence.')


def existing_contracts():
    ideologies = definitions(ROOT / 'common/ideologies/ffpa_eastern_mediterranean_ideologies.txt')
    liberalism = ideologies['ideology_ffpa_rhomaic_liberalism']
    assert not fields(liberalism, 'lawgroup_citizenship')
    for group in ('policing', 'internal_security', 'free_speech', 'rights_of_women'):
        assert fields(liberalism, 'lawgroup_' + group)
    universal = ideologies['ideology_ffpa_rhomaic_civic_universalism']
    assert one(one(universal, 'lawgroup_citizenship'), 'law_multicultural') == 'strongly_approve'
    text = (ROOT / 'common/scripted_effects/ffpa_eastern_mediterranean_effects.txt').read_text()
    for operation in ('remove_ideology = ideology_liberal', 'remove_ideology = ideology_liberal_modern',
                      'add_ideology = ideology_ffpa_rhomaic_liberalism', 'set_variable = ffpa_byz_rhomaic_civic_universalism_v2'):
        assert re.search(r'^\s*' + operation + r'\s*$', text, re.M)
    for lang in ('english', 'simp_chinese'):
        assert 'ideology_ffpa_rhomaic_liberalism_desc:' in (ROOT / f'localization/{lang}/ffpa_l_{lang}.yml').read_text()
    hooks = definitions(ROOT / 'common/on_actions/ffpa_global_ig_on_actions.txt')
    for hook in ('on_game_started_after_lobby', 'on_country_formed', 'on_monthly_pulse_country'):
        assert set(k for k, _, _ in entries(hooks[hook])) == {'on_actions'}
    print('PASS: Rhomaic assertions and additive startup/formation/monthly registration.')


def usa_definition_checks(roots):
    from itertools import product
    from generate_usa_charter_rules import load_laws
    laws = load_laws([*roots, ROOT])
    files = gen.source_files([*roots, ROOT])
    database = {}
    for rel, (_, _, path) in sorted(files.items(), key=lambda item: (item[1][0], item[0])):
        category = str(Path(rel).parent)
        if category not in ('common/government_types', 'common/ideologies', 'common/scripted_effects', 'common/scripted_triggers'): continue
        for key, body in gen.objects(path.read_text(encoding='utf-8-sig')):
            assert not key.startswith('INJECT:'), (rel, key)
            database[category, key.removeprefix('REPLACE:')] = parse(body)[2]
    ideologies = definitions(ROOT / 'common/ideologies/ffpa_north_american_ideologies.txt')
    governments = definitions(ROOT / 'common/government_types/00_ffpa_american_governments.txt')
    assert len(ideologies) == 5 and len(governments) == 7
    for key, block in ideologies.items():
        assert database['common/ideologies', key] == block
        icon = one(block, 'icon').strip('"')
        assert any((root / icon).exists() for root in roots), icon
        for group, _, values in entries(block):
            if not group.startswith('lawgroup_'): continue
            for law, op, stance in entries(values):
                assert op == '=' and one(laws[law], 'group') == group, (key, group, law)
                assert stance in ('strongly_approve', 'approve', 'neutral', 'disapprove', 'strongly_disapprove')
    liberal = ideologies['ideology_ffpa_usa_civic_liberalism']
    republican = ideologies['ideology_ffpa_usa_civic_republicanism']
    assert one(liberal, 'priority') == '100'
    assert one(one(liberal, 'lawgroup_citizenship'), 'law_multicultural') == 'strongly_approve'
    assert not fields(republican, 'lawgroup_citizenship')
    for law in ('law_presidential_republic', 'law_parliamentary_republic'):
        assert one(one(republican, 'lawgroup_governance_principles'), law) == 'strongly_approve'
    assert one(one(ideologies['ideology_ffpa_usa_continental_market'], 'lawgroup_trade_policy'), 'law_free_trade') == 'strongly_approve'
    assert one(one(ideologies['ideology_ffpa_usa_local_constitutionalism'], 'lawgroup_trade_policy'), 'law_free_trade') == 'disapprove'

    # Execute actual possible blocks, using the installed native franchise
    # trigger and variant parents, rather than assuming single-party = no votes.
    franchise = database['common/scripted_triggers', 'country_has_voting_franchise']
    def has_law(active, value):
        target = value.removeprefix('law_type:')
        for law in active:
            while law:
                if law == target: return True
                parents = fields(laws[law], 'parent')
                law = parents[0].removeprefix('law_type:') if parents else None
        return False

    def possible(block, tag, active, regency=False, domain=False):
        results = []
        for key, op, value in entries(block):
            assert op == '=' or key.startswith('modifier:') and op == '>'
            if key in ('AND', 'OR', 'NOT', 'NOR'):
                children = [possible([k, o, v], tag, active, regency, domain) for k, o, v in entries(value)]
                result = {'AND': all(children), 'OR': any(children), 'NOT': not all(children), 'NOR': not any(children)}[key]
            elif key == 'country_definition': result = value == 'cd:' + tag
            elif key == 'has_law_or_variant': result = has_law(active, value)
            elif key == 'country_has_voting_franchise': result = possible(franchise, tag, active, regency, domain) == (value == 'yes')
            elif key == 'has_gov_regency': result = regency == (value == 'yes')
            elif key == 'is_domain_alliance_gov': result = domain == (value == 'yes')
            elif key == 'text': continue
            elif key == 'custom_tooltip': result = possible(value, tag, active, regency, domain)
            elif key.startswith('modifier:'):
                # Law-only fixtures: no population, event or character modifiers.
                modifier = key.removeprefix('modifier:')
                total = sum(float(v) for law in active for block in fields(laws[law], 'modifier') for v in fields(block, modifier))
                result = total > float(value)
            else: raise AssertionError(('Unsupported government condition', key))
            results.append(result)
        return all(results)

    reached = set()
    for tag, governance, power, regency, domain in product(
            ('USA', 'CAN', 'TUR', 'BYZ', 'ZZZGEORGIA'),
            ('monarchy', 'presidential_republic', 'parliamentary_republic', 'theocracy', 'council_republic', 'corporate_state', 'social_monarchy'),
            ('autocracy', 'oligarchy', 'landed_voting', 'wealth_voting', 'census_voting', 'universal_suffrage', 'single_party_state', 'technocracy', 'anarchy'),
            (False, True), (False, True)):
        active = {'law_' + governance, 'law_' + power}
        matches = [key for key, block in governments.items() if possible(one(block, 'possible'), tag, active, regency, domain)]
        assert len(matches) <= 1, (active, matches)
        if tag != 'USA' or regency or domain or governance not in ('monarchy', 'presidential_republic', 'parliamentary_republic'):
            assert not matches, (tag, active, matches)
        elif governance != 'monarchy' and power in ('technocracy', 'single_party_state'):
            assert not matches, (active, matches)
        else:
            assert len(matches) == 1, (active, matches)
            reached.update(matches)
            voting = possible(franchise, tag, active)
            expected = ('imperial_government' if power == 'autocracy' else 'constitutional_cabinet' if voting else 'imperial_cabinet') if governance == 'monarchy' else (
                ('federal_government' if voting else 'presidential_directorate') if governance == 'presidential_republic' else ('federal_cabinet' if voting else 'congressional_directorate'))
            assert matches == ['gov_ffpa_usa_' + expected]
            transfer = 'hereditary' if governance == 'monarchy' else 'dictatorial' if not voting else 'presidential_elective' if governance == 'presidential_republic' else 'parliamentary_elective'
            block = governments[matches[0]]
            assert one(block, 'transfer_of_power') == transfer
            for callback, effect in (('on_government_type_change', 'change_to_'), ('on_post_government_type_change', 'post_change_to_')):
                assert one(block, callback) == [effect + transfer, '=', 'yes']
                assert ('common/scripted_effects', effect + transfer) in database
            if voting and governance != 'monarchy':
                assert one(block, 'new_leader_on_reform_government') == ('yes' if governance == 'parliamentary_republic' else 'no')
    assert reached == governments.keys()

    effect = (ROOT / 'common/scripted_effects/ffpa_north_american_identity.txt').read_text()
    # This is the contract permitting the charter check to isolate this call.
    assert not re.search(r'\b(?:activate_law|add_modifier|trigger_event|add_journal_entry|set_ig_trait|every_\w+)\s*=', effect)
    assert set(re.findall(r'set_variable\s*=\s*(\w+)', effect)) == {'ffpa_usa_flavor_names_v1', 'ffpa_usa_flavor_ideologies_v1'}
    names = set(re.findall(r'set_interest_group_name\s*=\s*(\w+)', effect))
    required = names | {k + suffix for k in (*ideologies, *governments) for suffix in ('', '_desc')} | {'RULER_TITLE_FFPA_USA_CHAIR'}
    for lang in ('english', 'simp_chinese'):
        path = ROOT / f'localization/{lang}/ffpa_north_american_identity_l_{lang}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        keys = re.findall(r'^ (\w+):', path.read_text(encoding='utf-8-sig'), re.M)
        assert len(keys) == len(required) and set(keys) == required
        catalog = '\n'.join(p.read_text(encoding='utf-8-sig') for root in [*roots, ROOT] for p in (root / 'localization' / lang).rglob('*.yml'))
        for block in governments.values():
            for field in ('male_ruler', 'female_ruler', 'male_heir', 'female_heir'):
                for title in fields(block, field): assert re.search(r'^\s*' + title.strip('"') + r':', catalog, re.M), title
    print('PASS: USA final-stack laws/icons/titles, five definitions, 33 bilingual keys and 1,260 government combinations with native callbacks and special-government fallbacks.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, required=True)
    parser.add_argument('--upstream', type=Path, action='append', default=[])
    args = parser.parse_args()
    source_checks([args.game_root, *args.upstream])
    script_checks()
    existing_contracts()
    usa_definition_checks([args.game_root, *args.upstream])
