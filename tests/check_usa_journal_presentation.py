"""Read-only journal contracts and display branches; not engine rendering proof."""
import argparse
import operator
from pathlib import Path
import re
from check_north_america_preflight import ROOT, definitions, fields, one, parse
from check_cmf_presentation import entries, progress_presentation
from validate_localization import parse as parse_loc

P = 'ffpa_usa_ui_'
NAME = 'ffpa_usa_journal_presentation'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmf-root', type=Path, required=True)
    parser.add_argument('--game-root', type=Path, required=True)
    args = parser.parse_args()
    guis = definitions(ROOT / f'common/scripted_guis/{NAME}.txt')
    locs = definitions(ROOT / f'common/customizable_localization/{NAME}.txt')
    values = definitions(ROOT / f'common/script_values/{NAME}.txt')
    gui = (ROOT / f'gui/{NAME}.gui').read_text()
    parse(gui)
    for folder in ('scripted_guis', 'customizable_localization', 'script_values'):
        text = (ROOT / f'common/{folder}/{NAME}.txt').read_text()
        assert not re.search(r'\b(effect|set_variable|change_variable|remove_variable|trigger_event|on_monthly_pulse)\s*=', text)
    assert 'onclick' not in gui and 'com_setup_enactment_journal' not in gui
    assert 'ROOT' not in gui and 'GetPlayer' not in gui
    for name in re.findall(r"GetScriptedGui\('([^']+)'\)", gui):
        assert name in guis
    cmf = (args.cmf_root / 'gui/com_journal_injects/enactment.gui').read_text()
    # A typo in an override silently leaves the inherited size: inspect the real base.
    blocks = set(re.findall(r'block "([^"]+)"', cmf))
    assert set(re.findall(r'blockoverride "([^"]+)"', gui)) <= blocks
    assert 'name = yellow' in (args.game_root / 'gui/textformatting.gui').read_text()
    for texture in re.findall(r'texture = "([^"]+\.dds)"', gui):
        assert (args.game_root / texture).exists() or (args.cmf_root / texture).exists(), texture
    for expression in re.findall(r'"(\[[^"\n]+\])"', gui):
        assert expression.count('(') == expression.count(')'), expression
        assert expression.count('[') == expression.count(']'), expression
    assert f'visible = "[GetScriptedGui(\'{P}usa\')' in gui

    # The metric rows must retain the original simulation predicates, including mix.
    economy = definitions(ROOT / 'common/scripted_triggers/ffpa_north_american_economy.txt')
    market = fields(economy['ffpa_usa_market_stable_v1'], 'custom_tooltip')
    industry = fields(economy['ffpa_usa_industry_stable_v1'], 'custom_tooltip')
    def without_text(block):
        return [x for k, op, v in entries(block) if k != 'text' for x in (k, op, v)]
    def canonical(block):
        return [(k, op, canonical(v) if isinstance(v, list) else v) for k, op, v in entries(block)]
    for name, source in [('population', market[0]), ('facilities', market[1]), ('categories', industry[1])]:
        assert canonical(one(guis[P + name], 'is_valid')) == canonical(without_text(source))
    for name, source, guard in [('levels', industry[0], 'ffpa_usa_industry_target_v1'),
                                ('distribution', industry[3], 'ffpa_usa_industry_route_v1')]:
        assert canonical(one(guis[P + name], 'is_valid')) == canonical(['has_variable', '=', guard] + without_text(source))
    assert canonical(one(guis[P + 'materials'], 'is_valid') + one(guis[P + 'consumer'], 'is_valid')) == canonical(without_text(industry[2]))

    comparisons = {'=': operator.eq, '>': operator.gt, '>=': operator.ge, '<': operator.lt}
    def condition(block, state):
        def value(key):
            if key.startswith('var:'):
                assert key[4:] in state, f'Unguarded missing variable: {key}'
                return state[key[4:]]
            try:
                return float(key)
            except ValueError:
                return state.get(key, key)
        for key, op, wanted in entries(block):
            if key == 'always': result = wanted == 'yes'
            elif key in ('has_variable', 'exists'): result = wanted.removeprefix('var:') in state
            elif key == 'NOT': result = not condition(wanted, state)
            elif key == 'OR': result = any(condition([k, o, v], state) for k, o, v in entries(wanted))
            elif wanted in ('yes', 'no'): result = bool(state.get(key, False)) == (wanted == 'yes')
            else: result = comparisons[op](value(key), value(wanted))
            if not result: return False
        return True
    def choose(name, state):
        for branch in fields(locs[P + name], 'text'):
            if condition(one(branch, 'trigger'), state): return one(branch, 'localization_key')
        raise AssertionError(name)
    for name in ('market', 'industry'):
        ready, stable = f'ffpa_usa_{name}_ready_v1', f'ffpa_usa_{name}_stable_v1'
        assert choose(name + '_status', {}) == P + 'blocked'
        assert choose(name + '_status', {stable: True}) == P + 'accumulating'
        assert choose(name + '_status', {stable: True, 'ffpa_usa_economy_pending_v1': 10}) == P + 'reply'
        assert choose(name + '_status', {ready: 1, 'ffpa_usa_economy_pending_v1': 11}) == P + 'settlement'
    for tag in ('USA', 'CAN', 'ZZZGEORGIA'):
        state = {'country_definition': 'cd:' + tag}
        assert condition(one(guis[P + 'usa'], 'is_valid'), state) == (tag == 'USA')
        assert choose('union_reason', state) == P + ('union_story' if tag == 'USA' else 'union_original_reason')
    assert choose('union_target', {}) == P + 'union_no_target'
    assert choose('union_target', {'ffpa_na_union_target_v1': object()}) == P + 'union_candidate'
    assert choose('union_target', {'ffpa_na_union_region_v1': object()}) == P + 'union_region'
    for state, expected in [({}, 'union_empty'), ({'ffpa_na_union_status_v1': 1}, 'union_expired'),
                            ({'ffpa_na_union_status_v1': 1, 'ffpa_na_union_deadline_v1': 1}, 'union_active'),
                            ({'ffpa_na_union_status_v1': 2}, 'settlement'),
                            ({'ffpa_na_union_status_v1': 2, 'ffpa_na_union_cooldown_v1': 1}, 'union_cooldown')]:
        assert choose('union_status', state) == P + expected
    for name in ('levels', 'distribution', 'union_progress'):
        assert not condition(one(guis[P + name], 'is_valid'), {})
    for name, metric, threshold in [('legitimacy', 'government_legitimacy', 40), ('bureaucracy', 'bureaucracy', 0)]:
        for number in (threshold - 1, threshold, threshold + 1):
            assert condition(one(guis[P + name], 'is_valid'), {metric: number}) == (number >= threshold)
    for key in ('stage', 'target', 'baseline', 'owned', 'total'):
        block = values[P + key]
        assert one(block, 'value') == '0'
        branch = one(block, 'if')
        assert one(branch, 'value') == 'var:' + one(one(branch, 'limit'), 'has_variable')
    progress = values[P + 'union_progress']
    assert one(one(progress, 'if'), 'divide') == P + 'total'
    assert one(one(progress, 'if'), 'limit') == [P + 'total', '>', '0']
    assert one(progress, 'min') == '0' and one(progress, 'max') == '1'

    # GUI value/condition/state references resolve against the live local catalog.
    catalogs = {}
    for folder in ('script_values', 'customizable_localization'):
        for file in (ROOT / 'common' / folder).glob('*.txt'):
            catalogs.update(definitions(file))
    for lang in ('english', 'simp_chinese'):
        all_loc = {}
        for file in (ROOT / 'localization' / lang).glob('*.yml'):
            all_loc.update(parse_loc(file.read_text(encoding='utf-8-sig'), lang))
        for key in re.findall(r'(?:text|tooltip) = (ffpa_[\w]+)', gui): assert key in all_loc, key
        for block in locs.values():
            for branch in fields(block, 'text'): assert one(branch, 'localization_key') in all_loc
        presentation = (ROOT / f'localization/{lang}/{NAME}_l_{lang}.yml').read_text(encoding='utf-8-sig')
        for key in re.findall(r"(?:ScriptValue|GetCustom)\('([^']+)'\)", gui + presentation):
            assert key in catalogs, key
    journals = {}
    for file in ('ffpa_north_american_journal_entries.txt', 'ffpa_north_american_economy.txt'):
        journals.update(definitions(ROOT / 'common/journal_entries' / file))
    mounts = [w for block in journals.values() for w in fields(block, 'widget') if NAME in one(w, 'gui')]
    assert len(mounts) == 4
    for w in mounts: assert one(w, 'container') == '"custom_widget_container_3"'
    for name in ('continental_market', 'industrial_scale'):
        key = f'je_ffpa_usa_{name}_v1'
        assert progress_presentation(key, journals[key]) == 'native'
    print('PASS: USA display predicates match gameplay; guarded old-save values, state priority, USA-only union view, native bars, CMF blocks/assets and bilingual references.')
    print('NOT TESTED: engine layout, GUI/localization scope evaluation, tooltip hover, scaling or save reload.')


if __name__ == '__main__':
    main()
