"""Check every number stated in the STS report against the freshly generated outputs."""
import pandas as pd, pickle
checks=[]
def chk(label, paper, actual, tol=0.5):
    ok = abs(float(paper)-float(actual))<=tol
    checks.append((label, paper, round(float(actual),3), 'OK' if ok else 'MISMATCH'))
agg=pd.read_csv('outputs/aggregate/aggregate_period_totals_summary.csv',comment='#')
def tot(party,per): return float(agg[(agg.Party==party)&(agg.Period.str.startswith(per))].Total_Amount.iloc[0])
chk('pre total',812074962,tot('Total','2001-2010')); chk('post total',5968594250,tot('Total','2011-2020'))
chk('Dem pre',474145427,tot('Democrat','2001-2010')); chk('Dem post',3019239341,tot('Democrat','2011-2020'))
chk('Rep pre',337929535,tot('Republican','2001-2010')); chk('Rep post',2949354909,tot('Republican','2011-2020'))
chk('total % change',635,(tot('Total','2011-2020')/tot('Total','2001-2010')-1)*100,1)
chk('Dem % change',536.8,(tot('Democrat','2011-2020')/tot('Democrat','2001-2010')-1)*100,0.05)
chk('Rep % change',772.8,(tot('Republican','2011-2020')/tot('Republican','2001-2010')-1)*100,0.05)
chk('gap pre $M',136.2,(tot('Democrat','2001-2010')-tot('Republican','2001-2010'))/1e6,0.05)
chk('gap pre %',40.3,(tot('Democrat','2001-2010')/tot('Republican','2001-2010')-1)*100,0.05)
chk('gap post $M',69.9,(tot('Democrat','2011-2020')-tot('Republican','2011-2020'))/1e6,0.05)
chk('gap post %',2.4,(tot('Democrat','2011-2020')/tot('Republican','2011-2020')-1)*100,0.05)
n=agg[(agg.Party=='Total')]
chk('transactions pre',53483,float(n[n.Period.str.startswith('2001-2010')].Num_Transactions.iloc[0])); chk('transactions post',457080,float(n[n.Period.str.startswith('2011-2020')].Num_Transactions.iloc[0]))
chk('committees pre',831,float(n[n.Period.str.startswith('2001-2010')].Unique_Committees.iloc[0])); chk('committees post',1979,float(n[n.Period.str.startswith('2011-2020')].Unique_Committees.iloc[0]))
cyc=pd.read_csv('outputs/aggregate/aggregate_ie_summary_by_cycle.csv',comment='#'); cyc=cyc[cyc.CYCLE_END_YEAR.notna()]
def c(y,p): return float(cyc[(cyc.CYCLE_END_YEAR==y)&(cyc.BENEFITING_PARTY==p)].Total_Amount.iloc[0])
chk('2004 gap $M',117.3,(c(2004,'Democrat')-c(2004,'Republican'))/1e6,0.05); chk('2004 gap %',188.5,(c(2004,'Democrat')/c(2004,'Republican')-1)*100,0.05)
chk('2012 gap $M',310.4,(c(2012,'Republican')-c(2012,'Democrat'))/1e6,0.05); chk('2012 gap %',100.2,(c(2012,'Republican')/c(2012,'Democrat')-1)*100,0.05)
chk('2020 gap $M',358.8,(c(2020,'Democrat')-c(2020,'Republican'))/1e6,0.05); chk('2020 gap %',31.1,(c(2020,'Democrat')/c(2020,'Republican')-1)*100,0.05)
for name,pre_d,pre_r,post_d,post_r in [('senate',231328478,198288123,1727045597,1764633884),('presidential',242816949,139641412,1292193744,1184721025)]:
    t=pd.read_csv(f'outputs/{name}/{name}_period_totals_summary.csv',comment='#')
    def tt(party,per): return float(t[(t.Party==party)&(t.Period.str.startswith(per))].Total_Amount.iloc[0])
    chk(f'{name} Dem pre',pre_d,tt('Democrat','2001-2010')); chk(f'{name} Rep pre',pre_r,tt('Republican','2001-2010'))
    chk(f'{name} Dem post',post_d,tt('Democrat','2011-2020')); chk(f'{name} Rep post',post_r,tt('Republican','2011-2020'))
    chk(f'{name} committees pre', {'senate':475,'presidential':558}[name], float(t[(t.Party=='Total')&(t.Period.str.startswith('2001-2010'))].Unique_Committees.iloc[0]))
    chk(f'{name} committees post', {'senate':1238,'presidential':1287}[name], float(t[(t.Party=='Total')&(t.Period.str.startswith('2011-2020'))].Unique_Committees.iloc[0]))
    chk(f'{name} median pre', {'senate':100,'presidential':187}[name], float(t[(t.Party=='Total')&(t.Period.str.startswith('2001-2010'))].Median_Amount.iloc[0]))
    chk(f'{name} median post', 34, float(t[(t.Party=='Total')&(t.Period.str.startswith('2011-2020'))].Median_Amount.iloc[0]))
    chk(f'{name} growth %', {'senate':712.7,'presidential':547.6}[name], (tt('Democrat','2011-2020')+tt('Republican','2011-2020'))/(tt('Democrat','2001-2010')+tt('Republican','2001-2010'))*100-100, 0.05)
