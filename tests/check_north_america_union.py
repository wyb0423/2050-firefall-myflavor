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
    for n, options in ((3, 2), (4, 3), (5, 1)):
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
    check_lifecycle(effects, triggers, events, modifiers)
    print('PASS: province snapshot ownership, claim guards, fixed deadlines/cooldowns, guarded full rewards, event localization and bounded AI scope.')
    print('NOT TESTED: engine macros/scopes, selectors, callback timing, claim regrants, AI choices, state merge inheritance or save reload.')

def check_lifecycle(effects, triggers, events, modifiers):
    """Run actual control flow; native map queries/callbacks are supplied as fixture facts."""
    import operator
    from check_cmf_presentation import entries
    triggers.update(definitions(ROOT/'common/scripted_triggers/ffpa_north_american_union_provinces.txt'))
    buttons = definitions(ROOT/'common/scripted_buttons/ffpa_north_american_buttons.txt')
    journal = definitions(ROOT/'common/journal_entries/ffpa_north_american_journal_entries.txt')['je_ffpa_na_union_agenda_v1']
    regions = fields(triggers['ffpa_usa_union_mainland_owned_v1'], 'owns_entire_state_region')
    expected = fields(one(triggers['ffpa_na_is_mainland_state_v1'], 'OR'), 'state_region')
    assert set(regions) == {s[2:] for s in expected} and len(regions) == 49
    assert not {'STATE_ALASKA', 'STATE_HAWAII', 'STATE_PUERTO_RICO'} & set(regions)
    assert one(modifiers['ffpa_usa_union_integration_v1'], 'state_incorporation_speed_mult') == '0.25'
    P = 'ffpa_na_union_'; benefit = 'ffpa_usa_union_integration_v1'; finished = 'ffpa_usa_union_complete_v1'
    variables = {}; scopes = {}; facts = {}; mods = {}; queue = []; grants = []; candidates = []; owned = set(); journals = set()
    snapshot = triggers['ffpa_na_union_snapshot_owned_v2']
    branches = fields(snapshot,'trigger_if') + fields(snapshot,'trigger_else_if')
    branch = next(b for b in branches if one(one(b,'limit'),'var:'+P+'region_v1') == 's:STATE_GEORGIA')
    fixture_provinces = [one(one(b,'NOT'),'has_variable') for b in fields(branch,'OR')][:3]
    assert len(fixture_provinces) == 3
    compare = {'=': operator.eq, '!=': operator.ne, '>': operator.gt, '>=': operator.ge, '<': operator.lt, '<=': operator.le}

    def body(block, *exclude):
        return [x for k,o,v in entries(block) if k not in exclude for x in (k,o,v)]

    def value(v, ctx='ROOT', prev=None):
        if v == 'root': return 'ROOT'
        if v == 'this': return ctx
        if v == 'prev': return prev
        if v.startswith('root.'): return value(v[5:], 'ROOT', prev)
        if v.startswith('var:'): return variables.get(v[4:])
        if v.startswith('scope:'): return scopes.get(v[6:])
        if v == 'state_region': return 's:STATE_GEORGIA'
        if v.startswith('p:'):
            flag=P+'p_'+v[2:].split('.')[0]+'_v1'
            if flag not in fixture_provinces: return 'FOREIGN'
            i=fixture_provinces.index(flag)
            return None if i >= facts['seen'] else 'ROOT' if i < facts['owned'] else 'FOREIGN'
        if v in facts: return facts[v]
        try: return float(v)
        except ValueError: return v

    def cond(block, ctx='ROOT'):
        taken = False
        for k,o,v in entries(block):
            if k in ('AND', 'NOT'): ok = cond(v,ctx) if k == 'AND' else not cond(v,ctx)
            elif k == 'OR': ok = any(cond([a,b,c],ctx) for a,b,c in entries(v))
            elif k == 'custom_tooltip': ok = cond(body(v,'text'),ctx)
            elif k in ('trigger_if','trigger_else_if','trigger_else'):
                if k == 'trigger_if': taken=False
                if not taken and (k == 'trigger_else' or cond(one(v,'limit'),ctx)):
                    taken=True;ok=cond(body(v,'limit'),ctx)
                else: ok=True
            elif k == 'ffpa_na_union_candidate_v1': ok = (ctx in candidates) == (v == 'yes')
            elif k == 'ffpa_usa_political_eligible_v1': ok = False  # Unrelated political journal is complete.
            elif k in triggers: ok = cond(triggers[k],ctx) == (v == 'yes')
            elif k == 'has_variable': ok = v in variables
            elif k == 'has_modifier': ok = v in mods
            elif k == 'has_journal_entry': ok = v in journals
            elif k == 'exists': ok = value(v,ctx) is not None
            elif k == 'always': ok = v == 'yes'
            elif k == 'owns_entire_state_region': ok = v in owned
            elif k == 'any_scope_state':
                if ctx == 'ROOT': ok = facts['mainland']  # Country owns a mainland state.
                else: ok = ctx == 's:STATE_GEORGIA' and any(cond(v,s) for s in candidates)
            elif isinstance(v,list):
                target = value(k,ctx)
                ok = target is not None and cond(v,target)
            else:
                a,b = value(k,ctx),value(v,ctx)
                ok = a is not None and b is not None and compare[o](a,b)
            if not ok: return False
        return True

    def execute(block, ctx='ROOT', prev=None):
        taken = False
        for k,o,v in entries(block):
            if k in ('if','else_if','else'):
                if k == 'if': taken = False
                if not taken and (k == 'else' or cond(one(v,'limit'),ctx)):
                    taken = True; execute(body(v,'limit'),ctx,prev)
            elif k == 'ffpa_na_union_visit_region_v1':
                # Native province ownership is external to the interpreter; execute actual caller ordering.
                mode = variables[P+'pass_v1']
                if mode == 1:
                    variables[P+'total_v1'] = 3
                    variables.update({p:1 for p in fixture_provinces})
                elif mode == 2: variables.update({P+'seen_v1':facts['seen'], P+'owned_v1':facts['owned']})
                elif mode == 3:
                    for p in fixture_provinces: variables.pop(p,None)
                elif mode == 4: grants.append('receiving states')
            elif k in effects: execute(effects[k],ctx,prev)
            elif k == 'set_variable':
                variables[v if isinstance(v,str) else one(v,'name')] = 1 if isinstance(v,str) or not fields(v,'value') else value(one(v,'value'),ctx,prev)
            elif k == 'change_variable': variables[one(v,'name')] += value(one(v,'add'),ctx,prev)
            elif k == 'remove_variable': variables.pop(v,None)
            elif k == 'add_modifier':
                name=one(v,'name');mods[name]=fields(v,'years');grants.append(name)
            elif k == 'remove_modifier': mods.pop(v,None)
            elif k == 'ordered_state':
                selected = [s for s in candidates if cond(one(v,'limit'),s)]
                index=int(value(one(v,'position'),ctx));selected=selected[index:index+1]
                for s in selected: execute(body(v,'limit','position','order_by','check_range_bounds'),s,ctx)
            elif k == 'save_scope_as': scopes[v] = ctx
            elif k == 'save_scope_value_as': scopes[one(v,'name')] = value(one(v,'value'),ctx)
            elif k in ('add_claim','remove_claim'): pass  # Native claim provenance is covered by the static contract above.
            elif k == 'trigger_event': queue.append(one(v,'id'))
            elif k == 'add_journal_entry':
                assert one(v,'type') not in journals;journals.add(one(v,'type'));execute(one(journal,'immediate'))
            elif k == 'every_scope_state': pass  # Only clears native receiving-state scratch markers.
            elif k in ('name','trigger','default_option','ai_chance','show_as_unavailable'): pass
            elif isinstance(v,list): execute(v,value(k,ctx),ctx)
            else: raise AssertionError((k,o,v))

    def reset(tag='USA', targets=()):
        for d in (variables,scopes,facts,mods):d.clear()
        queue.clear();grants.clear();candidates[:]=targets;owned.clear();journals.clear()
        facts.update(country_definition='cd:'+tag,is_revolutionary='no',is_ai='no',is_at_war='no',is_diplomatic_play_committed_participant='no',mainland=True,seen=3,owned=0)
        journals.add('je_ffpa_na_union_agenda_v1')
        execute(effects[P+'initialize_v1'])

    def active():
        reset();variables.update({P+'status_v1':1,P+'total_v1':3,P+'deadline_v1':1,P+'region_v1':'s:STATE_GEORGIA'})
        variables.update({p:1 for p in fixture_provinces})
        grants.clear()

    def pulse(): execute(effects[P+'monthly_v1'])
    def possible(button): return cond(one(buttons[P+button], 'possible'))

    reset();assert not possible('next_button_v1') and not possible('propose_button_v1')
    reset(targets=['a']);assert variables[P+'target_v1']=='a'
    assert not possible('next_button_v1') and possible('propose_button_v1')
    variables.pop(P+'target_v1');assert possible('next_button_v1');pulse();assert variables[P+'target_v1']=='a'
    candidates[:]=['b'];pulse();assert variables[P+'target_v1']=='b'
    candidates[:]=[];pulse();assert P+'target_v1' not in variables
    reset(targets=['a','b']);assert possible('next_button_v1')
    execute(one(buttons[P+'next_button_v1'],'effect'));assert variables[P+'target_v1']=='b'
    variables[P+'cooldown_v1']=1;assert not possible('next_button_v1') and not possible('propose_button_v1')
    reset(targets=['a']);facts['is_at_war']='yes';assert not possible('propose_button_v1')
    facts['is_at_war']='no';execute(one(buttons[P+'propose_button_v1'],'effect'))
    proposal=events['ffpa_na_flavor.3'];execute(one(proposal,'immediate'))
    accept=fields(proposal,'option')[0];assert cond(one(accept,'trigger'))
    assert not possible('next_button_v1') and not possible('propose_button_v1')
    candidates.clear();assert not cond(one(accept,'trigger'));execute(accept);assert variables[P+'status_v1']==0
    candidates[:]=['a'];old=scopes['ffpa_na_union_event_serial'];variables[P+'serial_v1']+=1
    assert not cond(one(accept,'trigger'));variables[P+'serial_v1']=old
    facts['is_at_war']='yes';assert not cond(one(accept,'trigger'));facts['is_at_war']='no'
    execute(accept);assert variables[P+'status_v1']==1 and P+'deadline_v1' in variables

    # Timely acquisition during war is secured; post-deadline acquisition cannot rescue failure.
    active();facts.update(owned=3,is_at_war='yes');pulse();assert variables[P+'status_v1']==2 and not queue
    variables.pop(P+'deadline_v1');facts['is_at_war']='no';assert possible('reopen_button_v2')
    execute(one(buttons[P+'reopen_button_v2'],'effect'));assert queue==['ffpa_na_flavor.4']
    assert not possible('reopen_button_v2');settlement=events['ffpa_na_flavor.4']
    execute(one(settlement,'immediate'));old=scopes['ffpa_na_union_event_serial']
    variables.pop(P+'reply_cooldown_v2');execute(one(buttons[P+'reopen_button_v2'],'effect'))
    assert not cond(triggers[P+'settlement_valid_v2'])
    execute(fields(settlement,'option')[0]);assert not grants, 'Stale reply cannot pay'
    execute(one(settlement,'immediate'));assert scopes['ffpa_na_union_event_serial']>old
    execute(fields(settlement,'option')[0]);paid=list(grants);execute(fields(settlement,'option')[1])
    assert grants==paid and paid==['ffpa_na_union_dividend_v1','receiving states']
    assert variables[P+'status_v1']==0 and P+'cooldown_v1' in variables and benefit in mods
    active();variables.pop(P+'deadline_v1');facts.update(owned=3,is_at_war='yes');pulse()
    assert variables[P+'status_v1']==1 and P+'withdraw_v1' in variables and not queue
    facts['is_at_war']='no';pulse();assert variables[P+'status_v1']==0 and queue==['ffpa_na_flavor.5']
    active();facts['owned']=3;pulse();assert variables[P+'status_v1']==2
    variables.pop(P+'reply_cooldown_v2');execute(one(settlement,'immediate'))
    facts['owned']=2;assert not possible('reopen_button_v2') and not cond(one(fields(settlement,'option')[0],'trigger'))
    pulse();assert variables[P+'status_v1']==1
    active();facts['seen']=2;pulse();assert variables[P+'status_v1']==0 and not grants

    reset();execute(effects['ffpa_usa_ensure_journals_v2']);execute(effects['ffpa_usa_ensure_journals_v2'])
    assert grants==[benefit], 'Recovery must not stack the active modifier'
    variables[P+'cooldown_v1']=1;pulse();assert benefit in mods
    # Native full-region predicates must all pass, even when there are no actionable targets.
    assert not cond(one(journal,'complete'));owned.update(regions)
    for region in regions:
        owned.remove(region);assert not cond(one(journal,'complete'));owned.add(region)
    for status in (1,2,3):
        variables[P+'status_v1']=status;assert not cond(one(journal,'complete'))
    variables[P+'status_v1']=0;variables[P+'proposal_v1']=1;assert not cond(one(journal,'complete'))
    variables.pop(P+'proposal_v1');assert cond(one(journal,'complete'))
    mods['ffpa_na_union_dividend_v1']=['5'];execute(one(journal,'on_complete'))
    assert finished in variables and benefit not in mods and mods['ffpa_na_union_dividend_v1']==['5']
    journals.clear();execute(effects['ffpa_usa_ensure_journals_v2']);assert not journals and benefit not in mods
    reset();facts['country_definition']='cd:CAN';execute(effects['ffpa_usa_ensure_journals_v2']);assert benefit not in mods
    reset();facts['is_revolutionary']='yes';execute(one(journal,'on_invalid'));assert benefit not in mods
    reset('ZZZGEORGIA');assert benefit not in mods;owned.update(regions);assert not cond(one(journal,'complete'))
    print('PASS: actual union control flow for zero/one/multiple/stale targets, stale replies, recovery, deadline/war, lost land, idempotent rewards, USA-only benefit and terminal ownership.')


if __name__ == '__main__':
    main()
