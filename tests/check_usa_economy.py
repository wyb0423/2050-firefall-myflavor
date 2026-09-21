"""Run the actual USA economic script subset. Not an engine, UI, AI or save-format test."""
from copy import deepcopy
from itertools import product
import math
import operator
from check_north_america_preflight import ROOT, definitions, fields, one
from check_cmf_presentation import entries
from validate_localization import parse as parse_loc

P = 'ffpa_usa_'

def main():
    effects = definitions(ROOT/'common/scripted_effects/ffpa_north_american_economy.txt')
    triggers = definitions(ROOT/'common/scripted_triggers/ffpa_north_american_economy.txt')
    triggers.update(definitions(ROOT/'common/scripted_triggers/ffpa_north_american_triggers.txt'))
    values = definitions(ROOT/'common/script_values/ffpa_north_american_economy.txt')
    journals = definitions(ROOT/'common/journal_entries/ffpa_north_american_economy.txt')
    events = definitions(ROOT/'events/ffpa_american_economic_events.txt')
    mods = definitions(ROOT/'common/static_modifiers/ffpa_north_american_economy.txt')
    actions = definitions(ROOT/'common/on_actions/ffpa_north_american_on_actions.txt')
    buttons = definitions(ROOT/'common/scripted_buttons/ffpa_north_american_economy.txt')
    scopes = {}; queue = []; awards = []; country = {}
    compare = {'=':operator.eq, '>':operator.gt, '>=':operator.ge, '<':operator.lt, '<=':operator.le}

    def body(block, *exclude):
        return [x for k,o,v in entries(block) if k not in exclude for x in (k,o,v)]

    def subst(block, params):
        if isinstance(block,list): return [subst(v,params) for v in block]
        for k,v in params.items(): block=block.replace('$'+k+'$',v)
        return block

    def value(v, ctx, prev=None):
        if isinstance(v,list): return calc(v,ctx)
        if v in values: return calc(values[v],ctx)
        if v=='root': return country
        if v=='prev': return prev
        if v=='this': return ctx
        if v.startswith('this.'): return value(v[5:],ctx,prev)
        if v.startswith('root.'): return value(v[5:],country,prev)
        if v.startswith('var:'): return ctx['variables'].get(v[4:],0)
        if v.startswith('scope:'): return scopes.get(v[6:])
        if v in ctx: return ctx[v]
        try: return float(v)
        except ValueError: return v

    def cond(block, ctx=None):
        if ctx is None: ctx=country
        for k,o,v in entries(block):
            if k=='OR': ok=any(cond([a,b,c],ctx) for a,b,c in entries(v))
            elif k=='NOT': ok=not cond(v,ctx)
            elif k=='AND': ok=cond(v,ctx)
            elif k=='custom_tooltip': ok=cond(body(v,'text'),ctx)
            elif k in triggers:
                ok=cond(subst(triggers[k],{a:c for a,b,c in entries(v)}),ctx) if isinstance(v,list) else cond(triggers[k],ctx)==(v=='yes')
            elif k in ('any_scope_state','any_scope_building','any_company'):
                collection={'any_scope_state':'states','any_scope_building':'buildings','any_company':'companies'}[k]
                ok=any(cond(v,s) for s in ctx.get(collection,[]))
            elif k=='has_variable': ok=v in ctx['variables']
            elif k=='has_journal_entry': ok=v in ctx['journals']
            elif k=='has_modifier': ok=v in ctx['modifiers']
            elif k=='exists': ok=value(v,ctx) is not None
            elif k=='always': ok=v=='yes'
            elif isinstance(v,list): ok=cond(v,value(k,ctx))
            else:
                a,b=value(k,ctx),value(v,ctx)
                ok=(a is b) if isinstance(a,dict) or isinstance(b,dict) else compare[o](a,b)
            if not ok:return False
        return True

    def calc(block,ctx,result=0):
        taken=False
        for k,o,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or cond(one(v,'limit'),ctx)):
                    result=calc(body(v,'limit'),ctx,result);taken=True
            elif k in ('every_scope_state','every_scope_building'):
                for s in ctx['states' if k=='every_scope_state' else 'buildings']:
                    if cond(one(v,'limit'),s):result=calc(body(v,'limit'),s,result)
            elif k=='ceiling':result=math.ceil(result)
            else:
                n=value(v,ctx)
                if k=='value':result=n
                elif k=='add':result+=n
                elif k=='subtract':result-=n
                elif k=='multiply':result*=n
                elif k=='divide':assert n;result/=n
                elif k=='min':result=max(result,n)
                else:raise AssertionError((k,v))
        return result

    def execute(block,ctx=None,prev=None):
        if ctx is None:ctx=country
        taken=False
        for k,o,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or cond(one(v,'limit'),ctx)):
                    execute(body(v,'limit'),ctx,prev);taken=True
            elif k in effects:
                execute(subst(effects[k],{a:c for a,b,c in entries(v)}) if isinstance(v,list) else effects[k],ctx,prev)
            elif k=='set_variable':
                name=v if isinstance(v,str) else one(v,'name')
                ctx['variables'][name]=1 if isinstance(v,str) or not fields(v,'value') else value(one(v,'value'),ctx,prev)
                if isinstance(v,list):
                    months=float(one(v,'months')) if fields(v,'months') else 12*float(one(v,'years')) if fields(v,'years') else None
                    if months is not None:ctx['expiry'][name]=months
            elif k=='change_variable':ctx['variables'][one(v,'name')]+=value(one(v,'add'),ctx,prev)
            elif k=='remove_variable':ctx['variables'].pop(v,None);ctx['expiry'].pop(v,None)
            elif k=='add_modifier':
                name=one(v,'name'); assert name in mods,name
                duration=12*float(one(v,'years')) if fields(v,'years') else None
                amount=value(one(v,'multiplier'),ctx) if fields(v,'multiplier') else 1
                ctx['modifiers'][name]=(duration,amount);awards.append((ctx['id'],name,duration,amount))
            elif k=='remove_modifier':ctx['modifiers'].pop(v,None)
            elif k=='clear_variable_list':ctx['lists'].pop(v,None)
            elif k=='add_to_variable_list':ctx['lists'].setdefault(one(v,'name'),[]).append(value(one(v,'target'),ctx,prev))
            elif k in ('every_scope_state','ordered_scope_state','every_in_list','random_company'):
                candidates=ctx['lists'].get(one(v,'variable'),[]) if k=='every_in_list' else ctx['companies'] if k=='random_company' else ctx['states']
                selected=[s for s in candidates if not fields(v,'limit') or cond(one(v,'limit'),s)]
                if k=='ordered_scope_state':
                    selected.sort(key=lambda s:value(one(v,'order_by'),s),reverse=True)
                    i=int(one(v,'position'));selected=selected[i:i+1]
                if k=='random_company':selected=selected[:1]
                for s in selected:execute(body(v,'limit','variable','order_by','position','check_range_bounds'),s,ctx)
            elif k in ('owner','root'):execute(v,value(k,ctx),ctx)
            elif k=='trigger_event':assert one(v,'popup')=='yes';queue.append(one(v,'id'))
            elif k=='add_journal_entry':
                j=one(v,'type');assert j not in ctx['journals'];ctx['journals'].add(j);execute(one(journals[j],'immediate'),ctx)
            elif k=='save_scope_value_as':scopes[one(v,'name')]=value(one(v,'value'),ctx)
            elif k=='save_scope_as':scopes[v]=ctx
            elif k.startswith('je:'):pass  # Progress bar mirrors are not authoritative.
            elif k in ('name','default_option','ai_chance'):pass
            else:raise AssertionError((k,o,v))

    def obj(id,**kwargs):return dict(id=id,variables={},expiry={},lists={},modifiers={},**kwargs)
    def reset(tag='USA',state_count=5):
        country.clear();scopes.clear();queue.clear();awards.clear()
        country.update(obj('country',country_definition='cd:'+tag,is_revolutionary='no',gdp=100_000_000,states=[],companies=[],journals=set()))
        for i,region in enumerate(['STATE_GEORGIA','STATE_FLORIDA','STATE_ALABAMA','STATE_TEXAS','STATE_CALIFORNIA'][:state_count]):
            s=obj(str(i),owner=country,state_region='s:'+region,state_population=1000+i,market_access=.95,buildings=[])
            s['buildings']=[obj(f'{i}-{b}',is_building_type='building_'+b,level=3,occupancy=.75) for b in ('food_industry','textile_mill','steel_mill','tooling_workshop')]
            country['states'].append(s)
        execute(effects[P+'economy_ensure_v1'])

    def expire():
        for name in list(country['expiry']):
            country['expiry'][name]-=1
            if country['expiry'][name]<=0:country['expiry'].pop(name);country['variables'].pop(name,None)
        for name,(duration,amount) in list(country['modifiers'].items()):
            if duration is not None:
                if duration<=1:country['modifiers'].pop(name)
                else:country['modifiers'][name]=(duration-1,amount)
    def month():
        expire();execute(effects[P+'economy_ensure_v1'])
        for j in list(country['journals']):
            execute(one(one(journals[j],'on_monthly_pulse'),'effect'))
            if cond(one(journals[j],'complete')):country['journals'].remove(j)
    def choose(number=1):
        event=events['ffpa_usa_flavor.'+str(int(country['variables'][P+'economy_pending_v1']))]
        assert cond(one(event,'trigger'));execute(one(event,'immediate'))
        option=fields(event,'option')[number-1];execute(option);return option
    def finish_market(choice=1):
        for _ in range(12):
            month()
            if country['variables'].get(P+'economy_pending_v1')==10:choose(2)
        assert country['variables'][P+'economy_pending_v1']==11
        return choose(choice)

    # Boundary arithmetic comes from actual script values, including zero population and ceil.
    reset(state_count=0);assert value(P+'market_coverage_v1',country)==0
    assert not cond(triggers[P+'market_stable_v1'])
    reset();country['states'][0]['state_population']=150
    for s in country['states'][1:]:s['state_population']=212.5
    country['states'][0]['market_access']=.9499
    assert value(P+'market_coverage_v1',country)==85 and cond(triggers[P+'market_stable_v1'])
    country['states'][0]['state_population']=151;assert not cond(triggers[P+'market_stable_v1'])
    for baseline,target in [(0,30),(20,30),(40,50),(41,52),(100,125)]:
        country['variables'][P+'industry_baseline_v1']=baseline
        assert value(P+'industry_target_value_v1',country)==target
    assert math.isclose(value(P+'economy_weekly_grant_v1',country),100_000_000*.005/52)

    # Empty factories, wrong geography, non-manufacturing buildings and same-category overcounting.
    reset();s=country['states'][0];s['buildings']=[obj('f',is_building_type='building_furniture_manufactory',level=10,occupancy=.75),obj('g',is_building_type='building_glassworks',level=10,occupancy=.75)]
    country['states']= [s];assert value(P+'industry_categories_v1',country)==1
    s['buildings'].append(obj('office',is_building_type='building_office',level=100,occupancy=1))
    assert value(P+'industry_levels_v1',country)==20
    s['state_region']='s:STATE_PUERTO_RICO';assert value(P+'industry_levels_v1',country)==0
    reset();country['states'][0]['buildings'][0]['occupancy']=.6999
    for b in country['states'][0]['buildings'][1:]:b['occupancy']=0
    assert value(P+'market_states_v1',country)==4
    for s in country['states']:
        for b in s['buildings']:b['occupancy']=.7499
    assert value(P+'industry_categories_v1',country)==0 and value(P+'industry_levels_v1',country)==60

    # Recovery cannot move counters or reset the fixed target; failed observations break continuity.
    reset()
    for _ in range(5):month()
    before=deepcopy(country['variables']);execute(effects[P+'economy_ensure_v1']);assert before==country['variables']
    country['states'][0]['market_access']=0;month();assert country['variables'][P+'market_months_v1']==0
    # Paid programs freeze their amount, never charge twice, expire and are canceled on identity loss.
    paid=choose(1); amount=country['variables'][P+'market_grant_weekly_v1'];country['gdp']*=2
    count=len(awards);execute(paid);assert len(awards)==count and country['variables'][P+'market_grant_weekly_v1']==amount
    for _ in range(24):expire()
    assert P+'market_grant_v1' not in country['modifiers'] and value(P+'economy_total_grants_v1',country)==0

    for market_choice,route,policy in product((1,2),repeat=3):
        reset();finish_market(market_choice)
        assert sum(n==P+'market_registration_v1' for _,n,_,_ in awards)==1
        rewarded=[id for id,n,_,_ in awards if n==P+('market_corridor_v1' if market_choice==1 else 'market_branches_v1')]
        assert set(rewarded)==({'2','3','4'} if market_choice==1 else {'0','1','2','3','4'})
        baseline=country['variables'][P+'industry_baseline_v1'];target=country['variables'][P+'industry_target_v1']
        assert (baseline,target)==(60,75)
        month();assert country['variables'][P+'economy_pending_v1']==12;choose(route)
        for s in country['states']:
            for b in s['buildings']:b['level']=4
        execute(effects[P+'economy_ensure_v1']);assert country['variables'][P+'industry_target_v1']==target
        # A company event can coexist with the main line but cannot be replayed after retry.
        company=obj('company',company_owned_levels=1,company_is_prosperous='yes');country['companies']=[company]
        month();assert country['variables'][P+'economy_pending_v1']==13;choose(1)
        month();assert country['variables'][P+'economy_pending_v1']==15
        event=events['ffpa_usa_flavor.15'];execute(one(event,'immediate'));old_scope=scopes.copy()
        execute(effects[P+'economy_retry_v1']);count=len(awards);execute(fields(event,'option')[0]);assert len(awards)==count
        choose(1);assert country['variables'][P+'company_contract_choice_v1']==1
        while country['variables'][P+'industry_months_v1']<17:month()
        country['states'][0]['buildings'][0]['level']=0
        country['states'][1]['buildings'][0]['level']=0
        month();assert country['variables'][P+'industry_months_v1']==0
        for s in country['states']:
            for b in s['buildings']:b['level']=4
        for _ in range(18):month()
        assert country['variables'][P+'industry_ready_v1']==1
        assert country['variables'][P+'economy_pending_v1']==14
        # The snapshot excludes later acquisitions and states no longer owned by USA.
        lost=country['states'][0];lost['owner']=obj('foreign');country['states'].remove(lost)
        new=deepcopy(country['states'][0]);new['id']='new';new['owner']=country;country['states'].append(new)
        option=choose(policy);count=len(awards);execute(option);assert len(awards)==count
        selected=P+('company_entry_v1' if policy==1 else 'company_champions_v1')
        other=P+('company_champions_v1' if policy==1 else 'company_entry_v1')
        assert selected in country['modifiers'] and other not in country['modifiers']
        assert country['modifiers'][selected][0] is None
        timed=P+('company_entry_construction_v1' if policy==1 else 'company_champions_construction_v1')
        assert country['modifiers'][timed][0]==120
        assert not any(id in ('new',lost['id']) and n in (P+'industry_hub_v1',P+'industry_network_v1') for id,n,_,_ in awards)
        assert not country['lists'];month();execute(effects[P+'economy_ensure_v1'])
        assert not country['journals'] and len(awards)==count

    # No company is needed for either milestone. Native/old-save recovery can resume a validated snapshot.
    reset();finish_market();month();choose(1)
    for s in country['states']:
        for b in s['buildings']:b['level']=4
    for _ in range(18):
        month()
        if country['variables'].get(P+'economy_pending_v1')==13:choose(2)
    assert country['variables'][P+'economy_pending_v1']==14 and 'ffpa_usa_flavor.15' not in queue
    target=country['variables'][P+'industry_target_v1'];saved_targets=list(country['lists'][P+'industry_reward_states_v1'])
    event=events['ffpa_usa_flavor.14'];execute(one(event,'immediate'))
    country['country_definition']='cd:CAN';execute(effects[P+'economy_ensure_v1'])
    country['journals'].clear();country['country_definition']='cd:USA';execute(effects[P+'economy_ensure_v1'])
    assert country['variables'][P+'industry_target_v1']==target
    assert all(a is b for a,b in zip(saved_targets,country['lists'][P+'industry_reward_states_v1']))
    execute(effects[P+'economy_dispatch_v1']);count=len(awards)
    execute(fields(event,'option')[0]);assert len(awards)==count
    choose(1);assert country['variables'][P+'industry_complete_v1']==1

    # All independent route/company choice combinations retain the approved numbers and durations.
    assert one(mods[P+'market_registration_v1'],'country_max_companies_add')=='1'
    assert one(mods[P+'company_entry_v1'],'country_max_companies_add')=='2'
    assert one(mods[P+'company_champions_v1'],'country_company_throughput_bonus_add')=='0.1'
    assert one(mods[P+'company_entry_construction_v1'],'country_company_construction_efficiency_bonus_add')=='0.1'
    assert one(mods[P+'company_champions_construction_v1'],'country_company_construction_efficiency_bonus_add')=='0.2'
    reset();month();country['variables'][P+'economy_pending_v1']=10;paid=choose(1)
    country['country_definition']='cd:CAN';execute(effects[P+'economy_ensure_v1'])
    assert P+'market_grant_v1' not in country['modifiers'] and P+'market_linkage_v1' not in country['modifiers']
    assert country['variables'][P+'market_months_v1']==0
    count=len(awards);execute(paid);assert len(awards)==count
    snapshot=deepcopy(country['variables']);execute(effects[P+'economy_ensure_v1']);assert snapshot==country['variables']
    for tag in ('CAN','ZZZGEORGIA'):
        reset(tag);assert not country['journals'] and not country['variables']
    reset();country['is_revolutionary']='yes';execute(effects[P+'economy_ensure_v1']);assert not cond(triggers[P+'market_eligible_v1'])

    for lang in ('english','simp_chinese'):
        p=ROOT/f'localization/{lang}/ffpa_north_american_economy_l_{lang}.yml'
        assert p.read_bytes().startswith(b'\xef\xbb\xbf');loc=parse_loc(p.read_text(encoding='utf-8-sig'),lang)
        for event in events.values():
            for f in ('title','desc','flavor'):assert one(event,f) in loc
            for option in fields(event,'option'):assert one(option,'name') in loc
        assert all(k in loc for k in mods)
        for button in buttons.values():
            assert one(button,'name') in loc and one(button,'desc') in loc
    wrapper=P+'economy_recovery_v1'
    for hook in ('on_country_formed','on_monthly_pulse_country'):assert wrapper in one(actions[hook],'on_actions')
    assert one(one(actions[wrapper],'effect'),P+'economy_ensure_v1')=='yes'
    print('PASS: actual USA economic scripts: population/industry boundaries, fixed targets, continuity, recovery, fiscal snapshots/expiry, company choices, reward scopes, stale events and bilingual coverage.')
    print('NOT TESTED: native company/list scopes, split/merged states, popup and JE ordering, AI, UI, budget display or save reload.')

if __name__=='__main__':main()
