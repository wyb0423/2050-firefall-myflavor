"""Static agenda contracts. Does not emulate engine parsing or game callbacks."""
import re
from check_north_america_preflight import ROOT, definitions, fields, one
from validate_localization import parse as localization


def main():
    effects = definitions(ROOT / 'common/scripted_effects/ffpa_north_american_effects.txt')
    triggers = definitions(ROOT / 'common/scripted_triggers/ffpa_north_american_triggers.txt')
    events = definitions(ROOT / 'events/ffpa_north_american_events.txt')
    modifiers = definitions(ROOT / 'common/static_modifiers/ffpa_north_american_modifiers.txt')
    source = (ROOT / 'common/scripted_effects/ffpa_north_american_effects.txt').read_text()
    visitor = effects['ffpa_na_union_visit_province_v1']
    snapshot = one(one(visitor, 'if'), 'if')
    assert one(one(snapshot, 'limit'), 'p:$PROVINCE$.state') == 'root.var:ffpa_na_union_target_v1'
    assert one(snapshot, 'set_variable') == 'ffpa_na_union_p_$PROVINCE$_v1'
    assert one(one(snapshot, 'change_variable'), 'name') == 'ffpa_na_union_total_v1'
    assert one(triggers['ffpa_na_union_all_owned_v1'], 'var:ffpa_na_union_seen_v1') == 'var:ffpa_na_union_total_v1'
    assert one(triggers['ffpa_na_union_all_owned_v1'], 'var:ffpa_na_union_owned_v1') == 'var:ffpa_na_union_total_v1'
    assert 'var:ffpa_na_union_total_v1 > 0' in (ROOT / 'common/scripted_triggers/ffpa_north_american_triggers.txt').read_text()
    # Neither disappearance of the original state nor a partial transfer is a success test.
    assert not fields(triggers['ffpa_na_union_all_owned_v1'], 'exists')
    cleanup = effects['ffpa_na_union_cleanup_v1']
    assert 'ffpa_na_union_serial_v1' not in fields(cleanup, 'remove_variable')
    assert 'ffpa_na_union_cooldown_v1' not in fields(cleanup, 'remove_variable')
    claim = one(one(cleanup, 'if'), 'if')
    claim_guard = one(claim, 'limit')
    assert one(claim_guard, 'has_variable') == 'ffpa_na_union_claim_v1'
    assert any(fields(n, 'has_variable') == ['ffpa_na_union_external_claim_v1'] for n in fields(claim_guard, 'NOT'))
    assert any(fields(n, 'any_scope_state') for n in fields(claim_guard, 'NOT'))
    assert 'name = ffpa_na_union_deadline_v1 years = 10' in source
    assert 'name = ffpa_na_union_cooldown_v1 years = 3' in source
    assert 'name = ffpa_na_union_cooldown_v1 years = 1' in source
    settle = one(effects['ffpa_na_union_settle_v1'], 'if')
    assert one(one(settle, 'limit'), 'var:ffpa_na_union_serial_v1') == 'scope:ffpa_na_union_event_serial'
    payment = one(settle, 'if')
    assert one(one(payment, 'limit'), 'ffpa_na_union_all_owned_v1') == 'yes'
    assert one(one(payment, 'limit'), 'ffpa_na_union_peace_v1') == 'yes'
    assert one(one(payment, 'add_modifier'), 'years') == '5'
    assert fields(payment, 'set_variable')[0] == ['name', '=', 'ffpa_na_union_status_v1', 'value', '=', '3']
    assert fields(payment, 'ffpa_na_union_cleanup_v1') == ['yes']
    rewards = {
        'dividend': {'country_prestige_mult': '0.10', 'country_legitimacy_base_add': '5'},
        'market': {'state_construction_mult': '0.25', 'building_group_bg_infrastructure_throughput_add': '0.20', 'building_group_bg_manufacturing_throughput_add': '0.10'},
        'government': {'state_tax_capacity_mult': '0.25', 'state_incorporation_speed_mult': '0.50', 'state_turmoil_effects_mult': '-0.25'},
    }
    for kind, values in rewards.items():
        for key, value in values.items():
            assert one(modifiers[f'ffpa_na_union_{kind}_v1'], key) == value
    # Exact phase-boundary calls and native references, not a second state machine.
    assert 'annex =' not in source and 'set_owner_of_provinces' not in source
    catalog = []
    for lang in ('english', 'simp_chinese'):
        path = ROOT / f'localization/{lang}/ffpa_north_american_l_{lang}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        catalog.append(localization(path.read_text(encoding='utf-8-sig'), lang))
    assert catalog[0].keys() == catalog[1].keys()
    for n, options in ((3, 2), (4, 2), (5, 1)):
        event = events[f'ffpa_na_flavor.{n}']
        assert len(fields(event, 'option')) == options
        for field in ('title', 'desc', 'flavor'):
            assert one(event, field) in catalog[0]
        for option in fields(event, 'option'):
            assert one(option, 'name') in catalog[0]
    for category in ('scripted_effects', 'scripted_triggers'):
        path = ROOT / f'common/{category}/ffpa_north_american_union_provinces.txt'
        definitions(path)
        provinces = set(re.findall(r'(?:PROVINCE = |p:)(x[0-9A-Fa-f]{6})', path.read_text()))
        assert len(provinces) == 2192
    strategy = definitions(ROOT / 'common/ai_strategies/ffpa_north_american_strategies.txt')['ai_strategy_ffpa_na_union_v1']
    assert one(one(strategy, 'possible'), 'var:ffpa_na_union_status_v1') == '1'
    scores = one(strategy, 'wargoal_scores')
    assert set(scores[::3]) == {'return_state', 'conquer_state'}
    print('PASS: province snapshot ownership, claim guards, fixed deadlines/cooldowns, guarded full rewards, event localization and bounded AI scope.')
    print('NOT TESTED: engine macros/scopes, selectors, callback timing, claim regrants, AI choices, state merge inheritance or save reload.')


if __name__ == '__main__':
    main()
