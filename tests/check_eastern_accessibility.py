"""Threshold boundaries and shared-rule contracts; not an engine simulation."""
from itertools import combinations
from check_north_america_preflight import ROOT, definitions, one, fields
from check_cmf_presentation import entries

TR = definitions(ROOT / 'common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt')
TR.update(definitions(ROOT / 'common/scripted_triggers/ffpa_turkish_flavor_triggers.txt'))
JE = definitions(ROOT / 'common/journal_entries/ffpa_eastern_mediterranean_journal_entries.txt')


def condition(block, owned):
    results = []
    for key, op, value in entries(block):
        if key == 'owns_entire_state_region':
            results.append(value in owned)
        elif key == 'calc_true_if':
            parts = list(entries(value))
            assert parts[0][:2] == ('amount', '>=')
            results.append(sum(condition([k, o, v], owned) for k, o, v in parts[1:]) >= int(parts[0][2]))
        else:
            raise AssertionError(f'Unsupported territory condition: {key}')
    return all(results)


def scalar(block, key, op, expected):
    assert [(o, v) for k, o, v in entries(block) if k == key] == [(op, str(expected))], key


def main():
    formation = definitions(ROOT / 'common/country_formation/ffpa_byzantium.txt')['BYZ']
    states = one(formation, 'states')
    shared = 'ffpa_byz_foundation_territory_ready_v1'
    assert len(set(states)) == 12
    anchors = {'STATE_EASTERN_THRACE', 'STATE_ATTICA'}
    for n in range(13):
        for owned in combinations(states, n):
            expected = n >= 10 and anchors <= set(owned)
            assert condition(TR[shared], owned) == expected
            if expected:
                assert n / len(states) >= float(one(formation, 'required_states_fraction'))
    scalar(one(formation, 'potential'), 'country_definition', '=', 'cd:GRE')
    assert one(one(formation, 'ai_will_do'), 'has_variable') == 'embrace_ambitious_agenda_var'
    for block in (one(formation, 'possible'), one(JE['je_ffpa_byz_new_rome'], 'complete')):
        assert any(fields(tooltip, shared) == ['yes'] for tooltip in fields(block, 'custom_tooltip'))

    rebuild = one(JE['je_ffpa_tur_rebuild_anatolia'], 'complete')
    scalar(one(rebuild, 'calc_true_if'), 'amount', '>=', 8)
    scalar(next(v for k, o, v in entries(rebuild) if k == 'gdp'), 'multiply', '=', 1.15)
    scalar(one(rebuild, 'any_scope_state'), 'count', '>=', 6)
    new_rome = one(JE['je_ffpa_byz_new_rome'], 'complete')
    scalar(new_rome, 'government_legitimacy', '>=', 50)
    scalar(one(new_rome, 'any_scope_state'), 'count', '>=', 7)
    assert one(one(new_rome, 'capital'), 'state_region') == 's:STATE_EASTERN_THRACE'
    for name, levels in [('tur_gate_of_two_continents', [4, 4, 4]), ('byz_restore_new_rome', [6, 6, 6, 4, 4])]:
        state = one(one(JE['je_ffpa_' + name], 'complete'), 'any_scope_state')
        buildings = fields(state, 'any_scope_building')
        assert len(buildings) == len(levels)
        for building, level in zip(buildings, levels):
            scalar(building, 'level', '>=', level)
    for name, count in [('porte_charter', 6), ('second_foundation', 6), ('directorate', 4)]:
        block = TR[f'ffpa_tur_{name}_completion_conditions_v1']
        scalar(block, 'government_legitimacy', '>=', 50)
        scalar(block, 'bureaucracy', '>=', 0)
        scalar(one(block, 'any_scope_state'), 'count', '>=', count)
        if name != 'porte_charter':
            scalar(block, 'literacy_rate', '>=', '0.25')
    council = TR['ffpa_tur_ai_frontier_council_ready_v1']
    assert {k for k, _, _ in entries(council)} == {'ffpa_tur_frontier_council_ready_v1', 'infamy', 'gold_reserves'}
    scalar(council, 'infamy', '<', 'infamy_threshold:infamous')
    scalar(council, 'gold_reserves', '>', 0)
    for tag, leg, admin, civic, count, access in [('tur', 3, 5, 5, 6, '0.70'), ('byz', 2, 4, 4, 7, '0.75')]:
        base = f'ffpa_{tag}_commonwealth_'
        scalar(TR[base + f'administration_conditions_factor_{leg}'], 'government_legitimacy', '>=', 50)
        state = one(TR[base + f'administration_conditions_factor_{admin}'], 'any_scope_state')
        scalar(state, 'count', '>=', count)
        scalar(state, 'market_access', '>=', access)
        scalar(one(TR[base + f'civic_conditions_factor_{civic}'], 'calc_true_if'), 'amount', '>=', 3)
    decision = definitions(ROOT / 'common/decisions/ffpa_eastern_mediterranean_decisions.txt')['ffpa_request_eastern_roman_title']
    event = definitions(ROOT / 'events/ffpa_eastern_mediterranean_events.txt')['ffpa_flavor.8']
    scalar(one(decision, 'possible'), 'government_legitimacy', '>=', 60)
    scalar(one(event, 'trigger'), 'government_legitimacy', '>=', 60)
    assert [one(one(option, 'ai_chance'), 'factor') for option in fields(event, 'option')] == ['2', '1']
    # The CMF hover text must use the same factors and retain stable IDs.
    from validate_localization import parse as parse_loc
    for lang in ('english', 'simp_chinese'):
        path = ROOT / f'localization/{lang}/ffpa_eastern_mediterranean_cmf_l_{lang}.yml'
        loc = parse_loc(path.read_text(encoding='utf-8-sig'), lang)
        for tag, leg, admin, civic, count, access in [('tur', 3, 5, 5, 6, 70), ('byz', 2, 4, 4, 7, 75)]:
            base = f'ffpa_{tag}_commonwealth_'
            for status in ('yes', 'no'):
                assert '50' in loc[base + f'administration_conditions_factor_{leg}_status_{status}']
                text = loc[base + f'administration_conditions_factor_{admin}_status_{status}']
                assert str(count) in text and str(access) + '%' in text
                text = loc[base + f'civic_conditions_factor_{civic}_status_{status}']
                assert 'At least 3' in text if lang == 'english' else '至少3' in text
    print('PASS: all 4096 BYZ territory subsets; shared entry rules, route/capital/commonwealth thresholds and title AI choices')


if __name__ == '__main__':
    main()
