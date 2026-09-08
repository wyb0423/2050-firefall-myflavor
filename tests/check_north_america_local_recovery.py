"""Static contracts for local recovery; does not simulate engine execution."""
import re
from check_north_america_preflight import ROOT, EXPECTED_TAGS, definitions, fields, one
from validate_localization import parse as parse_localization


def main():
    paths = sorted((ROOT / 'common').glob('*/ffpa_north_american*.txt'))
    paths += [ROOT / 'events/ffpa_north_american_events.txt']
    catalog = {}
    for path in paths:
        for key, block in definitions(path).items():
            assert key not in catalog, f'Duplicate North America object: {key}'
            catalog[key] = block
    source = '\n'.join(path.read_text() for path in paths)
    references = set(re.findall(r'(?<![:\w])(ffpa_na_[\w-]+)\s*(?:[<>]=?|=)\s*(?:yes|no|[\d{])', source))
    assert references <= catalog.keys(), sorted(references - catalog.keys())
    identity = catalog['ffpa_na_is_predecessor_v1']
    assert one(identity, 'is_revolutionary') == 'no'
    assert set(fields(one(identity, 'OR'), 'country_definition')) == {'cd:' + tag for tag in EXPECTED_TAGS}
    assert len(fields(one(catalog['ffpa_na_is_mainland_state_v1'], 'OR'), 'state_region')) == 49
    je = catalog['je_ffpa_na_local_recovery_v1']
    assert fields(je, 'on_monthly_pulse') and not fields(je, 'timeout')
    assert one(one(je, 'on_invalid'), 'ffpa_na_local_cleanup_v1') == 'yes'
    complete = one(je, 'complete')
    assert one(complete, 'ffpa_na_local_target_valid_v1') == 'yes'
    assert one(complete, 'has_variable') == 'ffpa_na_local_route_v1'
    assert 'var:ffpa_na_local_months_v1 >= 12' in source
    assert source.count('occupancy >= 0.60') == 3
    assert 'market_access >= 0.80' in source
    assert 'ffpa_na_local_qualified_levels_v1 >= 3' in source
    monthly = fields(catalog['ffpa_na_local_monthly_v1'], 'if')[0]
    change = one(monthly, 'if')
    assert one(one(change, 'change_variable'), 'add') == '1'
    reset = one(one(monthly, 'else'), 'set_variable')
    assert one(reset, 'name') == 'ffpa_na_local_months_v1' and one(reset, 'value') == '0'
    completion = one(catalog['ffpa_na_local_complete_v1'], 'if')
    guard = one(completion, 'limit')
    assert one(one(guard, 'NOT'), 'has_variable') == 'ffpa_na_local_complete_v1'
    assert fields(completion, 'set_variable') == ['ffpa_na_local_complete_v1']
    cleanup = catalog['ffpa_na_local_cleanup_v1']
    assert 'ffpa_na_local_complete_v1' not in fields(cleanup, 'remove_variable')
    assert 'ffpa_na_local_progress_event_v1' not in fields(cleanup, 'remove_variable')
    assert not fields(cleanup, 'remove_modifier'), 'Completed state rewards must survive cleanup'
    for kind in ('food', 'industry', 'transport'):
        assert catalog[f'ffpa_na_local_{kind}_v1']
        exclusions = fields(catalog['ffpa_na_local_candidate_state_v1'], 'NOT')
        assert any(fields(block, 'has_modifier') == [f'ffpa_na_local_{kind}_v1'] for block in exclusions)
    start = catalog['ffpa_na_flavor.1']
    assert one(one(start, 'trigger'), 'has_variable') == 'ffpa_na_local_choice_pending_v1'
    options = fields(start, 'option')
    assert len(options) == 4 and one(options[-1], 'default_option') == 'yes'
    for option in options[:3]:
        guard = one(one(option, 'if'), 'limit')
        assert one(guard, 'var:ffpa_na_local_target_v1') == 'scope:ffpa_na_event_target'
    assert one(one(catalog['ffpa_na_flavor.2'], 'immediate'), 'remove_variable') == 'ffpa_na_local_notice_pending_v1'
    assert len(fields(catalog['ffpa_na_flavor.2'], 'option')) == 2
    assert 'var:ffpa_na_local_months_v1 >= 6' in source
    assert 'state_infrastructure_mult' not in source
    catalogs = []
    for language in ('english', 'simp_chinese'):
        path = ROOT / f'localization/{language}/ffpa_north_american_l_{language}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        catalogs.append(parse_localization(path.read_text(encoding='utf-8-sig'), language))
    assert catalogs[0].keys() == catalogs[1].keys()
    for event in ('ffpa_na_flavor.1', 'ffpa_na_flavor.2'):
        for field in ('title', 'desc', 'flavor'):
            assert one(catalog[event], field) in catalogs[0]
        for option in fields(catalog[event], 'option'):
            assert one(option, 'name') in catalogs[0]
    assert 'every_pop' not in source and 'every_country' not in source
    print(f'PASS: {len(catalog)} objects; identity, threshold/reset, one-time reward, invalidation, event guards and bilingual text.')
    print('NOT TESTED: native activation, variable-index state selector, UI, monthly timing, state split/merge or save reload.')


if __name__ == '__main__':
    main()
