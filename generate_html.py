import os
import yaml

CATALOG_DIR = "catalogs"
OUTPUT_DIR = "docs"

def load_catalog(yaml_file):
    with open(yaml_file) as f:
        catalog = yaml.safe_load(f)
    sources = catalog.get("sources", {})
    entries = []
    for key, value in sources.items():
        entries.append({
            "name": key,
            "description": value.get("description", "No description"),
            "metadata": value.get("metadata", {}),
            "args": value.get("args", {}),
        })
    return entries

def generate_filtered_html(entries, output_path, title):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    details {{ margin-bottom: 10px; }}
    summary {{ font-weight: bold; cursor: pointer; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
"""

    for entry in entries:
        name = entry.get("name", "unknown")
        metadata = entry.get("metadata", {})
        urlpath = entry.get("args", {}).get("urlpath", "unknown")
        meta_html = "<ul>"
        for k, v in metadata.items():
            meta_html += f"<li><strong>{k}</strong>: {v}</li>"
        meta_html += f"<li><strong>urlpath</strong>: {urlpath}</li></ul>"

        html_content += f"""<details>
  <summary>{name}</summary>
  {meta_html}
</details>
"""

    html_content += """
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"✅ wrote {output_path} with {len(entries)} entries.")

def main():
    obs_catalog = os.path.join(CATALOG_DIR, "obs.yaml")
    reanalysis_catalog = os.path.join(CATALOG_DIR, "reanalysis.yaml")

    # load and generate obs
    obs_entries = load_catalog(obs_catalog)
    obs_output = os.path.join(OUTPUT_DIR, "obs.html")
    generate_filtered_html(obs_entries, obs_output, title="Observational Data Catalog")

    # load and generate reanalysis
    reanalysis_entries = load_catalog(reanalysis_catalog)
    reanalysis_output = os.path.join(OUTPUT_DIR, "reanalysis.html")
    generate_filtered_html(reanalysis_entries, reanalysis_output, title="Reanalysis Data Catalog")

if __name__ == "__main__":
    main()

