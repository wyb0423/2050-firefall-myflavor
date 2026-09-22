"""Execute the predecessor activation/selection subset; native scope/UI behavior remains unverified."""
from check_north_america_preflight import ROOT, EXPECTED_TAGS, definitions, fields, one
from check_cmf_presentation import entries


def main():
    effects = definitions(ROOT/'common/scripted_effects/ffpa_north_american_effects.txt')
    triggers = definitions(ROOT/'common/scripted_triggers/ffpa_north_american_triggers.txt')
    journals = definitions(ROOT/'common/journal_entries/ffpa_north_american_journal_entries.txt')
    actions = definitions(ROOT/'common/on_actions/ffpa_north_american_on_actions.txt')
    events = definitions(ROOT/'events/ffpa_north_american_events.txt')
    prefix = 'ffpa_na_local_'
    local = 'je_ffpa_na_local_recovery_v1'
    union = 'je_ffpa_na_union_agenda_v1'
    scopes = {}; queued = []; skip_variable_position = False
    country = {'variables': {}, 'states': [], 'journals': set()}

    def value(v, ctx, prev=None):
        if v == 'root': return country
        if v == 'prev': return prev
        if v.startswith('root.var:'): return country['variables'].get(v[9:])
        if v.startswith('var:'): return ctx['variables'].get(v[4:])
        if v.startswith('scope:'): return scopes.get(v[6:])
        try: return float(v)
        except ValueError: return ctx.get(v, v)

    def condition(block, ctx):
        checks = []
        for k, op, v in entries(block):
            if k in ('OR', 'AND', 'NOT'):
                children = [condition([a, b, c], ctx) for a, b, c in entries(v)]
                checks.append(any(children) if k == 'OR' else not all(children) if k == 'NOT' else all(children))
            elif k in triggers: checks.append(condition(triggers[k], ctx) == (v == 'yes'))
            elif k == 'any_scope_state': checks.append(any(condition(v, s) for s in ctx['states']))
            elif k == 'has_variable': checks.append(v in ctx['variables'])
            elif k == 'has_journal_entry': checks.append(v in ctx['journals'])
            elif k == 'has_modifier': checks.append(v in ctx['modifiers'])
            elif k == 'exists': checks.append(value(v, ctx) is not None)
            elif isinstance(v, list):
                target = value(k, ctx)
                checks.append(isinstance(target, dict) and condition(v, target))
            else:
                actual = value(k, ctx); wanted = value(v, ctx)
                checks.append(actual is not None and {'=': lambda: actual == wanted, '>=': lambda: actual >= wanted}[op]())
        return all(checks)

    def execute(block, ctx=None, prev=None):
        if ctx is None: ctx = country
        taken = False
        for k, op, v in entries(block):
            if k in ('if', 'else_if', 'else'):
                if k == 'if': taken = False
                if not taken and (k == 'else' or condition(one(v, 'limit'), ctx)):
                    taken = True
                    execute([x for a, b, c in entries(v) if a != 'limit' for x in (a, b, c)], ctx, prev)
            elif k in effects: execute(effects[k], ctx, prev)
            elif k == 'set_variable':
                if isinstance(v, str): ctx['variables'][v] = 1
                else: ctx['variables'][one(v, 'name')] = value(one(v, 'value'), ctx, prev) if fields(v, 'value') else 1
            elif k == 'change_variable': ctx['variables'][one(v, 'name')] += value(one(v, 'add'), ctx, prev)
            elif k == 'remove_variable': ctx['variables'].pop(v, None)
            elif k == 'remove_modifier': ctx['modifiers'].discard(v)
            elif k in ('every_scope_state', 'ordered_scope_state'):
                selected = [s for s in ctx['states'] if condition(one(v, 'limit'), s)]
                if k == 'ordered_scope_state':
                    selected.sort(key=lambda s: value(one(v, 'order_by'), s), reverse=True)
                    position = one(v, 'position')
                    selected = [] if skip_variable_position and position.startswith('root.var:') else selected[int(value(position, ctx)):int(value(position, ctx))+1]
                body = [x for a, b, c in entries(v) if a not in ('limit', 'position', 'order_by', 'check_range_bounds') for x in (a, b, c)]
                for target in selected: execute(body, target, ctx)
            elif k == 'ordered_state': pass  # No neighbouring countries in this fixture.
            elif k in ('owner', 'root'): execute(v, value(k, ctx), ctx)
            elif k == 'add_journal_entry':
                name = one(v, 'type'); assert name not in ctx['journals']
                ctx['journals'].add(name); execute(one(journals[name], 'immediate'), ctx)
            elif k == 'trigger_event':
                assert one(v, 'popup') == 'yes'; queued.append(one(v, 'id'))
            elif k.startswith('je:'): pass  # Native progress-bar mirror.
            else: raise AssertionError((k, op, v))

    def reset(tag='ZZZGEORGIA'):
        nonlocal skip_variable_position
        skip_variable_position = False; scopes.clear(); queued.clear()
        country.update(country_definition='cd:'+tag, is_revolutionary='no', variables={}, journals=set(), modifiers=set())
        state = {'state_region': 's:STATE_GEORGIA', 'state_population': 100, 'owner': country, 'variables': {}, 'modifiers': set()}
        country['states'] = [state]
        return state

    wrapper = 'ffpa_na_predecessor_journals_monthly_v2'
    assert wrapper in one(actions['on_monthly_pulse_country'], 'on_actions')
    recover = one(actions[wrapper], 'effect')
    for tag in EXPECTED_TAGS:
        state = reset(tag); execute(recover)
        assert country['journals'] == {local, union} and country['variables'][prefix+'target_v1'] is state
        country['variables'].update({prefix+'route_v1': 1, prefix+'months_v1': 5, prefix+'choice_pending_v1': 1})
        saved = country['variables'].copy(); country['journals'].clear(); execute(recover); execute(recover)
        assert country['variables'] == saved and not queued, 'Recovery must preserve a valid project and its pending event'

    state = reset(); skip_variable_position = True; execute(recover)
    assert country['variables'][prefix+'target_v1'] is state, 'Literal first-state fallback'
    assert not condition(one(journals[local], 'invalid'), country)
    state = reset(); scopes['ffpa_na_selected_state'] = state; country['states'].clear()
    country['variables'][prefix+'index_v1'] = 0; execute(effects[prefix+'select_target_v1'])
    assert prefix+'target_v1' not in country['variables'], 'Never reuse an inherited event scope after empty selection'
    assert condition(one(journals[local], 'invalid'), country)

    state = reset(); execute(recover); country['variables'].pop(prefix+'target_v1')
    assert not condition(one(journals[local], 'invalid'), country), 'Missing target alone must not destroy the JE'
    country['variables'].update({prefix+'route_v1': 2, prefix+'months_v1': 5, prefix+'choice_pending_v1': 1, prefix+'notice_pending_v1': 1, prefix+'progress_event_v1': 1})
    execute(effects[prefix+'monthly_v1'])
    assert country['variables'][prefix+'target_v1'] is state and country['variables'][prefix+'months_v1'] == 0
    assert prefix+'route_v1' not in country['variables'] and prefix+'choice_pending_v1' not in country['variables'] and prefix+'notice_pending_v1' not in country['variables']
    assert prefix+'progress_event_v1' in country['variables'] and not queued
    lost = state
    replacement = dict(state, state_region='s:STATE_FLORIDA', variables={}, modifiers=set())
    country['states'] = [replacement]; lost['owner'] = {'country_definition': 'cd:CAN'}
    execute(effects[prefix+'monthly_v1'])
    assert country['variables'][prefix+'target_v1'] is replacement, 'Recover to an owned state after losing the previous target'
    state = reset(); country['variables'][prefix+'complete_v1'] = 1; execute(recover)
    assert country['journals'] == {union}
    for tag, revolutionary in [('USA', 'no'), ('CAN', 'no'), ('ZZZGEORGIA', 'yes')]:
        reset(tag); country['is_revolutionary'] = revolutionary; execute(recover)
        assert not country['journals'] and not country['variables']

    # Execute the actual formation cleanup branch even when the target reference has already vanished.
    reset('USA'); country['variables'].update({prefix+'months_v1': 5, prefix+'choice_pending_v1': 1, prefix+'complete_v1': 1, prefix+'progress_event_v1': 1})
    formation = one(actions['ffpa_na_on_country_formed_v1'], 'effect')
    cleanup = next(v for k, op, v in entries(formation) if isinstance(v, list) and fields(v, prefix+'cleanup_v1'))
    execute(['if', '=', cleanup])
    assert country['variables'] == {prefix+'complete_v1': 1, prefix+'progress_event_v1': 1}
    # Every NA event dispatch requests a popup, and the old default options still clear pending tickets.
    source = '\n'.join((ROOT/p).read_text() for p in ('common/scripted_effects/ffpa_north_american_effects.txt', 'common/scripted_buttons/ffpa_north_american_buttons.txt'))
    import re
    dispatches = re.findall(r'trigger_event = \{ id = (ffpa_na_flavor\.\d+) days = 1 popup = yes \}', source)
    assert set(dispatches) == {f'ffpa_na_flavor.{n}' for n in range(1, 6)}
    for event, flag in [(1, prefix+'choice_pending_v1'), (3, 'ffpa_na_union_proposal_v1')]:
        option = next(o for o in fields(events[f'ffpa_na_flavor.{event}'], 'option') if fields(o, 'default_option'))
        assert flag in one(option, 'if'), 'Default option must keep its pending cleanup'
    print('PASS: 15 predecessor identities, Georgia activation/recovery, preserved projects, empty/stale/fallback selection, lost-target cleanup, completion/revolution/USA exclusions and five explicit popups.')
    print('NOT TESTED: native ordered selection, JE activation timing, event delivery/UI or save reload.')


if __name__ == '__main__': main()
