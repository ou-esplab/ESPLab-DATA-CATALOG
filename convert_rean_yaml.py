import yaml
import json

with open("catalogs/reanalysis.yaml") as f:
    data = yaml.safe_load(f)

with open("docs/reanalysis.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ converted reanalysis.yaml to docs/reanalysis.json")

