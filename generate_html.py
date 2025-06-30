import os
import json

OUTPUT_DIR = "docs"

def generate_dataset_html(name, meta):
    description = meta.get('description', 'No description available')
    metadata = meta.get('metadata', {})
    long_name = metadata.get('long_name', 'unknown')
    units = metadata.get('units', 'unknown')
    date_range = metadata.get('date_range', 'unknown')
    n_files = metadata.get('n_files', 'unknown')
    data_location = metadata.get('data_location', 'unknown')

    html = f"""
    <div class="dataset-entry" style="margin-bottom:1em; padding:0.5em; border-bottom:1px solid #ccc;">
      <strong>{name}</strong><br>
      <div class="metadata" style="margin-left:1em;">
        <b>Description:</b> {description}<br>
        <b>Date Range:</b> {date_range}<br>
        <b>Units:</b> {units}<br>
        <b>Files:</b> {n_files}<br>
        <b>Data Location:</b> {data_location}<br>
      </div>
    </div>
    """
    return html

def generate_html(catalog_json_path, output_html_path, page_title):
    with open(catalog_json_path) as f:
        catalog = json.load(f)

    sources = catalog.get("sources", {})
    # sort keys for consistent order
    sorted_keys = sorted(sources.keys())

    # Generate HTML entries for all datasets
    entries_html = ""
    for key in sorted_keys:
        meta = sources[key]
        # For display, show only the dataset folder name (last part of the key)
        dataset_name = os.path.basename(key)
        entries_html += generate_dataset_html(dataset_name, meta)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>{page_title}</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 2em;
          background: #f9f9f9;
          color: #222;
        }}
        h1 {{
          color: #004080;
        }}
        .dataset-entry {{
          background: white;
          border-radius: 4px;
          box-shadow: 0 0 5px #ccc;
          padding: 10px;
          margin-bottom: 10px;
        }}
        .metadata b {{
          color: #004080;
        }}
      </style>
    </head>
    <body>
      <h1>{page_title}</h1>
      {entries_html}
    </body>
    </html>
    """

    with open(output_html_path, "w") as f:
        f.write(html_content)
    print(f"✅ Generated {output_html_path}")

if __name__ == "__main__":
    # Adjust these paths as needed
    obs_json = os.path.join(OUTPUT_DIR, "obs.json")
    reanalysis_json = os.path.join(OUTPUT_DIR, "reanalysis.json")

    generate_html(obs_json, os.path.join(OUTPUT_DIR, "obs.html"), "ESPLab Observational Data Catalog")
    generate_html(reanalysis_json, os.path.join(OUTPUT_DIR, "reanalysis.html"), "ESPLab Reanalysis Data Catalog")

