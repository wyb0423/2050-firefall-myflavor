"""Read-only project-view contracts; does not execute the game GUI."""
import re
import sys
from check_north_america_preflight import ROOT, definitions, fields, one, parse
from check_cmf_presentation import entries
sys.path.insert(0, str(ROOT / 'tools'))
from generate_cmf_project_widgets import outputs


def main():
    generated = outputs()
    sguis = {}
    for path in (ROOT / 'common/scripted_guis').glob('ffpa*.txt'):
        sguis.update(definitions(path))
    for name, content in generated.items():
        assert (ROOT / name).read_text() == content, f'Regenerate {name}'
        if name.endswith('.yml'):
            continue
        parse(content)
        assert not re.search(r'\b(set_variable|change_variable|add_modifier|every_country|every_pop)\s*=', content)
        for ref in re.findall(r"GetScriptedGui\('([^']+)'\)", content):
            assert ref in sguis, ref
        for expression in re.findall(r'"(\[[^"\n]*\])"', content):
            depth = 0
            for char in re.sub(r"'[^']*'", '', expression):
                depth += (char == '(') - (char == ')')
                assert depth >= 0, expression
            assert depth == 0, expression
    journals = definitions(ROOT / 'common/journal_entries/ffpa_imperial_regional_development.txt')
    count = 0
    for key, journal in journals.items():
        name = key.removeprefix('je_') + '_cmf_project'
        states = fields(one(journal, 'complete'), 'any_scope_state')
        shown = fields(one(sguis[name + '_details'], 'effect'), 'if')
        assert len(states) == len(shown)
        for original, row in zip(states, shown):
            # Preserve every comparison/operator and the per-state AND grouping.
            whole = one(fields(row, 'if')[0], 'limit')
            assert list(entries(original)) == list(entries(whole))
            count += 1
    assert len(journals) == 15 and count == 56
    levels = definitions(ROOT / 'common/script_values/ffpa_regional_development_cmf.txt')
    for block in levels.values():
        loop = one(block, 'every_scope_building')
        # Script-value min is a floor (max would cap the result at zero).
        assert one(block, 'value') == '0' and one(loop, 'min') == 'this.level'
        assert not fields(loop, 'add') and not fields(loop, 'max')
    assert list(entries(one(sguis['ffpa_na_cmf_building_staffed'], 'is_valid'))) == [('level', '>', '0'), ('occupancy', '>=', '0.60')]
    gui = generated['gui/ffpa_north_american_cmf.gui']
    routes = definitions(ROOT / 'common/scripted_triggers/ffpa_north_american_triggers.txt')
    kinds = [kind for route in range(1, 4) for kind in fields(one(routes[f'ffpa_na_local_building_{route}_v1'], 'OR'), 'is_building_type')]
    assert len(kinds) == 16
    assert re.findall(r'text = (building_\w+) autoresize', gui) == kinds
    assert 'GetExpansionLevel' not in gui and '.Execute(' not in gui
    values = definitions(ROOT / 'common/script_values/ffpa_permanent_governance_values.txt')
    counters = [k for k in values if k.endswith('_months_v1_display') and '_repair_' not in k]
    assert len(counters) == 8
    runtime = (ROOT / 'common/scripted_effects/ffpa_permanent_governance_effects.txt').read_text()
    for key in counters:
        variable = key.removesuffix('_display')
        block = values[key]
        assert variable in runtime and one(block, 'value') == '0'
        branch = one(block, 'if')
        assert one(one(branch, 'limit'), 'has_variable') == variable
        assert one(branch, 'value') == 'var:' + variable
    print('PASS: 15 journals / 56 state requirements; 16 route building rows; 8 safe counters; generated consistency, GUI expressions and read-only scope contracts.')


if __name__ == '__main__':
    main()