s2=pd.read_csv('outputs/senate/senate_ie_summary_by_cycle.csv',comment='#'); s2=s2[s2.CYCLE_END_YEAR.notna()]
chk('2012 senate diff $M',27.8,(float(s2[(s2.CYCLE_END_YEAR==2012)&(s2.BENEFITING_PARTY=='Republican')].Total_Amount.iloc[0])-float(s2[(s2.CYCLE_END_YEAR==2012)&(s2.BENEFITING_PARTY=='Democrat')].Total_Amount.iloc[0]))/1e6,0.05)
src=pd.read_csv('outputs/aggregate/aggregate_ie_summary_by_period_party_source.csv',comment='#')
def sv(per,party,cat):
    r=src[(src.PERIOD.str.startswith(per))&(src.BENEFITING_PARTY==party)&(src.COMMITTEE_CATEGORY==cat)]; return float(r.Total_Amount.iloc[0]) if len(r) else 0.0
for cat,pre,post in [('Party Committee',509480610,586054167),('Traditional PAC',203942957,852136236),('Other/Unknown',97795511,760905537),('Individual IE Committee',855884,2456820),('Super PAC',0,3767041490)]:
    chk(f'T3 {cat} pre',pre,sv('Pre','Total',cat)); chk(f'T3 {cat} post',post,sv('Post','Total',cat))
for party,cat,pre,post in [('Democrat','Super PAC',0,1708147004),('Democrat','Party Committee',309809643,275260984),('Democrat','Traditional PAC',120960424,699244833),('Democrat','Other/Unknown',42918244,334232798),('Democrat','Individual IE Committee',457116,2353722),('Republican','Super PAC',0,2058894486),('Republican','Party Committee',199670967,310793183),('Republican','Traditional PAC',82982533,152891403),('Republican','Other/Unknown',54877267,426672739),('Republican','Individual IE Committee',398768,103098)]:
    chk(f'C1 {party} {cat} pre',pre,sv('Pre',party,cat)); chk(f'C1 {party} {cat} post',post,sv('Post',party,cat))
for name,rows in [('senate',[('Super PAC',0,2277600550),('Party Committee',313055244,531311743),('Traditional PAC',73130459,266544890),('Other/Unknown',43199866,414142750),('Individual IE Committee',231032,2079548)]),('presidential',[('Super PAC',0,1489440940),('Party Committee',196425366,54742424),('Traditional PAC',130812498,585591346),('Other/Unknown',54595645,346762787),('Individual IE Committee',624852,377272)])]:
    d=pd.read_csv(f'outputs/{name}/{name}_ie_summary_by_period_party_source.csv',comment='#')
    for cat,pre,post in rows:
        for per,val in [('Pre',pre),('Post',post)]:
            r=d[(d.PERIOD.str.startswith(per))&(d.BENEFITING_PARTY=='Total')&(d.COMMITTEE_CATEGORY==cat)]
            chk(f'T4 {name} {cat} {per}',val,float(r.Total_Amount.iloc[0]) if len(r) else 0.0)
