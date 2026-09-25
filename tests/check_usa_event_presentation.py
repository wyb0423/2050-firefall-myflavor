"""Check narrative/hover separation and local assets; not engine tooltip rendering."""
import argparse
from pathlib import Path
import re
from check_north_america_preflight import ROOT, definitions, fields, one
from validate_localization import parse as parse_loc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, required=True)
    args = parser.parse_args()
    events = {}
    for name in ('political', 'economic', 'governance'):
        events.update(definitions(ROOT / f'events/ffpa_american_{name}_events.txt'))
    assert set(events) == {f'ffpa_usa_flavor.{n}' for n in [*range(1, 17), 30, 31, 40, 41, 43, 44]}
    predecessor = definitions(ROOT / 'events/ffpa_north_american_events.txt')
    assert set(predecessor) == {f'ffpa_na_flavor.{n}' for n in range(1, 6)}
    events.update(predecessor)
    media = definitions(args.game_root / 'gfx/media_aliases/media_aliases.txt')
    for event in events.values():
        assert (args.game_root / one(event, 'icon').strip('"')).is_file()
        alias = one(one(event, 'event_image'), 'video').strip('"')
        assert alias in media
        assert (args.game_root / one(media[alias], 'video').strip('"')).is_file()
    assert len({one(e, 'icon') for e in events.values()}) == 4
    assert len({one(one(e, 'event_image'), 'video') for e in events.values()}) == 4
    for lang in ('english', 'simp_chinese'):
        loc = {}
        for path in (ROOT / 'localization' / lang).glob('*.yml'):
            loc.update(parse_loc(path.read_text(encoding='utf-8-sig'), lang))
        for event in events.values():
            desc = loc[one(event, 'desc')]
            assert desc.strip() and loc[one(event, 'flavor')].strip()
            # A compact scene need not imitate the layout of a long draft review.
            if one(event, 'title') == 'ffpa_usa_flavor.9.t':
                assert r'\n\n' in desc and '#bold ' in desc
            assert not re.search(r'\d\s*(?:%|个百分点|percentage points)', desc)
            assert not re.search(r'\$\w+_tt\$', desc)
            for option in fields(event, 'option'):
                label = loc[one(option, 'name')]
                assert not re.search(r'\d\s*(?:%|个百分点|percentage points)', label)
        for name in ('continental_market', 'industrial_scale'):
            reason = loc[f'je_ffpa_usa_{name}_v1_reason']
            assert '_route_text_v1' not in reason and not re.search(r'\d\s*(?:%|公司|company)', reason)
        assert all('$ffpa_usa_charter_window_tt$' in loc[k] for k in (
            'ffpa_usa_charter_draft_tt', 'ffpa_usa_charter_sign_hover_tt', 'ffpa_usa_charter_defer_hover_tt'))
        grant = loc['ffpa_usa_grant_cost_hover_tt']
        assert "ScriptValue('ffpa_usa_economy_weekly_grant_v1')" in grant
        assert '52' in grant and ('两年' in grant or 'two years' in grant)

    # Compound settlement is explained once; its real effect still executes once.
    for number, helper, tips in [
        (11, 'ffpa_usa_market_settle_v1', ('ffpa_usa_market_core_reward_tt', 'ffpa_usa_market_branches_reward_tt')),
        (14, 'ffpa_usa_industry_settle_v1', ('ffpa_usa_company_entry_hover_tt', 'ffpa_usa_company_champions_hover_tt')),
    ]:
        for choice, (option, tip) in enumerate(zip(fields(events[f'ffpa_usa_flavor.{number}'], 'option'), tips), 1):
            branch = one(option, 'if')
            assert one(one(one(branch, 'limit'), 'ffpa_usa_economy_event_valid_v1'), 'EVENT') == str(number)
            assert one(branch, 'custom_tooltip') == tip
            assert one(one(one(branch, 'hidden_effect'), helper), 'CHOICE') == str(choice)
            assert not fields(branch, helper)
    for number, part, reward in [(10, 'market', 'linkage'), (13, 'industry', 'training')]:
        branch = one(fields(events[f'ffpa_usa_flavor.{number}'], 'option')[0], 'if')
        assert one(branch, 'custom_tooltip') == 'ffpa_usa_grant_cost_hover_tt'
        hidden = one(branch, 'hidden_effect')
        assert one(one(hidden, 'set_variable'), 'value') == 'ffpa_usa_economy_weekly_grant_v1'
        fee = one(hidden, 'add_modifier')
        assert one(fee, 'multiplier') == f'var:ffpa_usa_{part}_grant_weekly_v1'
        assert one(fee, 'years') == '2'
        assert one(one(branch, 'add_modifier'), 'name') == f'ffpa_usa_{part}_{reward}_v1'
    # Future project rewards need explicit hovers: selection only stores a route.
    for option, tip in zip(fields(predecessor['ffpa_na_flavor.1'], 'option')[:3], (
        'ffpa_na_local_food_reward_tt', 'ffpa_na_local_industry_reward_tt', 'ffpa_na_local_transport_reward_tt')):
        assert one(one(option, 'if'), 'custom_tooltip') == tip
    for option, tip in zip(fields(predecessor['ffpa_na_flavor.4'], 'option')[:2], (
        'ffpa_na_union_market_reward_tt', 'ffpa_na_union_government_reward_tt')):
        assert one(one(option, 'if'), 'custom_tooltip') == tip
    assert one(one(predecessor['ffpa_na_flavor.5'], 'option'), 'custom_tooltip') == 'ffpa_na_union_failure_tt'
    for lang in ('english', 'simp_chinese'):
        loc = parse_loc((ROOT / f'localization/{lang}/ffpa_north_american_l_{lang}.yml').read_text(encoding='utf-8-sig'), lang)
        rules = loc['ffpa_na_local_route_rules_tt']
        assert all(value in rules for value in ('3', '60%', '80%', '12'))
        for route in ('food', 'industry', 'transport'):
            tip = loc[f'ffpa_na_local_{route}_reward_tt']
            assert '$ffpa_na_local_route_rules_tt$' in tip
            assert ('+10%' if route == 'transport' else '+5%') in tip
        dividend = loc['ffpa_na_union_dividend_tt']
        assert '+10%' in dividend and '+5#!' in dividend and '+5%' not in dividend
        for route in ('market', 'government'):
            assert '$ffpa_na_union_dividend_tt$' in loc[f'ffpa_na_union_{route}_reward_tt']
    gui = (ROOT / 'gui/ffpa_usa_journal_presentation.gui').read_text()
    for name in ('market', 'industry'):
        assert f'tooltip = ffpa_usa_ui_{name}_outcomes_tt' in gui
    print('PASS: 27 bilingual USA/predecessor events, short choices, bound future/settlement/grant hovers, four icon/image themes and journal outcome tooltips.')
    print('NOT TESTED: native effect tooltip rendering, hover scope, line wrapping or image framing in game.')


if __name__ == '__main__':
    main()
