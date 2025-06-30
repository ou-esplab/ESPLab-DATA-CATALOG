import yaml
import json

def process_obs(yaml_file, json_file):
    with open(yaml_file) as f:
        catalog = yaml.safe_load(f)
    results = []
    for key, val in catalog.get('sources', {}).items():
        parts = key.split('/')
        if len(parts) < 5:
            continue
        _, _, domain, variable, temporal_res, dataset = parts + [""]*(6 - len(parts))
        results.append({
            "domain": domain,
            "variable": variable,
            "temporal_resolution": temporal_res,
            "dataset": dataset,
            "metadata": val.get('metadata', {}),
            "urlpath": val['args']['urlpath']
        })
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Wrote {json_file}")

def process_reanalysis(yaml_file, json_file):
    with open(yaml_file) as f:
        catalog = yaml.safe_load(f)
    results = []
    for key, val in catalog.get('sources', {}).items():
        parts = key.split('/')
        if len(parts) < 3:
            continue
        _, dataset, temporal_res, variable = parts + [""]*(4 - len(parts))
        results.append({
            "dataset": dataset,
            "temporal_resolution": temporal_res,
            "variable": variable,
            "metadata": val.get('metadata', {}),
            "urlpath": val['args']['urlpath']
        })
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Wrote {json_file}")

if __name__ == "__main__":
    process_obs("catalogs/obs.yaml", "docs/obs.json")
    process_reanalysis("catalogs/reanalysis.yaml", "docs/reanalysis.json")