pd_=pd.read_csv('outputs/presidential/presidential_ie_summary_by_period_party_source.csv',comment='#')
chk('pres post Dem trad PAC $M',520.9,float(pd_[(pd_.PERIOD.str.startswith('Post'))&(pd_.BENEFITING_PARTY=='Democrat')&(pd_.COMMITTEE_CATEGORY=='Traditional PAC')].Total_Amount.iloc[0])/1e6,0.05)
oth=pd.read_csv('outputs/other_IEs_breakdown.csv')
def o(g,tp): r=oth[(oth.Group==g)&(oth.CMTE_TP==tp)]; return float(r.Total_Amount.iloc[0])/1e6 if len(r) else 0
for g,tp,v in [('Pre-CU Overall','I',52.9),('Pre-CU Overall','W',29.4),('Pre-CU Overall','C',15.5),('Post-CU Overall','I',586.8),('Post-CU Overall','W',167.0),('Post-CU Overall','C',7.1),('Pre-CU Democrats','I',20.5),('Pre-CU Democrats','W',19.6),('Pre-CU Democrats','C',2.8),('Post-CU Democrats','I',239.7),('Post-CU Democrats','W',93.5),('Pre-CU Republicans','I',32.4),('Pre-CU Republicans','C',12.7),('Pre-CU Republicans','W',9.8),('Post-CU Republicans','I',347.1),('Post-CU Republicans','W',73.5)]:
    chk(f'other {g} {tp}',v,o(g,tp),0.05)
co=pd.read_csv('outputs/regressions/regression_coefficients.csv')
def coef(ds,model,term): return co[(co.dataset==ds)&(co.model==model)&(co.term==term)].iloc[0]
M='source_share_shift_category_specific_post_base_party_committee'; W='weighted_superpac_source_share_partisan_shift'
paper_T2={('Aggregate','post_cu'):(1.698,.822),('Senate','post_cu'):(2.151,.529),('Presidential','post_cu'):(1.244,.662),('Aggregate','republican'):(-.400,.899),('Senate','republican'):(-.140,.684),('Presidential','republican'):(-.660,1.025),('Aggregate','post_x_republican'):(.529,1.180),('Senate','post_x_republican'):(.154,.778),('Presidential','post_x_republican'):(.904,1.251),('Aggregate','presidential_office'):(-2.395,.590),('Aggregate','presidential_cycle'):(3.123,.606),('Senate','presidential_cycle'):(.301,.346),('Presidential','presidential_cycle'):(5.944,.616),('Aggregate','const'):(16.037,.687),('Senate','const'):(17.185,.526),('Presidential','const'):(12.494,.793)}
for (ds,t),(b,se) in paper_T2.items():
    r=coef(ds,'party_growth_baseline',t); chk(f'T2 {ds} {t} b',b,r.coefficient,0.0006); chk(f'T2 {ds} {t} se',se,r.robust_se,0.0006)
paper_T6={('Aggregate','post_cu'):(.555,.027),('Senate','post_cu'):(.601,.036),('Presidential','post_cu'):(.499,.016),('Aggregate','republican'):(-.001,.016),('Senate','republican'):(.003,.022),('Presidential','republican'):(-.001,.007),('Aggregate','post_x_republican'):(.131,.060),('Senate','post_x_republican'):(.072,.084),('Presidential','post_x_republican'):(.212,.093),('Aggregate','presidential_office'):(-.061,.059),('Aggregate','presidential_cycle'):(.059,.066),('Senate','presidential_cycle'):(.052,.069),('Presidential','presidential_cycle'):(.450,.231),('Aggregate','const'):(-.011,.042),('Senate','const'):(-.023,.035),('Presidential','const'):(-.446,.231)}
for (ds,t),(b,se) in paper_T6.items():
    r=coef(ds,W,t); chk(f'T6 {ds} {t} b',b,r.coefficient,0.0006); chk(f'T6 {ds} {t} se',se,r.robust_se,0.0006)
paper_T5={('Aggregate','post_x_super_pac'):(.591,.048),('Senate','post_x_super_pac'):(.598,.046),('Presidential','post_x_super_pac'):(.585,.088),('Aggregate','post_x_party_committee'):(-.326,.089),('Senate','post_x_party_committee'):(-.475,.106),('Presidential','post_x_party_committee'):(-.177,.101),('Aggregate','post_x_traditional_pac'):(-.360,.094),('Senate','post_x_traditional_pac'):(-.199,.091),('Presidential','post_x_traditional_pac'):(-.522,.131),('Aggregate','post_x_other_unknown'):(.097,.052),('Senate','post_x_other_unknown'):(.076,.051),('Presidential','post_x_other_unknown'):(.118,.095),('Aggregate','post_x_individual_ie_committee'):(-.002,.006),('Senate','post_x_individual_ie_committee'):(.000,.006),('Presidential','post_x_individual_ie_committee'):(-.004,.010),('Aggregate','const'):(.415,.092),('Senate','const'):(.636,.115),('Presidential','const'):(.193,.096)}
for (ds,t),(b,se) in paper_T5.items():
    r=coef(ds,M,t); chk(f'T5 {ds} {t} b',b,r.coefficient,0.0006); chk(f'T5 {ds} {t} se',se,r.robust_se,0.0006)
