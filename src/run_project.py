"""Deterministic synthetic paint-shop demonstration. Run from any directory."""
from pathlib import Path
import json, sqlite3, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, average_precision_score, brier_score_loss
import joblib
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'outputs'; SAP=ROOT/'data/sap_import'
for d in [RAW,OUT,SAP]: d.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(42)
n=3600
start=pd.date_range('2025-01-01',periods=n,freq='h')
b=pd.DataFrame({'BATCH_ID':[f'B{i:05}' for i in range(n)],'START_TIME':start,'END_TIME':start+pd.Timedelta(minutes=45),'LINE_ID':np.array(['L1','L2','L3'])[np.arange(n)%3],'SHIFT_ID':np.where(start.hour<8,'Night',np.where(start.hour<16,'Day','Evening')),'MODEL_ID':rng.choice(['Sedan','SUV','Hatchback'],n)})
b['MACHINE_ID']=b.LINE_ID.map({'L1':'M1','L2':'M2','L3':'M3'}); b['DATE_ID']=start.strftime('%Y-%m-%d'); b['PRODUCTION_VOLUME']=rng.integers(8,21,n)
temp=rng.normal(24,3,n); humidity=rng.normal(52,10,n); pressure=rng.normal(2.5,.3,n)
prob=1/(1+np.exp(-(-3.0+.5*np.abs(temp-24)+.065*np.maximum(humidity-55,0)+2*np.abs(pressure-2.5))))
y=rng.binomial(1,prob)
ins=pd.DataFrame({'INSPECTION_ID':[f'I{i:05}' for i in range(n)],'BATCH_ID':b.BATCH_ID,'INSPECTION_TIME':b.END_TIME+pd.Timedelta(minutes=30),'FAILED':y,'DEFECT_CATEGORY':np.where(y==1,rng.choice(['Orange peel','Blister','Dust inclusion'],n),'None')})
# Ten samples per batch; all readings precede scoring at batch completion.
s=pd.DataFrame({'READING_ID':[f'S{i:06}' for i in range(n*10)],'BATCH_ID':np.repeat(b.BATCH_ID.to_numpy(),10),'TIMESTAMP':np.repeat(start.to_numpy(),10)+np.tile(np.arange(10)*4,n).astype('timedelta64[m]'),'TEMPERATURE_C':np.repeat(temp,10)+rng.normal(0,.5,n*10),'HUMIDITY_PCT':np.repeat(humidity,10)+rng.normal(0,1,n*10),'PRESSURE_BAR':np.repeat(pressure,10)+rng.normal(0,.03,n*10)})
s.loc[rng.choice(len(s),500,replace=False),'TEMPERATURE_C']=np.nan
s.loc[rng.choice(len(s),80,replace=False),'HUMIDITY_PCT']=150
ix=np.arange(0,n,7)
e=pd.DataFrame({'EVENT_ID':[f'E{i:05}' for i in ix],'MACHINE_ID':b.MACHINE_ID.iloc[ix].to_numpy(),'DOWNTIME_START':b.END_TIME.iloc[ix].to_numpy(),'EVENT_CATEGORY':rng.choice(['Cleaning','Maintenance','Fault'],len(ix))})
e['DOWNTIME_END']=e.DOWNTIME_START+pd.to_timedelta(rng.integers(5,50,len(ix)),unit='m'); e['DATE_ID']=e.DOWNTIME_START.dt.strftime('%Y-%m-%d')
for name,df in [('production',b),('sensors',s),('inspections',ins),('machine_events',e)]: df.to_csv(RAW/f'{name}.csv',index=False)
checks=[]
def check(name,ok):
 checks.append({'check':name,'passed':bool(ok)})
 if not ok: raise ValueError(name)
for name,df,key in [('production',b,'BATCH_ID'),('sensors',s,'READING_ID'),('inspections',ins,'INSPECTION_ID'),('events',e,'EVENT_ID')]:
 check(name+' unique keys',df[key].is_unique); check(name+' nonnull keys',df[key].notna().all())
