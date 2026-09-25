"""Run the actual reform/restore subset; not engine scheduling, UI or save-format proof."""
from copy import deepcopy
from math import inf
from check_north_america_preflight import ROOT, definitions, fields, one
from check_cmf_presentation import entries
from check_usa_governance import Script


class ReformScript(Script):
    """Reuse the existing interpreter with two native shorthand forms used here."""
    def __init__(self, tag='BYZ'):
        super().__init__()
        self.effects = definitions(ROOT / 'common/scripted_effects/ffpa_permanent_governance_effects.txt')
        self.triggers = {}; self.values = {}
        self.country = self.scope(country_definition='cd:' + tag, in_default='no', states=[])

    def cond(self, block, c=None, p=None):
        for k, op, value in entries(block):
            if k == 'ROOT':
                if not self.cond(value, self.country): return False
            elif not super().cond([k, op, value], c, p): return False
        return True

    def run(self, block, c=None, p=None):
        if isinstance(block, str): block = self.effects[block]
        normalized = []
        for k, op, value in entries(block):
            if k == 'add_modifier' and isinstance(value, str): value = ['name', '=', value]
            normalized.extend((k, op, value))
        super().run(normalized, c, p)


def main():
    stage = 'ffpa_byz_military_reform_stage_v1'
    project = 'ffpa_byz_military_reform_project_v1'
    months = 'ffpa_byz_military_reform_project_months_v1'
    fatigue = 'ffpa_byz_military_reform_fatigue_v1'
    pressure = 'ffpa_byz_dynatoi_pressure_v1'
    welfare = 'ffpa_byz_supply_veterans_welfare_v1'
    costs = {1: 'ffpa_byz_military_register_professional_cost_v1',
             2: 'ffpa_byz_land_tenure_reform_cost_v1', 3: 'ffpa_byz_supply_veterans_reform_cost_v1'}
    initialize = 'ffpa_initialize_byz_dynatoi_v1'
    ensure = 'ffpa_ensure_byz_supply_veterans_welfare_v1'
    monthly = 'ffpa_monthly_byz_military_reform_project_v1'
    event = definitions(ROOT / 'events/ffpa_byzantine_permanent_governance_events.txt')['ffpa_flavor.53']

    def active(number=3, tag='BYZ'):
        script = ReformScript(tag)
        script.country['variables'].update({stage: number - 1, project: number, months: 0, pressure: 80})
        script.country['modifiers'][costs[number]] = (60, 1)  # An existing five-year project cost.
        script.run(initialize)
        return script

    def pulse(script):
        script.tick(); script.run(monthly)

    # The first two real phase completions retain their reductions and stay silent.
    for number, duration, reduction in ((1, 12, 15), (2, 18, 20), (3, 24, 25)):
        s = active(number); variables = s.country['variables']
        for _ in range(duration - 1): pulse(s)
        assert variables[stage] == number - 1 and variables[months] == duration - 1
        assert variables[pressure] == 80 and not s.events
        assert not s.cond(one(event, 'trigger'))
        pulse(s)
        assert variables[stage] == number and variables[pressure] == 80 - reduction
        assert project not in variables and months not in variables
        assert s.country['expiry'][fatigue] == s.now + 36
        assert s.country['modifiers'][costs[number]] == (60, 1), 'Notification must not cancel or renew existing costs'
        assert s.events == (['ffpa_flavor.53'] if number == 3 else [])
        if number < 3:
            assert welfare not in variables and welfare not in s.country['modifiers']
        else:
            assert variables[welfare] == 1 and s.country['modifiers'][welfare] == (inf, 1)
            assert s.cond(one(event, 'trigger'))
            completed = deepcopy(s.country)
            for _ in range(3): s.run(monthly); s.run(initialize); s.run(ensure)
            assert s.country == completed and s.events == ['ffpa_flavor.53']

    # Default suspends the actual project counter, including the final observation.
    s = active(); s.country['variables'][months] = 23
    s.country['in_default'] = 'yes'
    for _ in range(3): pulse(s)
    assert s.country['variables'][months] == 23 and not s.events
    s.country['in_default'] = 'no'; pulse(s)
    assert s.events == ['ffpa_flavor.53']

    # Old stage-three saves restore the permanent welfare mirror without a new event.
    s = ReformScript(); s.country['variables'].update({stage: 3, pressure: 55})
    s.run(initialize)
    assert s.country['variables'][welfare] == 1 and s.country['modifiers'][welfare] == (inf, 1)
    restored = deepcopy(s.country)
    for _ in range(3): s.run(ensure); s.run(initialize); s.run(monthly)
    assert s.country == restored and not s.events

    # Neither foreign completion nor missing completed-state facts can display the notice.
    foreign = active(tag='TUR'); foreign.country['variables'][months] = 23; pulse(foreign)
    assert not foreign.events and not foreign.cond(one(event, 'trigger'))
    for missing in (stage, welfare):
        removed = s.country['variables'].pop(missing)
        assert not s.cond(one(event, 'trigger'))
        s.country['variables'][missing] = removed

    completion = s.effects['ffpa_complete_byz_military_reform_project_v1']
    dispatch = one(one(fields(completion, 'else_if')[-1], 'if'), 'trigger_event')
    assert one(dispatch, 'id') == 'ffpa_flavor.53'
    assert one(dispatch, 'days') == '1' and one(dispatch, 'popup') == 'yes'
    modifiers = definitions(ROOT / 'common/static_modifiers/ffpa_permanent_governance_modifiers.txt')
    assert one(modifiers[welfare], 'state_welfare_payments_add') == '0.10'
    assert not fields(event, 'immediate')
    option = one(event, 'option')
    assert {k for k, op, value in entries(option)} == {'name', 'default_option'}
    before = deepcopy((s.country, s.events)); s.run(option); s.run(option)
    assert (s.country, s.events) == before
    print('PASS: actual reform phases, 24-month first notification, default pause, recovery silence, strict BYZ delivery, unchanged reductions/welfare/fatigue/cleanup and acknowledgement-only option.')
    print('NOT TESTED: engine event delivery, JE pulse ordering, GUI or save reload.')


if __name__ == '__main__': main()