su=pd.read_csv('outputs/regressions/regression_model_summaries.csv')
for ds,m,v in [('Aggregate','party_growth_baseline',.597),('Senate','party_growth_baseline',.622),('Presidential','party_growth_baseline',.846),('Aggregate',M,.493),('Senate',M,.659),('Presidential',M,.581),('Aggregate',W,.762),('Senate',W,.715),('Presidential',W,.822)]:
    chk(f'adjR2 {ds} {m[:12]}',v,float(su[(su.dataset==ds)&(su.model==m)].adj_r2.iloc[0]),0.0006)
r=coef('Aggregate',M,'post_x_super_pac'); chk('boot SP lo',.494,r.bootstrap_ci_low,.0006); chk('boot SP hi',.685,r.bootstrap_ci_high,.0006)
r=coef('Aggregate',W,'post_x_republican'); chk('boot T6 agg lo',-.046,r.bootstrap_ci_low,.0006); chk('boot T6 agg hi',.262,r.bootstrap_ci_high,.0006)
r=coef('Presidential',W,'post_x_republican'); chk('boot T6 pres lo',-.509,r.bootstrap_ci_low,.0006); chk('boot T6 pres hi',.874,r.bootstrap_ci_high,.0006)
for ds,b,p in [('Aggregate',-.988,.38),('Senate',-.263,.47),('Presidential',-1.712,.11)]:
    r=coef(ds,'party_growth_with_linear_trend','post_cu'); chk(f'trend post {ds}',b,r.coefficient,.0006); chk(f'trend post p {ds}',p,r.p_value,.006)
for ds,b in [('Aggregate',.537),('Senate',.483),('Presidential',.591)]:
    r=coef(ds,'party_growth_with_linear_trend','cycle_index'); chk(f'trend idx {ds}',b,r.coefficient,.0006)
r=coef('Aggregate','post_cu_superpac_partisan_advantage','republican'); chk('postSP rep b',-.252,r.coefficient,.0006); chk('postSP rep p',.78,r.p_value,.006)
rc=pd.read_csv('outputs/robustness_check/regressions/regression_coefficients.csv')
def rcoef(ds,model,term): return rc[(rc.dataset==ds)&(rc.model==model)&(rc.term==term)].iloc[0]
r=rcoef('Aggregate',W,'post_x_republican'); chk('robust agg interaction',.059,r.coefficient,.0006); chk('robust agg p',.46,r.p_value,.006)
r=rcoef('Presidential',W,'post_x_republican'); chk('robust pres interaction',.058,r.coefficient,.0006); chk('robust pres p',.70,r.p_value,.006)
r=rcoef('Aggregate',M,'post_x_super_pac'); chk('robust SP share',.627,r.coefficient,.0006)
ie=pickle.load(open('outputs/robustness_check/aggregate_processed.pkl','rb')); post=ie[ie.CYCLE_END_YEAR>2010]
g=post.groupby(['BENEFITING_PARTY','COMMITTEE_CATEGORY']).TRANSACTION_AMT.sum()
chk('robust Dem SP+hyb $B',2.36,(g[('Democrat','Super PAC')]+g[('Democrat','Hybrid PAC')])/1e9,.005); chk('robust Rep SP+hyb $B',2.16,(g[('Republican','Super PAC')]+g[('Republican','Hybrid PAC')])/1e9,.005)
pre=ie[ie.CYCLE_END_YEAR<=2010]; chk('robust Rep pre $M',327.5,pre[pre.BENEFITING_PARTY=='Republican'].TRANSACTION_AMT.sum()/1e6,.05)
full=pickle.load(open('outputs/aggregate_processed.pkl','rb'))
v=full[(full.CYCLE_END_YEAR>2010)&(full.CMTE_TP=='V')].groupby('BENEFITING_PARTY').TRANSACTION_AMT.sum()/1e6
chk('V post total $M',588.9,v.sum(),.05); chk('V post Dem $M',561.4,v['Democrat'],.05)
chk('24N $M',22.4,full[full.TRANSACTION_TP=='24N'].TRANSACTION_AMT.sum()/1e6,.05)
p=full[(full.CMTE_ID=='C00495861')&(full.CYCLE_END_YEAR.isin([2012,2016]))].TRANSACTION_AMT.sum()/1e6; chk('Priorities 2012+2016 $M',198.5,p,.05)
bad=[x for x in checks if x[3]!='OK']
print(len(checks),'checks;', len(bad),'mismatches')
for x in bad: print(x)