check('inspection batch unique',ins.BATCH_ID.is_unique)
check('inspection foreign keys',ins.BATCH_ID.isin(b.BATCH_ID).all()); check('sensor foreign keys',s.BATCH_ID.isin(b.BATCH_ID).all()); check('event machine keys',e.MACHINE_ID.isin(b.MACHINE_ID).all())
check('production timestamps', (b.END_TIME>b.START_TIME).all()); check('downtime timestamps',(e.DOWNTIME_END>e.DOWNTIME_START).all()); check('inspection after completion',(ins.INSPECTION_TIME.to_numpy()>=b.END_TIME.to_numpy()).all()); check('positive volume',(b.PRODUCTION_VOLUME>0).all())
sc=s.merge(b[['BATCH_ID','START_TIME','END_TIME']],on='BATCH_ID',validate='many_to_one')
check('sensors available at score time',((sc.TIMESTAMP>=sc.START_TIME)&(sc.TIMESTAMP<=sc.END_TIME)).all())
clean=s.copy(); invalid={}
for col,lo,hi in [('TEMPERATURE_C',10,45),('HUMIDITY_PCT',0,100),('PRESSURE_BAR',.5,5)]:
 mask=~clean[col].between(lo,hi); invalid[col]=int(mask.sum()); clean.loc[mask,col]=np.nan
features=['TEMPERATURE_C','HUMIDITY_PCT','PRESSURE_BAR']
agg=clean.groupby('BATCH_ID')[features].mean().reset_index()
f=b.merge(agg,on='BATCH_ID',validate='one_to_one').merge(ins,on='BATCH_ID',validate='one_to_one')
check('source target counts',len(f)==len(b)); check('binary labels',f.FAILED.isin([0,1]).all())
# Chronological train/validation/test: preprocessing fitted only on training data.
a,z=int(n*.6),int(n*.8); train=f.iloc[:a]; val=f.iloc[a:z]; test=f.iloc[z:]
check('split chronology',train.END_TIME.max()<val.END_TIME.min()<test.END_TIME.min())
model=make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),LogisticRegression(class_weight='balanced',max_iter=1000,random_state=42))
model.fit(train[features],train.FAILED)
vp=model.predict_proba(val[features])[:,1]
thresholds=np.arange(.1,.91,.05); threshold=float(max(thresholds,key=lambda t:f1_score(val.FAILED,vp>=t,zero_division=0)))
baseline=DummyClassifier(strategy='prior').fit(train[features],train.FAILED)
def evaluate(name,probs,t):
 pred=probs>=t
 return {'model':name,'threshold':t,'precision':precision_score(test.FAILED,pred,zero_division=0),'recall':recall_score(test.FAILED,pred,zero_division=0),'f1':f1_score(test.FAILED,pred,zero_division=0),'average_precision':average_precision_score(test.FAILED,probs),'brier_score':brier_score_loss(test.FAILED,probs),'confusion_matrix_TN_FP_FN_TP':confusion_matrix(test.FAILED,pred,labels=[0,1]).ravel().tolist()}
tp=model.predict_proba(test[features])[:,1]
metrics=[evaluate('logistic_regression',tp,threshold),evaluate('prior_baseline',baseline.predict_proba(test[features])[:,1],.5)]
f['RISK_SCORE']=model.predict_proba(f[features])[:,1]; f['RISK_FLAG']=(f.RISK_SCORE>=threshold).astype(int); f['SCORE_TIME']=f.END_TIME
f['SPLIT']=np.where(np.arange(n)<a,'TRAIN',np.where(np.arange(n)<z,'VALIDATION','TEST'))
f['SCORE_SCOPE']=np.where(f.SPLIT=='TEST','HELD_OUT','DEVELOPMENT_ONLY')
f['INSPECTED_BATCHES']=1; f['FAILED_BATCHES']=f.FAILED; f['FIRST_PASS_BATCHES']=1-f.FAILED
f['INSPECTION_STATUS']=np.where(f.FAILED==1,'Fail','Pass')
f.to_csv(SAP/'FACT_BATCH_QUALITY.csv',index=False)
e['DOWNTIME_MINUTES']=(e.DOWNTIME_END-e.DOWNTIME_START).dt.total_seconds()/60
e.to_csv(SAP/'FACT_DOWNTIME.csv',index=False)
for name,cols in [('DIM_MACHINE',['MACHINE_ID','LINE_ID']),('DIM_SHIFT',['SHIFT_ID']),('DIM_MODEL',['MODEL_ID']),('DIM_DATE',['DATE_ID']),('DIM_INSPECTION',['INSPECTION_STATUS'])]: f[cols].drop_duplicates().to_csv(SAP/f'{name}.csv',index=False)
with sqlite3.connect(OUT/'manufacturing.db') as con:
 f.to_sql('FACT_BATCH_QUALITY',con,index=False,if_exists='replace'); e.to_sql('FACT_DOWNTIME',con,index=False,if_exists='replace')
 for raw_name,raw_df in [('PRODUCTION',b),('SENSORS',s),('INSPECTIONS',ins),('EVENTS',e)]:
  raw_df.to_sql('RAW_'+raw_name,con,index=False,if_exists='replace')
 con.executescript((ROOT/'sql/source_transformation.sql').read_text())
 source=pd.read_sql_query('SELECT * FROM V_SOURCE_BATCH',con)
 check('SQL source join count',len(source)==len(b))
 check('SQL source sensor reconciliation',np.allclose(source[features].to_numpy(),f[features].to_numpy(),equal_nan=True))
 sql=(ROOT/'sql/local_analytics.sql').read_text(); con.executescript(sql)
 daily=pd.read_sql_query('SELECT * FROM V_DAILY_QUALITY',con); daily.to_csv(OUT/'daily_quality.csv',index=False)
 check('SQL inspected batch reconciliation',int(daily.INSPECTED_BATCHES.sum())==n)
 check('SQL failures reconciliation',int(daily.FAILED_BATCHES.sum())==int(y.sum()))
