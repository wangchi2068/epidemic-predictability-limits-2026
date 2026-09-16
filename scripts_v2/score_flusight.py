from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
FIPS={f'{i:02d}' for i in range(1,57)}
Q23=np.array([.01,.025,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.85,.9,.95,.975,.99])
def wis23(v,y):
 v=np.asarray(v,float)
 if len(v)!=23:return np.nan
 return float(2*np.mean(np.where(y>=v,Q23*(y-v),(1-Q23)*(v-y))))
def read(root):
 fs=sorted(root.glob('*.csv')); a=[]
 for f in fs:
  try:a.append(pd.read_csv(f))
  except Exception:pass
 return pd.concat(a,ignore_index=True) if a else pd.DataFrame()
def score(root,B=2000,block=4,start_date=None,end_date=None):
 t=pd.read_csv(root/'target-hospital-admissions.csv');t.date=pd.to_datetime(t.date);t.location=t.location.astype(str).str.zfill(2);t=t[t.location.isin(FIPS)]; truth=t.set_index(['location','date']).value; rows=[]
 for model in ('ensemble','baseline'):
  fc=read(root/model)
  if fc.empty:continue
  fc.location=fc.location.astype(str).str.zfill(2);fc.reference_date=pd.to_datetime(fc.reference_date)
  fc=fc[(fc.location.isin(FIPS))&(fc.target=='wk inc flu hosp')&(fc.horizon.isin([1,2,3]))&(fc.output_type=='quantile')]
  if start_date: fc=fc[fc.reference_date>=pd.Timestamp(start_date)]
  if end_date: fc=fc[fc.reference_date<=pd.Timestamp(end_date)]
  for (ref,loc,h,end),g in fc.groupby(['reference_date','location','horizon','target_end_date']):
   if (loc,pd.Timestamp(end)) not in truth.index:continue
   g=g.sort_values('output_type_id'); v=g.value.to_numpy(float); lev=g.output_type_id.to_numpy(float)
   if len(v)!=23 or not np.allclose(lev,Q23):continue
   y=float(truth.loc[(loc,pd.Timestamp(end))]); hist=t[(t.location==loc)&(t.date<=pd.Timestamp(ref)-pd.Timedelta(days=7))].sort_values('date'); p=float(hist.iloc[-1].value) if len(hist) else np.nan
   rows.append(dict(model=model,reference_date=ref,location=loc,horizon=int(h),target_end_date=end,truth=y,point=v[11],wis=wis23(v,y),mae=abs(v[11]-y),persistence_mae=abs(p-y) if np.isfinite(p) else np.nan))
 fr=pd.DataFrame(rows)
 if len(fr):
  keys=fr.groupby(['reference_date','location','horizon']).model.nunique(); keys=keys[keys==2].index
  fr=fr.set_index(['reference_date','location','horizon']).loc[keys].reset_index()
 out={'rows':len(fr),'models':sorted(fr.model.unique()) if len(fr) else [],'bootstrap':{'B':B,'block_weeks':block,'unit':'origin_week'},'by_horizon':{}}
 rng=np.random.default_rng(20260914)
 for h,g in fr.groupby('horizon'):
  origins=np.array(sorted(g.reference_date.unique()), dtype='datetime64[ns]'); z_wis=[]; z_mae=[]; z_delta_wis=[]; z_delta_mae=[]
  for _ in range(B):
   if len(origins)==0:break
   starts=rng.integers(0,len(origins),size=max(1,int(np.ceil(len(origins)/block))))
   sampled=np.concatenate([origins[(start+np.arange(block))%len(origins)] for start in starts])[:len(origins)]
   sampled_frames=[]
   for origin in sampled:
    sampled_frames.append(g[g.reference_date==pd.Timestamp(origin)])
   boot=pd.concat(sampled_frames,ignore_index=True)
   z_wis.append(float(boot[boot.model=='ensemble'].wis.mean()))
   z_mae.append(float(boot[boot.model=='ensemble'].mae.mean()))
   paired=boot.pivot_table(index=['reference_date','location'],columns='model',values=['wis','mae'],aggfunc='mean')
   if {'ensemble','baseline'}.issubset(set(paired['wis'].columns)):
    z_delta_wis.append(float((paired['wis']['ensemble']-paired['wis']['baseline']).mean()))
    z_delta_mae.append(float((paired['mae']['ensemble']-paired['mae']['baseline']).mean()))
  model_summary={m:{'rows':int(len(g[g.model==m])),'wis_mean':float(g[g.model==m].wis.mean()),'mae_mean':float(g[g.model==m].mae.mean())} for m in g.model.unique()}
  model_summary['ensemble']['wis_bootstrap_ci95']=[float(np.nanpercentile(z_wis,2.5)),float(np.nanpercentile(z_wis,97.5))] if z_wis else [None,None]
  model_summary['ensemble']['mae_bootstrap_ci95']=[float(np.nanpercentile(z_mae,2.5)),float(np.nanpercentile(z_mae,97.5))] if z_mae else [None,None]
  out['by_horizon'][str(int(h))]={'n_cells':len(g),'n_origins':int(g.reference_date.nunique()),'n_states':int(g.location.nunique()),'by_model':model_summary,'paired_difference':{'wis_mean':float((g[g.model=='ensemble'].wis.mean()-g[g.model=='baseline'].wis.mean())),'mae_mean':float((g[g.model=='ensemble'].mae.mean()-g[g.model=='baseline'].mae.mean())),'wis_bootstrap_ci95':[float(np.nanpercentile(z_delta_wis,2.5)),float(np.nanpercentile(z_delta_wis,97.5))] if z_delta_wis else [None,None],'mae_bootstrap_ci95':[float(np.nanpercentile(z_delta_mae,2.5)),float(np.nanpercentile(z_delta_mae,97.5))] if z_delta_mae else [None,None]}}
 return out,fr
def main():
 p=argparse.ArgumentParser();p.add_argument('release_dir',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--csv',type=Path);p.add_argument('--B',type=int,default=2000);p.add_argument('--start-date');p.add_argument('--end-date');a=p.parse_args();r,f=score(a.release_dir,a.B,4,a.start_date,a.end_date);a.output.write_text(json.dumps(r,indent=2,default=str),encoding='utf-8');f.to_csv(a.csv,index=False) if a.csv else None;print(json.dumps(r,indent=2,default=str))
if __name__=='__main__':main()
