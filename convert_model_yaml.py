import yaml
import json

# Read in the YAML catalog
with open("catalogs/model.yaml", "r") as f:
    data = yaml.safe_load(f)

# Write catalog to JSON
with open("docs/model.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Converted model.yaml to model.json")