check('risk bounds',f.RISK_SCORE.between(0,1).all()); check('heldout count',(f.SCORE_SCOPE=='HELD_OUT').sum()==len(test))
f[features+['FAILED']].corr().to_csv(OUT/'correlations.csv')
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False)
(OUT/'model_evaluation.json').write_text(json.dumps({'synthetic':True,'features':features,'train_rows':len(train),'validation_rows':len(val),'test_rows':len(test),'threshold_selection':'validation F1; test untouched','metrics':metrics,'invalid_or_missing_readings':invalid},indent=2))
joblib.dump(model,OUT/'quality_model.joblib')
fig,axes=plt.subplots(1,2,figsize=(11,4)); cm=confusion_matrix(test.FAILED,tp>=threshold,labels=[0,1]); axes[0].imshow(cm,cmap='Blues')
for (i,j),v in np.ndenumerate(cm): axes[0].text(j,i,str(v),ha='center',va='center')
axes[0].set(xticks=[0,1],yticks=[0,1],xlabel='Predicted (0 pass, 1 fail)',ylabel='Actual',title='Held-out confusion matrix')
axes[1].hist(tp,bins=20,color='#187c92'); axes[1].axvline(threshold,color='red'); axes[1].set(title='Held-out estimated risk',xlabel='Score',ylabel='Batches'); fig.tight_layout(); fig.savefig(OUT/'model_evaluation.png',dpi=150); plt.close(fig)
(OUT/'RUN_SUMMARY.md').write_text(f'# Synthetic paint-shop run\n\n{n:,} batches; {len(s):,} readings; {len(e)} downtime events.\n\n{len(checks)} validation checks passed. Held-out F1: {metrics[0]["f1"]:.3f}; baseline: {metrics[1]["f1"]:.3f}.\n\nScores are prioritisation aids. Synthetic performance is not evidence of factory performance. Development scores are not held-out evidence.\n')
# Auto-generated dictionary covers every exported column and grain.
lines=['# Export data dictionary','', 'All source data is synthetic. ISO timestamps use a fictional UTC plant clock.','']
meaning={'RISK_SCORE':'Uncalibrated model probability-like score, 0–1; not proof of defect','FAILED':'Initial batch inspection label: 1 fail, 0 pass','PRODUCTION_VOLUME':'Vehicles in batch; vehicle-level defect counts unavailable','SCORE_SCOPE':'HELD_OUT for test; DEVELOPMENT_ONLY otherwise','DATE_ID':'Production date on batch fact; event start date on downtime fact','TEMPERATURE_C':'Mean valid pre-completion sensor temperature, Celsius','HUMIDITY_PCT':'Mean valid pre-completion relative humidity, percent','PRESSURE_BAR':'Mean valid pre-completion pressure, bar'}
for path in sorted(SAP.glob('*.csv')):
 df=pd.read_csv(path); lines += [f'## {path.stem}', '', 'Grain: '+('one row per batch' if path.stem=='FACT_BATCH_QUALITY' else 'one row per event' if path.stem=='FACT_DOWNTIME' else 'one row per dimension key'),'', '| Column | Type | Definition |','|---|---|---|']
 for col in df: lines.append(f'| {col} | {df[col].dtype} | {meaning.get(col,col.replace("_"," ").lower())} |')
 lines.append('')
(ROOT/'docs/DATA_DICTIONARY.md').write_text('\n'.join(lines))
print(f'SUCCESS: {n:,} batches; {len(checks)} checks passed. See outputs/RUN_SUMMARY.md')
