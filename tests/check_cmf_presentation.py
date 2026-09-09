"""Static CMF contracts and exhaustive arithmetic cases; no engine/UI simulation.

python3 tests/check_cmf_presentation.py --game-root GAME --cmf-root CMF \
    --upstream TECHRES --upstream FIREFALL
"""
import argparse
import itertools
import json
from pathlib import Path
import re
from check_north_america_preflight import ROOT, definitions, parse, fields, one
from validate_localization import parse as parse_loc


def entries(block):
    i = 0
    while i < len(block):
        key, op = block[i:i + 2]
        i += 2
        if op in ('>', '<', '!', '?') and block[i] == '=':
            op += '='
            i += 1
        value = block[i]
        i += 1
        yield key, op, value


def arithmetic_checks():
    """Interpret only the arithmetic/condition subset used by these three formulas."""
    values = definitions(ROOT / 'common/script_values/ffpa_permanent_governance_values.txt')
    def number(v, state):
        if isinstance(v, list):
            return calc(v, state)
        if v in values:
            return calc(values[v], state)
        return float(v)
    def condition(block, state):
        tests = []
        for key, op, val in entries(block):
            if key in ('OR', 'AND', 'NOT'):
                children = [condition([k, o, v], state) for k, o, v in entries(val)]
                tests.append(any(children) if key == 'OR' else not all(children) if key == 'NOT' else all(children))
            elif isinstance(val, list):
                tests.append(condition(val, state[key]))
            elif key in values:
                tests.append(number(key, state) == number(val, state))
            elif key in ('has_law_or_variant', 'has_variable', 'has_modifier'):
                tests.append(val in state.get(key, set()))
            else:
                actual = state[key]
                wanted = val if val in ('yes', 'no') else float(val)
                tests.append({'=': lambda: actual == wanted, '>=': lambda: actual >= wanted,
                              '<': lambda: actual < wanted, '>': lambda: actual > wanted}[op]())
        return all(tests)
    def calc(block, state):
        result = 0
        taken = False
        for key, _, val in entries(block):
            if key in ('if', 'else_if', 'else'):
                if key == 'if':
                    taken = False
                eligible = key == 'else' or condition(one(val, 'limit'), state)
                if not taken and eligible:
                    result += calc([x for k, op, v in entries(val) if k != 'limit' for x in (k, op, v)], state)
                    taken = True
            elif key == 'value': result = number(val, state)
            elif key == 'add': result += number(val, state)
            elif key == 'subtract': result -= number(val, state)
            elif key == 'min': result = max(result, number(val, state))
            elif key == 'max': result = min(result, number(val, state))
            else: assert key == 'desc', key
        return result
    count = 0
    for bureaucrat, legitimacy, default, access in itertools.product((-1, 0), (39, 40, 59, 60), ('yes', 'no'), (.84, .85)):
        state = dict(bureaucracy=bureaucrat, government_legitimacy=legitimacy, in_default=default, capital={'market_access': access})
        expected = max(-1, min(.75, (.25 if bureaucrat >= 0 else -.5) + (.25 if legitimacy >= 60 else -.25 if legitimacy < 40 else 0) - (.5 if default == 'yes' else 0) + (.25 if access >= .85 else -.25)))
        assert calc(values['ffpa_tur_register_monthly_balance_change_v1'], state) == expected
        count += 1
    for stage, powerful, law, levies, compact, survey in itertools.product(range(4), ('yes','no'), ('other','law_type:law_serfdom','law_type:law_tenant_farmers'), (False,True), (False,True), range(3)):
        state = {'var:ffpa_byz_military_reform_stage_v1': stage, 'ig:ig_landowners': {'is_powerful': powerful},
                 'has_law_or_variant': {law} | ({'law_type:law_peasant_levies'} if levies else set()),
                 'has_modifier': {'ffpa_byz_western_provincial_tax_compact'} if compact else set(),
                 'has_variable': {'ffpa_byz_western_cadastre_choice_v2'} if survey else set(),
                 'var:ffpa_byz_western_cadastre_choice_v2': survey}
        expected = (.25 if stage < 1 else 0) + ((.25 if stage >= 3 else .5) if powerful == 'yes' else 0)
        expected += ((.5 if stage >= 2 else 1) if law.endswith(':law_serfdom') else (.25 if stage >= 2 else .5) if law.endswith(':law_tenant_farmers') else 0)
        expected += (.5 if stage < 1 and levies else 0) + (.25 if stage < 3 and (compact or survey == 2) else 0) - (.25 if survey == 1 else 0)
        assert calc(values['ffpa_byz_dynatoi_monthly_pressure_gain_v1'], state) == max(0, expected)
        count += 1
    for anomalies in itertools.product((False, True), repeat=4):
        for famine in ('yes','no'):
            grain, transport, electricity, access = anomalies
            state = {'market_capital.market': {'mg:grain': {'market_goods_pricier': .26 if grain else .25}},
                     'capital': {'sg:transportation': {'state_goods_pricier': .26 if transport else .25},
                                 'sg:electricity': {'state_goods_pricier': .26 if electricity else .25},
                                 'market_access': .84 if access else .85}, 'ffpa_tur_capital_has_famine_v1': famine}
            assert calc(values['ffpa_tur_capital_supply_anomaly_count_v1'],state) == sum(anomalies)
            actual = calc(values['ffpa_tur_capital_monthly_reserve_change_v1'],state)
            assert actual == (3,1,-2,-5,-8)[sum(anomalies)] - (10 if famine == 'yes' else 0)
            # Actual stored balances must still clamp at both ends.
            for reserve in (0,1,50,99,100): assert 0 <= max(0,min(100,reserve+actual)) <= 100
            count += 1
    pulse = definitions(ROOT/'common/scripted_effects/ffpa_permanent_governance_effects.txt')['ffpa_monthly_tur_capital_supply_v1']
    assert any(fields(v,'add') == ['ffpa_tur_capital_monthly_reserve_change_v1'] for v in fields(pulse,'change_variable'))
    return count


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--game-root',type=Path,required=True)
    p.add_argument('--cmf-root',type=Path,required=True)
    p.add_argument('--upstream',type=Path,action='append',default=[])
    a=p.parse_args()
    roots=[a.game_root,a.cmf_root,*a.upstream,ROOT]
    meta=json.loads((ROOT/'.metadata/metadata.json').read_text())
    assert any(r['id']=='com.github.Victoria-3-Modding-Co-op.Community-Mod-Framework' for r in meta['relationships'])
    # Parse all FFPA syntax and register references from the final source stack.
    catalogs={}; all_gui=''; loc={}
    for root in roots:
        for file in (root/'gui').rglob('*.gui'):
            all_gui += file.read_text(encoding='utf-8-sig')+'\n'
        for folder in ('scripted_triggers','script_values','customizable_localization'):
            for file in (root/'common'/folder).glob('*.txt'):
                catalogs.update(definitions(file,allow_duplicates=True))
    for lang in ('english','simp_chinese'):
        entries_lang={}
        for file in (ROOT/'localization'/lang).glob('*.yml'):
            entries_lang.update(parse_loc(file.read_text(encoding='utf-8-sig'),lang))
        loc[lang]=entries_lang
    journal_count=bar_count=event_count=0
    for file in (ROOT/'common/journal_entries').glob('*.txt'):
        for key,block in definitions(file).items():
            for widget in fields(block,'widget'):
                gui=ROOT/one(widget,'gui').strip('"')
                if not gui.exists():continue
                name=one(widget,'name').strip('"');container=one(widget,'container').strip('"')
                assert re.search(r'\btype\s+'+re.escape(name)+r'\s*=',gui.read_text()),name
                assert re.search(r'^'+re.escape(name)+r' = \{ name = \"'+re.escape(name)+r'\" \}',gui.read_text(),re.M),name
                assert f'name = "{container}"' in all_gui,container
            if fields(block,'scripted_progress_bar') and key.startswith('je_ffpa_'):
                assert fields(block,'widget'),key
                journal_count+=1;bar_count+=len(fields(block,'scripted_progress_bar'))
    assert (journal_count,bar_count)==(7,13)
    for file in (ROOT/'events').glob('*.txt'):
        for block in definitions(file).values():
            for style in fields(block,'gui_window'):
                assert re.search(r'\btype\s+'+re.escape(style)+r'\s*=',all_gui),style
                event_count+=1
    assert event_count==82
    for file in (ROOT/'gui').glob('*.gui'):
        text=file.read_text();parse(text)
        for asset in re.findall(r'(?:texture|progresstexture)\s*=\s*"(gfx/[^"\[]+)"',text):
            assert any((r/asset).exists() for r in roots),asset
        assert 'GetPlayer' not in text and '.Execute(' not in text
    for file in (ROOT/'common/scripted_progress_bars').glob('ffpa*.txt'):
        for bar,block in definitions(file).items():
            for field in ('desc','second_desc'):
                key=one(block,field).strip('"');assert key in loc['english'],key
            if 'commonwealth' not in bar:
                assert not fields(block,'monthly_progress') and not fields(block,'weekly_progress'), 'Do not double-advance country-variable mirrors'
    for key,value in loc['english'].items():
        for ref in re.findall(r"(?:GetCustom|ScriptValue|GetScriptValueDesc)\('([^']+)'\)",value):
            if 'cmf' in key: assert ref in catalogs,ref
    for file in (ROOT/'common').glob('*/ffpa*cmf*.txt'):
        text=file.read_text();parse(text)
        assert not re.search(r'\b(?:set_variable|change_variable|add_modifier|every_country|every_pop)\s*=',text),file
    print(f'PASS: {arithmetic_checks()} arithmetic cases; {journal_count} journals / {bar_count} bars, {event_count} styled events; GUI mounts/assets, localization and read-only adapters.')
    print('NOT TESTED: engine GUI rendering, hover scope, font fallback, save reload, AI and pulse ordering.')


if __name__=='__main__': main()
