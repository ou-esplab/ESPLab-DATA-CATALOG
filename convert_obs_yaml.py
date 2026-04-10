import yaml
import json

# Read in the YAML catalog
with open("catalogs/obs.yaml") as f:
    data = yaml.safe_load(f)

# Write catalog to JSON
with open("docs/obs.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ converted obs.yaml to docs/obs.json")

