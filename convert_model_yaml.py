import yaml
import json

# Read the YAML catalog
with open("catalogs/model.yaml", "r") as f:
    data = yaml.safe_load(f)

# Write to JSON
with open("docs/model.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Converted model.yaml to model.json")

