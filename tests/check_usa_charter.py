"""Execute the actual charter script subset and audit its installed-source rule generation.

Requires --game-root GAME --upstream CMF --upstream TECHRES --upstream FIREFALL.
This does not emulate native law activation callbacks or engine event scheduling.
"""
import argparse
import copy
import itertools
from pathlib import Path
import sys
from check_north_america_preflight import ROOT, definitions, fields, one
from check_cmf_presentation import entries
sys.path.insert(0,str(ROOT/'tools'))
from generate_usa_charter_rules import CHOICES, load_laws, render

P='ffpa_usa_charter_'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root',type=Path,required=True)
    parser.add_argument('--upstream',type=Path,action='append',default=[])
    args=parser.parse_args()
    laws=load_laws([args.game_root,*args.upstream,ROOT])
    for path,text in render(laws).items():assert (ROOT/path).read_text()==text,path
    effects=definitions(ROOT/'common/scripted_effects/ffpa_north_american_charter.txt')
    triggers=definitions(ROOT/'common/scripted_triggers/ffpa_north_american_charter.txt')
    triggers.update(definitions(ROOT/'common/scripted_triggers/ffpa_north_american_charter_rules.txt'))
    events=definitions(ROOT/'events/ffpa_american_political_events.txt')
    state={}; context={}; scope={}; current={}; expiry={}; activated=[]; rewards=[]; queue=[]

    def value(v):
        if v.startswith('var:'):return state.get(v[4:],-999)
        if v.startswith('scope:'):return scope[v[6:]]
        try:return float(v)
        except ValueError:return v

    def has(k,variant):
        for law in current.values():
            if law==k:return True
            while variant and fields(laws[law],'parent'):
                law=one(laws[law],'parent')
                if law==k:return True
        return False

    def subst(block,params):return [subst(v,params) if isinstance(v,list) else params.get(v[1:-1],v) if v.startswith('$') and v.endswith('$') else v for v in block]

    def cond(block):
        result=[]
        for k,op,v in entries(block):
            if k in ('NOT','AND'):result.append(not cond(v) if k=='NOT' else cond(v))
            elif k=='OR':result.append(any(cond([a,b,c]) for a,b,c in entries(v)))
            elif k=='trigger_if':result.append(not cond(one(v,'limit')) or cond([x for a,b,c in entries(v) if a!='limit' for x in (a,b,c)]))
            elif k=='custom_tooltip':result.append(cond([x for a,b,c in entries(v) if a!='text' for x in (a,b,c)]))
            elif k in triggers:
                result.append(cond(subst(triggers[k],{a:c for a,b,c in entries(v)})) if isinstance(v,list) else cond(triggers[k])==(v=='yes'))
            elif k=='has_variable':result.append(v in state)
            elif k=='exists':assert v=='currently_enacting_law';result.append(context['enacting'])
            elif k in ('has_law','has_law_or_variant'):result.append(has(v.removeprefix('law_type:'),k=='has_law_or_variant'))
            elif k=='has_government_type':assert v=='gov_chartered_company';result.append(context['company'])
            elif k=='any_subject_or_below':result.append(context['crownland'])
            elif k=='always':result.append(v=='yes')
            else:
                actual=value(k) if k.startswith('var:') else context[k];want=value(v)
                result.append({'=':lambda:actual==want,'>':lambda:actual>want}[op]())
        return all(result)

    def execute(block):
        taken=False
        for k,op,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or cond(one(v,'limit'))):
                    taken=True;execute([x for a,b,c in entries(v) if a!='limit' for x in (a,b,c)])
            elif k in effects:execute(effects[k])
            elif k=='set_variable':
                if isinstance(v,str):state[v]=1
                else:
                    name=one(v,'name');state[name]=value(fields(v,'value')[0]) if fields(v,'value') else 1
                    if fields(v,'months'):expiry[name]=int(one(v,'months'))
                    if fields(v,'years'):expiry[name]=12*int(one(v,'years'))
            elif k=='change_variable':state[one(v,'name')]+=value(one(v,'add'))
            elif k=='remove_variable':state.pop(v,None);expiry.pop(v,None)
            elif k=='trigger_event':queue.append(one(v,'id'))
            elif k=='save_scope_value_as':scope[one(v,'name')]=value(one(v,'value'))
            elif k=='add_modifier':rewards.append((one(v,'name'),one(v,'months')))
            elif k=='activate_law':
                law=v.removeprefix('law_type:');activated.append(law);current[one(laws[law],'group')]=law
                execute(effects[P+'enactment_ended_v1'])  # Even unexpected re-entry cannot renew a closed charter.
            elif k in ('name','trigger','custom_tooltip','default_option','ai_chance'):pass
            else:raise AssertionError((k,op,v))

    def reset():
        for d in (state,context,scope,current,expiry):d.clear()
        activated.clear();rewards.clear();queue.clear()
        context.update(country_definition='cd:USA',is_revolutionary='no',is_subject='no',enacting=False,company=False,crownland=False)
        for law in ('law_monarchy','law_autocracy','law_traditionalism','law_national_supremacy'):
            current[one(laws[law],'group')]=law
        execute(effects[P+'initialize_v1'])

    def tick():
        for k in list(expiry):
            expiry[k]-=1
            if expiry[k]<=0:expiry.pop(k);state.pop(k,None)
        execute(effects[P+'monthly_v1'])

    def draft(values=(1,1,1)):
        execute(effects[P+'open_v1'])
        for stage,choice in enumerate(values):
            event=events[f'ffpa_usa_flavor.{stage+6}'];assert cond(one(event,'trigger'))
            execute(one(event,'immediate'))
            opts=fields(event,'option');index=choice-1 if choice else len(opts)-2
            execute(opts[index]);assert not activated and not rewards
            tick()
        execute(one(events['ffpa_usa_flavor.9'],'immediate'))

    def selection(g,p,e):
        state[P+'stage_v1']=3
        for group,n in zip(CHOICES,(g,p,e)):state[P+group+'_v1']=n

    reset();execute(effects[P+'initialize_v1']);assert not queue and expiry[P+'deadline_v1']==60
    draft((2,1,1));assert cond(triggers[P+'can_sign_v1'])
    execute(effects[P+'sign_v1'])
    assert activated==['law_interventionism','law_universal_suffrage','law_parliamentary_republic']
    assert rewards==[(P+'transition_v1','24')]
    snapshot=copy.deepcopy((state,current,rewards,activated,expiry));execute(effects[P+'sign_v1']);execute(effects[P+'initialize_v1']);assert (state,current,rewards,activated,expiry)==snapshot
    # All combinations preserve the explicit no-op path and safely validate changed choices.
    cases=0
    for g,p,e in itertools.product(range(3),range(4),range(4)):
        reset();selection(g,p,e)
        expected=not (g==2 and p==0)
        assert cond(triggers[P+'can_sign_v1'])==expected,(g,p,e)
        cases+=1
    for law,values in [('law_subjecthood',(1,1,1)),('law_millet_system',(1,1,1)),('law_chiefdom',(0,1,1)),('law_command_economy',(1,1,0)),('law_cooperative_ownership',(1,1,0)),('law_collectivized_agriculture',(1,1,3)),('law_serfdom',(1,1,2)),('law_manorialism',(1,1,2)),('law_sakoku',(1,1,3))]:
        reset();current[one(laws[law],'group')]=law;selection(*values)
        assert not cond(triggers[P+'can_sign_v1']),law
    reset();current['lawgroup_land_reform']='law_serfdom';selection(1,1,3);assert cond(triggers[P+'can_sign_v1'])
    for blocker in ('crownland','company','enacting'):
        reset();selection(1,1,1);context[blocker]=True;assert not cond(triggers[P+'can_sign_v1'])
    reset();draft((0,0,0));execute(effects[P+'sign_v1']);assert not activated and not rewards and P+'closed_v1' in state
    reset();draft();execute(fields(events['ffpa_usa_flavor.9'],'option')[2]);assert not activated and not rewards and P+'abandoned_v1' in state
    reset();execute(effects[P+'open_v1']);event=events['ffpa_usa_flavor.6'];execute(one(event,'immediate'));execute(fields(event,'option')[-1])
    for _ in range(4):tick()
    assert queue==['ffpa_usa_flavor.6']
    execute(effects[P+'open_v1']);execute(fields(event,'option')[0]);assert state[P+'stage_v1']==0  # stale ticket
    # A complete draft holds only the current enactment; ending it grants one bounded response period.
    reset();context['enacting']=True;draft();assert P+'hold_v1' in state
    state.pop(P+'deadline_v1');expiry.pop(P+'deadline_v1');tick();assert P+'closed_v1' not in state
    execute(effects[P+'enactment_ended_v1']);context['enacting']=False
    assert expiry[P+'grace_v1']==3 and P+'hold_v1' not in state
    context['enacting']=True;execute(effects[P+'enactment_started_v1']);execute(effects[P+'enactment_ended_v1']);assert expiry[P+'grace_v1']==3
    for _ in range(3):tick()
    assert P+'closed_v1' in state and not activated
    reset();state.pop(P+'deadline_v1');context['enacting']=True;execute(effects[P+'enactment_started_v1']);tick();assert P+'closed_v1' in state
    # Returned drafts do not retain submission protection or alter the fixed deadline.
    reset();context['enacting']=True;draft();deadline=expiry[P+'deadline_v1'];execute(fields(events['ffpa_usa_flavor.9'],'option')[1])
    assert state[P+'stage_v1']==0 and P+'hold_v1' not in state and expiry[P+'deadline_v1']==deadline
    source=(ROOT/'common/scripted_effects/ffpa_north_american_charter.txt').read_text()
    assert source.count('activate_law =')==8 and 'start_enactment' not in source and 'add_technology' not in source
    assert 'every_country' not in source and 'every_pop' not in source
    print(f'PASS: {cases} joint drafts; structural/variant conflicts, eight-law whitelist, no-op/24-month cost, stale ticket, deferral, expiry, fixed-draft enactment grace and no replay. Generated source rules match.')
    print('NOT TESTED: native activation order/callbacks, law-variant inheritance, events/UI, AI, save reload or Launcher load order.')


if __name__=='__main__':main()
