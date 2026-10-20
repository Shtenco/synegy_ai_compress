"""Merges verified frozen 69, active Tier-1 V2 reruns and fresh world-codec benchmarks.
Do not treat registered frozen rows as fresh executions. No silent substitution.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math,statistics,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def write_rows(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:return
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def normalize(rec,status):
    return {'engine':str(rec.get('engine') or rec.get('profile') or rec.get('name') or ''),
            'family':rec.get('family','historical'),
            'geo_mean_ratio':rec.get('geomean_ratio') or rec.get('geometric_mean_ratio'),
            'aggregate_ratio':rec.get('ratio_aggregate'),
            'run_class':status,'data_count':rec.get('data_count') or rec.get('datasets'),
            'pass_rows':rec.get('passed'),'run_sha256':rec.get('source_sha256','')}

def merge(out,world_csv,current_csv=None):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'compression_lab'))
    from frozen_tier1_summary import load_frozen_tier1_summary, SOURCE_ARTIFACT_SHA256,SOURCE_COMMIT
    frozen=load_frozen_tier1_summary()
    prev=[normalize(x,'FROZEN_VERIFIED_20260730_NOT_RERUN') for x in frozen['summary']]
    fresh=[]
    if current_csv and Path(current_csv).exists():
        with open(current_csv,encoding='utf-8') as f:
            native=json.load(f)['current_summary'] if str(current_csv).endswith('.json') else list(csv.DictReader(f))
        fresh=[normalize(x,'FRESH_SHTENCO_REEXECUTED') for x in native]
    else:
        from shtenco_tier1_engines import tier1_engine_suite
        from shtenco_tier1_v21 import tier1_v21_engine_suite
        for name,family,e in tier1_engine_suite()+tier1_v21_engine_suite():
            fresh.append({'engine':name,'family':family,'geo_mean_ratio':None,'aggregate_ratio':None,'run_class':'ACTIVE_REGISTERED_NOT_RERUN','data_count':None,'pass_rows':None,'run_sha256':''})
    byname={x['engine']:x for x in prev};byname.update({x['engine']:x for x in fresh})
    s_old=len(byname)
    with open(world_csv,encoding='utf-8') as f:
        world=[normalize(x,'FRESH_WORLD_BASELINE_20261020') for x in csv.DictReader(f)]
    for x in world:
        if x['engine'] in byname:
            raise AssertionError('World baseline collides with legacy name: '+x['engine'])
        byname[x['engine']]=x
    data=list(byname.values());data.sort(key=lambda x:(x['run_class'],x['engine']))
    write_rows(out,data)
    return {'frozen_systems':len(prev),'active_profiles':len(fresh),'unique_shtenco':s_old,'fresh_world_baselines':len(world),'unique_total':len(data),'reference_artifact_sha256':SOURCE_ARTIFACT_SHA256,'source_commit':SOURCE_COMMIT,'fresh_shtenco_benchmark_available':bool(current_csv and Path(current_csv).exists())}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--world',required=True);p.add_argument('--current',default=None);a=p.parse_args();o=Path(a.out);o.mkdir(parents=True,exist_ok=True)
    x=merge(o/'all_80plus_registry_with_provenance.csv',a.world,a.current)
    (o/'merge_metadata.json').write_text(json.dumps(x,indent=2,ensure_ascii=False));print(json.dumps(x,indent=2))
if __name__=='__main__':main()