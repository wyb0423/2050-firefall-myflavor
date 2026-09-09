"""Exercise the actual political effect/trigger subset; not an engine simulation."""
from copy import deepcopy
from check_north_america_preflight import ROOT, definitions, fields, one
from check_cmf_presentation import entries
from validate_localization import parse as localization

P = 'ffpa_usa_political_'


def main():
    effects = definitions(ROOT/'common/scripted_effects/ffpa_north_american_effects.txt')
    triggers = definitions(ROOT/'common/scripted_triggers/ffpa_north_american_triggers.txt')
    events = definitions(ROOT/'events/ffpa_american_political_events.txt')
    je = definitions(ROOT/'common/journal_entries/ffpa_north_american_journal_entries.txt')['je_ffpa_usa_federal_settlement_v1']
    state = {}; expiry = {}; rewards = []; queue = []; scope = {}

    def value(v):
        if v.startswith('var:'): return state.get(v[4:], -999)
        if v.startswith('scope:'): return scope[v[6:]]
        try: return float(v)
        except ValueError: return v

    def subst(block, args):
        return [subst(v,args) if isinstance(v,list) else args.get(v[1:-1],v) if v.startswith('$') and v.endswith('$') else v for v in block]

    def condition(block):
        result=[]
        for k,op,v in entries(block):
            if k == 'NOT': result.append(not condition(v))
            elif k == 'OR': result.append(any(condition([a,b,c]) for a,b,c in entries(v)))
            elif k in triggers:
                test=condition(subst(triggers[k],dict((a,c) for a,b,c in entries(v)))) if isinstance(v,list) else condition(triggers[k])
                result.append(test if isinstance(v,list) or v=='yes' else not test)
            elif k == 'has_variable': result.append(v in state)
            elif k == 'always': result.append(v=='yes')
            else:
                actual=value(k) if k.startswith('var:') else state[k]; wanted=value(v)
                result.append({'=':lambda:actual==wanted,'>=':lambda:actual>=wanted,'<':lambda:actual<wanted}[op]())
        return all(result)

    def execute(block):
        taken=False
        for k,op,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if': taken=False
                if not taken and (k=='else' or condition(one(v,'limit'))):
                    taken=True
                    execute([x for a,b,c in entries(v) if a!='limit' for x in (a,b,c)])
            elif k in effects: execute(effects[k])
            elif k=='set_variable':
                if isinstance(v,str): state[v]=1
                else:
                    name=one(v,'name');state[name]=value(fields(v,'value')[0]) if fields(v,'value') else 1
                    if fields(v,'months'):expiry[name]=int(one(v,'months'))
            elif k=='change_variable':state[one(v,'name')]+=value(one(v,'add'))
            elif k=='remove_variable':state.pop(v,None);expiry.pop(v,None)
            elif k=='add_modifier':rewards.append((one(v,'name'),fields(v,'years')))
            elif k=='trigger_event':queue.append(one(v,'id'))
            elif k=='save_scope_value_as':scope[one(v,'name')]=value(one(v,'value'))
            elif k.startswith('je:'): pass  # UI mirror has no authority over progress.
            elif k in ('name','default_option','ai_chance'):pass
            else:raise AssertionError((k,op,v))

    def reset():
        state.clear();expiry.clear();rewards.clear();queue.clear();scope.clear()
        state.update(country_definition='cd:USA',is_revolutionary='no',government_legitimacy=40,bureaucracy=0)
        execute(effects[P+'initialize_v1'])

    def month():
        for k in list(expiry):
            expiry[k]-=1
            if expiry[k]<=0:expiry.pop(k);state.pop(k,None)
        execute(effects[P+'monthly_v1'])

    def choose(stage,number):
        event=events[f'ffpa_usa_flavor.{stage+2}']
        assert condition(one(event,'trigger'))
        execute(one(event,'immediate'))
        execute(fields(event,'option')[number])

    # Actual minimum spacing, no duplicate initialization and no replay rewards.
    reset(); execute(effects[P+'initialize_v1']);assert queue==['ffpa_usa_flavor.1']
    month()
    for stage in range(4):
        choose(stage,0)
        count=len(rewards);execute(fields(events[f'ffpa_usa_flavor.{stage+2}'],'option')[1]);assert len(rewards)==count
        if stage<3:
            for _ in range(5):month();assert P+'pending_v1' not in state
            month();assert P+'pending_v1' in state
    assert len(rewards)==4 and rewards[2][1]==['5']
    for _ in range(11):month()
    assert not condition(one(je,'complete'))
    # Eleven good months cannot compensate for a single unhealthy observation.
    state['government_legitimacy']=39;month();assert state[P+'months_v1']==0
    state['government_legitimacy']=40
    for _ in range(11):month()
    state['bureaucracy']=-1;month();assert state[P+'months_v1']==0
    state['bureaucracy']=0
    for _ in range(12):month()
    assert condition(one(je,'complete'));execute(one(je,'on_complete'))
    before=deepcopy((state,rewards,queue));execute(effects[P+'initialize_v1']);execute(one(je,'on_complete'))
    assert (state,rewards,queue)==before
    # Deferral never auto-spams. An invalidated old event cannot choose a fresh meeting.
    reset();month();choose(0,2)
    for _ in range(12):month()
    assert queue.count('ffpa_usa_flavor.2')==1
    execute(effects[P+'convene_v1']);event=events['ffpa_usa_flavor.2'];execute(one(event,'immediate'))
    old_scope=scope.copy();state['country_definition']='cd:CAN';execute(effects[P+'suspend_v1'])
    execute(fields(event,'option')[0]);assert not rewards
    state['country_definition']='cd:USA';execute(effects[P+'initialize_v1']);execute(effects[P+'convene_v1'])
    execute(fields(event,'option')[0]);assert not rewards and scope==old_scope
    choose(0,1);assert state[P+'works_v1']==2
    # All eight options write their own persistent choice; only property costs expire.
    for stage,choice in enumerate(('works','titles','representation','oversight')):
        for number in (0,1):
            reset();state[P+'stage_v1']=stage;execute(effects[P+'convene_v1']);choose(stage,number)
            assert state[P+choice+'_v1']==number+1 and state[P+'stage_v1']==stage+1
            assert len(rewards)==(2 if stage==1 else 0 if stage==3 else 1)
    for lang in ('english','simp_chinese'):
        path=ROOT/f'localization/{lang}/ffpa_north_american_l_{lang}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        loc=localization(path.read_text(encoding='utf-8-sig'),lang)
        for event in events.values():
            for f in ('title','desc','flavor'): assert one(event,f) in loc
            for option in fields(event,'option'):assert one(option,'name') in loc
    assert not fields(je,'timeout')
    print('PASS: actual-script six-month spacing, twelve-month reset/boundaries, all choices, deferral, stale events, identity suspension and idempotent completion; bilingual event keys.')
    print('NOT TESTED: engine activation/pulse ordering, native event expiry, UI scopes, AI or save reload. Charter is checked separately; permanent governance is not yet implemented.')


if __name__=='__main__':main()
