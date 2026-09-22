"""Execute the actual governance script subset; no engine, UI or save-format proof."""
from pathlib import Path
import argparse
import math
import operator
import re
from check_north_america_preflight import ROOT, definitions, fields, one, parse
from check_cmf_presentation import entries
from validate_localization import parse as parse_loc

N = 'ffpa_north_american_governance'
P = 'ffpa_usa_gov_'
def key(n): return P+n+'_v1'
def without(block, *names): return [x for k,o,v in entries(block) if k not in names for x in (k,o,v)]
def subst(block, params):
    if isinstance(block, list): return [subst(x,params) for x in block]
    for k,v in params.items(): block=block.replace('$'+k+'$',str(v))
    return block

class Script:
    def __init__(self):
        self.effects=definitions(ROOT/f'common/scripted_effects/{N}.txt')
        self.triggers=definitions(ROOT/f'common/scripted_triggers/{N}.txt')
        self.values=definitions(ROOT/f'common/script_values/{N}.txt')
        self.mods=definitions(ROOT/f'common/static_modifiers/{N}.txt')
        self.now=0; self.events=[]; self.scopes={}
        self.country=self.scope(country_definition='cd:USA',is_revolutionary='no',gdp=52000000,
                                government_legitimacy=60,bureaucracy=0,produced_bureaucracy=100,
                                in_default='no',scaled_debt=0,ffpa_usa_mainland_population_v1=100,
                                ffpa_usa_industry_levels_v1=100)
        self.country['states']=[]
    def scope(self,**kwargs): return dict(variables={},expiry={},modifiers={},journals=set(),**kwargs)
    def value(self,x,c,p=None):
        if isinstance(x,list):return self.calc(x,c,p)
        if x=='root':return self.country
        if x=='this':return c
        if x=='prev':return p
        if x.startswith('prev.'):return self.value(x[5:],p,c)
        if x.startswith('root.'):return self.value(x[5:],self.country,c)
        if x.startswith('this.'):return self.value(x[5:],c,p)
        if x.startswith('var:'):return c['variables'].get(x[4:],0)
        if x.startswith('scope:'):return self.scopes.get(x[6:])
        if x in self.values:return self.calc(self.values[x],c,p)
        if x in c:return c[x]
        if x=='modifier:country_bureaucracy_mult':return c.get(x,0)
        try:return float(x)
        except ValueError:return x
    def cond(self,block,c=None,p=None):
        c=self.country if c is None else c
        ops={'=':operator.eq,'>':operator.gt,'<':operator.lt,'>=':operator.ge,'<=':operator.le}
        for k,o,v in entries(block):
            if k=='OR':ok=any(self.cond([a,b,d],c,p) for a,b,d in entries(v))
            elif k=='AND':ok=self.cond(v,c,p)
            elif k=='NOT':ok=not self.cond(v,c,p)
            elif k=='always':ok=v=='yes'
            elif k=='custom_tooltip':ok=self.cond(without(v,'text'),c,p)
            elif k=='has_variable':ok=v in c['variables']
            elif k=='has_modifier':ok=v in c['modifiers']
            elif k=='has_journal_entry':ok=v in c['journals']
            elif k=='exists':ok=self.value(v,c,p) is not None
            elif k in self.triggers:
                ok=self.cond(subst(self.triggers[k],{a:d for a,b,d in entries(v)}),c,p) if isinstance(v,list) else self.cond(self.triggers[k],c,p)==(v=='yes')
            elif k in ('any_scope_state','any_scope_building'):
                ok=any(self.cond(v,s,c) for s in c.get('states' if k=='any_scope_state' else 'buildings',[]))
            else:
                a,b=self.value(k,c,p),self.value(v,c,p)
                ok=a is b if isinstance(a,dict) or isinstance(b,dict) else ops[o](a,b)
            if not ok:return False
        return True
    def calc(self,block,c,p=None,result=0):
        taken=False
        for k,o,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or self.cond(one(v,'limit'),c,p)):
                    result=self.calc(without(v,'limit'),c,p,result);taken=True
            elif k in ('every_scope_state','every_scope_building'):
                for s in c.get('states' if k=='every_scope_state' else 'buildings',[]):
                    if self.cond(one(v,'limit'),s,c):result=self.calc(without(v,'limit'),s,c,result)
            elif k=='desc':pass
            else:
                n=self.value(v,c,p)
                if k=='value':result=n
                elif k=='add':result+=n
                elif k=='subtract':result-=n
                elif k=='multiply':result*=n
                elif k=='divide':assert n;result/=n
                elif k=='min':result=max(result,n)
                elif k=='max':result=min(result,n)
                else:raise AssertionError((k,v))
        return result
    def run(self,block,c=None,p=None):
        c=self.country if c is None else c
        if isinstance(block,str):block=self.effects[block]
        taken=False
        for k,o,v in entries(block):
            if k in ('if','else_if','else'):
                if k=='if':taken=False
                if not taken and (k=='else' or self.cond(one(v,'limit'),c,p)):
                    self.run(without(v,'limit'),c,p);taken=True
            elif k in self.effects:
                self.run(subst(self.effects[k],{a:d for a,b,d in entries(v)}) if isinstance(v,list) else self.effects[k],c,p)
            elif k in ('hidden_effect','effect'):self.run(v,c,p)
            elif k in ('custom_tooltip','ai_chance','default_option','name','trigger'):pass
            elif k=='set_variable':
                if isinstance(v,list):
                    name=one(v,'name');val=one(v,'value') if fields(v,'value') else '1'
                    c['variables'][name]=self.value(val,c,p)
                    duration=float(one(v,'months')) if fields(v,'months') else float(one(v,'years'))*12 if fields(v,'years') else 0
                    if duration:c['expiry'][name]=self.now+duration
                else:c['variables'][v]=1
            elif k=='change_variable':
                name=one(v,'name');a=c['variables'].get(name,0)
                for operation in ['add','subtract','multiply','divide']:
                    if fields(v,operation):
                        b=self.value(one(v,operation),c,p)
                        a={'add':lambda:a+b,'subtract':lambda:a-b,'multiply':lambda:a*b,'divide':lambda:a/b}[operation]()
                c['variables'][name]=a
            elif k=='clamp_variable':
                name=one(v,'name');c['variables'][name]=max(float(one(v,'min')),min(float(one(v,'max')),c['variables'][name]))
            elif k=='remove_variable':c['variables'].pop(v,None);c['expiry'].pop(v,None)
            elif k=='add_modifier':
                name=one(v,'name');duration=float(one(v,'months')) if fields(v,'months') else float(one(v,'years'))*12 if fields(v,'years') else math.inf
                c['modifiers'][name]=(self.now+duration,self.value(one(v,'multiplier'),c,p) if fields(v,'multiplier') else 1)
            elif k=='remove_modifier':c['modifiers'].pop(v,None)
            elif k=='add_journal_entry':c['journals'].add(one(v,'type'))
            elif k=='trigger_event':self.events.append(one(v,'id'))
            elif k=='save_scope_value_as':self.scopes[one(v,'name')]=self.value(one(v,'value'),c,p)
            elif k in ('every_scope_state','every_scope_building'):
                for s in c.get('states' if k=='every_scope_state' else 'buildings',[]):
                    if self.cond(one(v,'limit'),s,c):self.run(without(v,'limit'),s,c)
            elif k=='owner':self.run(v,c['owner'],c)
            else:raise AssertionError((k,v))
    def tick(self,months=1):
        self.now+=months
        for c in [self.country,*self.country['states']]:
            for name,expiry in list(c['expiry'].items()):
                if expiry<=self.now:c['variables'].pop(name,None);del c['expiry'][name]
            for name,(expiry,_) in list(c['modifiers'].items()):
                if expiry<=self.now:del c['modifiers'][name]
    def unlock(self,politics=True,economy=True):
        if politics:self.country['variables']['ffpa_usa_political_complete_v1']=1
        if economy:self.country['variables']['ffpa_usa_industry_complete_v1']=1
        self.run(key('ensure'))
    def state(self,sol=20,pop=100):
        s=self.scope(owner=self.country,average_sol=sol,state_population=pop,ffpa_na_is_mainland_state_v1='yes',turmoil=0,buildings=[])
        self.country['states'].append(s);return s


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--game-root',type=Path,required=True);args=ap.parse_args()
    # Every local definition parses; all assets and new modifier types have native definitions.
    game_types={}
    for f in (args.game_root/'common/modifier_type_definitions').glob('*.txt'):game_types.update(definitions(f,allow_duplicates=True))
    s=Script()
    for block in s.mods.values():
        for k,o,v in entries(block):
            if k=='icon':assert (args.game_root/v.strip('"')).exists(),v
            else:assert k in game_types,k
    # Recovery never advances counters; both unlock orders preserve the first domain.
    for first in ('credit','risk'):
        s=Script();s.unlock(first=='credit',first=='risk');d=s.country['variables'];d[key(first)]=42
        for _ in range(3):s.run(key('ensure'))
        assert d[key(first)]==42 and d[key(first+'_grace')]==24
        s.unlock();assert d[key(first)]==42 and len(s.country['journals'])==1
    # Strict identity and suspension: permanent penalties retain their original expiry.
    s=Script();s.country['country_definition']='cd:TUR';s.unlock();assert key('initialized') not in s.country['variables']
    s=Script();s.unlock();d=s.country['variables'];d[key('credit_grace')]=0;d[key('credit')]=0
    for _ in range(12):s.run(key('credit_transition'))
    expiry=s.country['modifiers'][key('credit_penalty')][0]
    s.country['country_definition']='cd:TUR';s.run(key('ensure'));s.run(key('ensure'))
    assert s.country['modifiers'][key('credit_penalty')][0]==expiry
    assert key('credit_good') not in s.country['modifiers']
    s.country['country_definition']='cd:USA';s.run(key('ensure'));assert d[key('credit_grace')]==0
    # Independent simultaneous failures, no repeats, repair before/after penalty expiry, second episode.
    s=Script();s.unlock();d=s.country['variables'];d.update({key('credit'):0,key('risk'):100,key('credit_grace'):0,key('risk_grace'):0})
    for _ in range(11):
        s.run(key('credit_transition'));s.run(key('risk_transition'))
    assert not s.events
    s.run(key('credit_transition'));s.run(key('risk_transition'));s.run(key('refresh'))
    assert set(s.events)=={'ffpa_usa_flavor.40','ffpa_usa_flavor.41'}
    assert s.country['modifiers'][key('credit_penalty')][0]==96 and s.country['modifiers'][key('risk_penalty')][0]==60
    for _ in range(20):s.run(key('credit_transition'));s.run(key('risk_transition'))
    assert len(s.events)==2
    d[key('risk')]=64
    for _ in range(12):s.run(key('risk_transition'))
    assert key('risk_failed') in d
    s.tick(60);s.run(key('risk_transition'));s.run(key('refresh'))
    assert key('risk_failed') not in d and key('credit_failed') in d and key('risk_good') in s.country['modifiers']
    s.tick(36);assert key('credit_penalty') not in s.country['modifiers']
    s.run(key('credit_transition'));assert key('credit_failed') in d
    d[key('credit')]=35
    for _ in range(11):s.run(key('credit_transition'))
    assert key('credit_failed') in d
    s.run(key('credit_transition'));assert key('credit_failed') not in d
    d[key('credit')]=19
    for _ in range(12):s.run(key('credit_transition'))
    assert s.events.count('ffpa_usa_flavor.40')==2
    # Twenty-four preparation pulses, then twelve actual crisis months.
    s=Script();s.unlock();d=s.country['variables'];d[key('credit')]=0
    for _ in range(24):s.run(key('credit_transition'))
    assert d[key('credit_crisis')]==0 and not s.events
    for _ in range(12):s.run(key('credit_transition'))
    assert s.events==['ffpa_usa_flavor.40']
    # Shared acceleration/review slots, frozen GDP fee, normal deficits, completion/cancellation.
    s=Script();s.unlock();d=s.country['variables'];d['ffpa_usa_political_oversight_v1']=2;d['ffpa_usa_political_representation_v1']=1
    s.run(key('start_emergency'));assert not s.cond([key('can_credit_line'),'=','yes'])
    s.run(key('start_credit_line'));assert key('credit_line_weekly') not in d
    s.run(key('start_conference'));assert d[key('conference_weekly')]==2500 and s.country['expiry'][key('conference_cooldown')]==18
    s.country['gdp']*=10;s.run(key('start_conference'));assert d[key('conference_weekly')]==2500
    s.run(key('start_review'));assert not s.cond([key('can_procurement'),'=','yes'])
    s.country['in_default']='yes';before=d[key('credit')]
    for _ in range(11):s.tick();s.run(key('actions_monthly'))
    assert d[key('credit')]==before
    s.tick();s.run(key('actions_monthly'));assert d[key('credit')]==before+12 and key('conference_weekly') not in d
    s.run(key('actions_monthly'));assert d[key('credit')]==before+12
    s=Script();s.unlock();s.run(key('start_relief'));s.country['country_definition']='cd:TUR';s.run(key('ensure'))
    assert key('relief_weekly') not in s.country['variables'] and key('relief_grant') not in s.country['modifiers']
    # Correct the journal's own bureaucracy and legitimacy contributions, including failure.
    for mod,leg,bur in [('credit_good',5,.08),('credit_warning',2,.04),('credit_penalty',-15,-.15)]:
        s=Script();s.country['modifiers'][key(mod)]=(100,1)
        s.country.update(government_legitimacy=50+leg,produced_bureaucracy=100*(1+bur),bureaucracy=100*bur)
        s.country['modifier:country_bureaucracy_mult']=bur
        assert abs(s.value(key('bureaucracy'),s.country))<1e-8
        assert s.value(key('legitimacy'),s.country)==50
    # Thirty-six observations; same-cohort comparison ignores newly acquired poor territory.
    s=Script();s.unlock();old=s.state()
    for _ in range(36):s.run(key('sample_sol'))
    assert s.country['variables'][key('sol_falling')]==0
    newcomer=s.state(sol=1,pop=1000)
    s.run(key('sample_sol'));assert s.country['variables'][key('sol_current')]==20
    old['average_sol']=17
    for _ in range(3):s.run(key('sample_sol'))
    assert s.country['variables'][key('sol_falling')]==3
    assert abs(old['variables'][key('history_sum')]-sum(old['variables'][key('sol_'+str(i))] for i in range(36)))<1e-8
    s.run(key('clear_history'),old);assert key('history_owner') not in old['variables']
    # Zero manufacturing is unhealthy; relief never reduces debt pressure.
    s=Script();s.unlock();s.country['ffpa_usa_industry_levels_v1']=0
    assert s.value(key('low_employment'),s.country)==100
    s.country['scaled_debt']=.9;assert s.value(key('risk_change'),s.country)==2.5
    s.country['variables'][key('relief_left')]=12;assert s.value(key('risk_change'),s.country)==2
    # Actual monthly path remains clamped and does not re-grant preparation after save-like ensures.
    s=Script();s.unlock();s.state()
    for _ in range(50):s.tick();s.run(key('monthly'));s.run(key('ensure'))
    assert 0<=s.country['variables'][key('credit')]<=100 and 0<=s.country['variables'][key('risk')]<=100
    assert s.country['variables'][key('credit_grace')]==0
    # Six real bilingual events, safe scoped tickets, native themes, no numerical option labels.
    events=definitions(ROOT/'events/ffpa_american_governance_events.txt')
    assert set(events)=={f'ffpa_usa_flavor.{n}' for n in (30,31,40,41,43,44)}
    media=definitions(args.game_root/'gfx/media_aliases/media_aliases.txt')
    for lang in ['english','simp_chinese']:
        loc=parse_loc((ROOT/f'localization/{lang}/{N}_l_{lang}.yml').read_text(encoding='utf-8-sig'),lang)
        for e in events.values():
            assert (args.game_root/one(e,'icon').strip('"')).exists()
            assert one(one(e,'event_image'),'video').strip('"') in media
            assert r'\n\n' in loc[one(e,'desc')] and '#bold ' in loc[one(e,'desc')]
            for option in fields(e,'option'):assert not re.search(r'\d',loc[one(option,'name')])
    s=Script();s.unlock();d=s.country['variables'];d[key('hearing_due')]=1;s.run(key('dispatch'))
    e=events['ffpa_usa_flavor.30'];s.run(one(e,'immediate'));option=fields(e,'option')[0]
    s.run(option);first=d[key('credit')];s.run(option);assert d[key('credit')]==first
    d[key('emergency_due')]=1;s.tick(18);s.run(key('dispatch'));s.run(one(events['ffpa_usa_flavor.31'],'immediate'))
    s.country['country_definition']='cd:TUR';s.run(key('ensure'));s.country['country_definition']='cd:USA';s.run(key('ensure'))
    before=d[key('credit')];s.run(fields(events['ffpa_usa_flavor.31'],'option')[1]);assert d[key('credit')]==before
    # Both hearing choices remain real choices with only one field; neither invents the other field.
    for political in (True,False):
        for option_index in (0,1):
            s=Script();s.unlock(political,not political);d=s.country['variables'];d[key('hearing_due')]=1
            s.run(key('dispatch'));s.run(one(events['ffpa_usa_flavor.30'],'immediate'))
            s.run(fields(events['ffpa_usa_flavor.30'],'option')[option_index])
            assert key('risk' if political else 'credit') not in d
            expected=(65 if option_index==0 else 63) if political else 20
            assert d[key('credit' if political else 'risk')]==expected
    # Native expiry is authoritative even between it and the next monthly settlement.
    s=Script();s.unlock();s.run(key('start_conference'));assert s.value(key('total_cost'),s.country)==2500
    s.tick(12);assert key('conference_weekly') in s.country['variables'] and s.value(key('total_cost'),s.country)==0
    # A slightly late monthly pulse cannot apply a thirteenth review/relief increment.
    s=Script();s.unlock();d=s.country['variables'];s.country.update(government_legitimacy=40,bureaucracy=8,produced_bureaucracy=108)
    s.country['modifier:country_bureaucracy_mult']=.08
    s.run(key('start_review'));s.country['expiry'][key('review_term')]=12.5
    gains=0
    for _ in range(13):
        s.tick();gains+=s.value(key('credit_change'),s.country);s.run(key('actions_monthly'))
    assert gains==12
    s=Script();s.unlock();d=s.country['variables'];d[key('relief_left')]=0
    s.country['ffpa_usa_industry_levels_v1']=0
    assert s.value(key('risk_change'),s.country)==1
    # Crisis continuity resets at its boundary, while a failed field stays failed until repaired.
    for domain,unsafe,safe in [('credit',19,20),('risk',85,84)]:
        s=Script();s.unlock();d=s.country['variables'];d[key(domain+'_grace')]=0;d[key(domain)]=unsafe
        for _ in range(11):s.run(key(domain+'_transition'))
        d[key(domain)]=safe;s.run(key(domain+'_transition'));assert d[key(domain+'_crisis')]==0
    # Governance input source assets have local precedents; new helper references resolve.
    catalog={}
    for folder in ('scripted_triggers','scripted_effects','script_values','scripted_guis'):
        for file in (ROOT/'common'/folder).glob('*.txt'):catalog.update(definitions(file))
    def check_refs(block):
        for k,o,v in entries(block):
            if k.startswith(P):assert k in catalog,k
            if isinstance(v,list):check_refs(v)
    for folder in ('scripted_triggers','scripted_effects','script_values','scripted_buttons','journal_entries'):
        for block in definitions(ROOT/f'common/{folder}/{N}.txt').values():check_refs(block)
    for folder in ('scripted_guis','customizable_localization','script_values'):
        text=(ROOT/f'common/{folder}/{N}.txt').read_text()
        assert not re.search(r'\b(effect|set_variable|change_variable|remove_variable|trigger_event|on_monthly_pulse)\s*=',text)
    gui=(ROOT/'gui/ffpa_usa_journal_presentation.gui').read_text();parse(gui)
    assert 'type ffpa_usa_ui_governance = vbox' in gui and 'progressbar_bad.dds' in gui
    assert 'GetPlayer' not in gui and '.Execute(' not in gui
    assert all('add_modifier' not in str(events[f'ffpa_usa_flavor.{n}']) for n in (40,41,43,44))
    actions=definitions(ROOT/'common/on_actions/ffpa_north_american_on_actions.txt')
    for hook in ['on_country_formed','on_monthly_pulse_country']:
        assert key('recovery') in one(actions[hook],'on_actions')
    assert one(actions[key('recovery')],'effect')==[key('ensure'),'=','yes']
    print('PASS: actual-script unlocks, grace/crisis/recovery, independent penalties, shared actions, frozen costs, self-correction, rolling SoL cohort, event tickets, bilingual narratives and native assets.')
    print('NOT TESTED: engine accessors, timing/cache refresh, state split/merge, UI/hover rendering, AI, budget entries or save reload.')

if __name__=='__main__':main()
