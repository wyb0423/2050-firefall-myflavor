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
    effects.update(definitions(ROOT/'common/scripted_effects/ffpa_north_american_effects.txt'))
    triggers=definitions(ROOT/'common/scripted_triggers/ffpa_north_american_charter.txt')
    triggers.update(definitions(ROOT/'common/scripted_triggers/ffpa_north_american_charter_rules.txt'))
    triggers.update(definitions(ROOT/'common/scripted_triggers/ffpa_north_american_triggers.txt'))
    events=definitions(ROOT/'events/ffpa_american_political_events.txt')
    journals=definitions(ROOT/'common/journal_entries/ffpa_north_american_journal_entries.txt')
    actions=definitions(ROOT/'common/on_actions/ffpa_north_american_on_actions.txt')
    state={}; context={}; scope={}; current={}; expiry={}; activated=[]; rewards=[]; queue=[]; errors=[]; active_journals=set()

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
            elif k=='has_journal_entry':result.append(v in active_journals)
            elif k=='any_scope_state':
                assert one(v,'ffpa_na_is_mainland_state_v1')=='yes'
                result.append(context['mainland'])
            elif k=='exists':
                assert v=='currently_enacting_law' or v.startswith('var:')
                result.append(context['enacting'] if v=='currently_enacting_law' else v[4:] in state)
            elif k in ('has_law','has_law_or_variant'):result.append(has(v.removeprefix('law_type:'),k=='has_law_or_variant'))
            elif k=='has_government_type':assert v=='gov_chartered_company';result.append(context['company'])
            elif k=='any_subject_or_below':result.append(context['crownland'])
            elif k=='always':result.append(v=='yes')
            else:
                actual=value(k) if k.startswith('var:') else context[k];want=value(v)
                result.append({'=':lambda:actual==want,'>':lambda:actual>want,'>=':lambda:actual>=want,'<':lambda:actual<want}[op]())
        return all(result)

    def execute(block):
        taken=False
        for k,op,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or cond(one(v,'limit'))):
                    taken=True;execute([x for a,b,c in entries(v) if a!='limit' for x in (a,b,c)])
            elif k in effects:execute(effects[k])
            elif k=='hidden_effect':execute(v)
            elif k=='set_variable':
                if isinstance(v,str):state[v]=1
                else:
                    name=one(v,'name');state[name]=value(fields(v,'value')[0]) if fields(v,'value') else 1
                    if fields(v,'months'):expiry[name]=int(one(v,'months'))
                    if fields(v,'years'):expiry[name]=12*int(one(v,'years'))
            elif k=='change_variable':state[one(v,'name')]+=value(one(v,'add'))
            elif k=='remove_variable':state.pop(v,None);expiry.pop(v,None)
            elif k=='trigger_event':
                assert one(v,'popup')=='yes'
                queue.append(one(v,'id'))
            elif k=='add_journal_entry':
                journal=one(v,'type');assert journal not in active_journals
                active_journals.add(journal);execute(one(journals[journal],'immediate'))
            elif k.startswith('je:'):pass  # Native UI mirror, not a progress source.
            elif k=='ordered_state':pass  # Fixture has no neighbouring country, so native selection is empty.
            elif k=='save_scope_value_as':scope[one(v,'name')]=value(one(v,'value'))
            elif k=='add_modifier':rewards.append((one(v,'name'),one(v,'months')))
            elif k=='activate_law':
                law=v.removeprefix('law_type:');activated.append(law)
                if law not in context['blocked_laws']:current[one(laws[law],'group')]=law
                execute(effects[P+'enactment_ended_v1'])  # Even unexpected re-entry cannot renew a closed charter.
                # A synchronous activation callback must not sign or charge a second time.
                execute(effects[P+'sign_v1'])
            elif k=='error_log':errors.append(v)
            elif k in ('name','trigger','custom_tooltip','default_option','ai_chance','show_as_unavailable'):pass
            else:raise AssertionError((k,op,v))

    def reset():
        for d in (state,context,scope,current,expiry):d.clear()
        activated.clear();rewards.clear();queue.clear();errors.clear();active_journals.clear()
        context.update(country_definition='cd:USA',is_revolutionary='no',is_subject='no',enacting=False,company=False,crownland=False,blocked_laws=set(),mainland=True,government_legitimacy=40,bureaucracy=0)
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
    # The option and effect must reject the same stale event, rather than offering a silent no-op.
    sign_option=fields(events['ffpa_usa_flavor.9'],'option')[0]
    reset();draft();assert cond(one(sign_option,'trigger'))
    scope['ffpa_usa_charter_event_serial']-=1
    assert not cond(one(sign_option,'trigger'))
    execute(sign_option);assert not activated and not rewards
    assert one(one(sign_option,'show_as_unavailable'),'always')=='yes'
    # Failed native activations must leave a retryable draft, not a signed/charged dead end.
    for blocked in ({'law_interventionism'}, {'law_interventionism','law_universal_suffrage','law_presidential_republic'}):
        reset();draft();deadline=expiry[P+'deadline_v1'];context['blocked_laws']=blocked
        execute(sign_option)
        assert P+'signed_v1' not in state and P+'closed_v1' not in state and not rewards
        assert P+'pending_v1' not in state and P+'applying_v2' not in state
        assert P+'apply_failed_v2' in state and errors and expiry[P+'deadline_v1']==deadline
        before=current.copy();context['blocked_laws']=set();activated.clear()
        execute(effects[P+'open_v1']);execute(one(events['ffpa_usa_flavor.9'],'immediate'));execute(sign_option)
        assert P+'signed_v1' in state and P+'closed_v1' in state and P+'apply_failed_v2' not in state
        assert rewards==[(P+'transition_v1','24')]
        assert all(before.get(one(laws[law],'group'))!=law for law in activated), 'Retry must skip laws already applied'
    # After a wholly failed attempt, a replacement no-op draft still has no cost.
    reset();draft();context['blocked_laws']={'law_interventionism','law_universal_suffrage','law_presidential_republic'}
    execute(sign_option);selection(0,0,0);execute(effects[P+'open_v1'])
    execute(one(events['ffpa_usa_flavor.9'],'immediate'));execute(sign_option);assert not rewards
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
    # Real formation/JE effects, with native journal activation represented by its documented immediate callback.
    formed=one(actions['ffpa_na_on_country_formed_v1'],'effect')
    monthly=one(actions['ffpa_usa_charter_monthly_action_v1'],'effect')
    political='ffpa_usa_political_'
    expected_journals={'je_ffpa_usa_federal_settlement_v1','je_ffpa_na_union_agenda_v1'}
    for je_first in (False,True):
        reset();state.clear();expiry.clear()
        if je_first:execute(effects['ffpa_usa_ensure_journals_v2'])
        execute(formed)
        assert active_journals==expected_journals
        assert queue.count('ffpa_usa_flavor.1')==queue.count('ffpa_usa_flavor.6')==1
        execute(formed);assert queue.count('ffpa_usa_flavor.6')==1 and expiry[P+'deadline_v1']==60
    # Old USA saves recover absent journals without requesting a charter or replaying political choices.
    reset();state[political+'stage_v1']=2;state[political+'months_v1']=0;state[political+'serial_v1']=4
    state[political+'works_v1']=1;state[political+'titles_v1']=2
    execute(monthly);before=copy.deepcopy((state,expiry,queue,rewards))
    assert active_journals==expected_journals and not queue and not rewards
    execute(monthly);assert (state,expiry,queue,rewards)==before
    active_journals.clear();state[political+'complete_v1']=1
    execute(monthly);assert active_journals=={'je_ffpa_na_union_agenda_v1'}
    for tag,revolution in [('cd:CAN','no'),('cd:USA','yes')]:
        reset();context.update(country_definition=tag,is_revolutionary=revolution)
        execute(effects['ffpa_usa_ensure_journals_v2']);assert not active_journals and not queue
    reset();context['mainland']=False;execute(effects['ffpa_usa_ensure_journals_v2'])
    assert active_journals=={'je_ffpa_usa_federal_settlement_v1'}
    source=(ROOT/'common/scripted_effects/ffpa_north_american_charter.txt').read_text()
    assert source.count('activate_law =')==8 and 'start_enactment' not in source and 'add_technology' not in source
    assert 'every_country' not in source and 'every_pop' not in source
    print(f'PASS: {cases} joint drafts; structural/variant conflicts, eight-law whitelist, verified settlement, failed/partial activation retries, callback re-entry, stale button, no-op/24-month cost, deferral, expiry and no replay. Generated source rules match.')
    print('PASS: formation before/after JE initialization, explicit event popups, missing-journal recovery, completed/foreign/revolutionary exclusions and preserved old-save choices.')
    print('NOT TESTED: native activation order/callbacks, law-variant inheritance, events/UI, AI, save reload or Launcher load order.')


if __name__=='__main__':main()
