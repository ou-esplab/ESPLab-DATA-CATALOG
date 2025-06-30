import os
import json
import yaml

# Change these paths as needed
OBS_JSON = "docs/obs.json"
REANALYSIS_JSON = "docs/reanalysis.json"
OUTPUT_DIR = "docs"

# Use University of Oklahoma colors
OU_PRIMARY = "#c9000d"  # OU Crimson Red
OU_SECONDARY = "#fdbb30"  # OU Gold
OU_BG = "#ffffff"
OU_TEXT = "#000000"

def load_json(json_path):
    with open(json_path) as f:
        return json.load(f)

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    print(f"Written: {path}")

def generate_index_page():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    background-color: {OU_BG};
    color: {OU_TEXT};
    margin: 20px;
  }}
  h1 {{
    color: {OU_PRIMARY};
    border-bottom: 3px solid {OU_SECONDARY};
    padding-bottom: 5px;
  }}
  .tab {{
    overflow: hidden;
    border-bottom: 2px solid {OU_PRIMARY};
  }}
  .tab button {{
    background-color: inherit;
    border: none;
    outline: none;
    cursor: pointer;
    padding: 14px 20px;
    transition: 0.3s;
    font-size: 16px;
    color: {OU_PRIMARY};
  }}
  .tab button:hover {{
    background-color: {OU_SECONDARY};
    color: #000;
  }}
  .tab button.active {{
    border-bottom: 3px solid {OU_PRIMARY};
    font-weight: bold;
  }}
  .tabcontent {{
    display: none;
    padding: 15px 0px;
  }}
</style>
</head>
<body>
  <h1>ESPLab Data Catalog</h1>
  <div class="tab">
    <button class="tablinks active" onclick="openTab(event, 'obs')">Observations</button>
    <button class="tablinks" onclick="openTab(event, 'reanalysis')">Reanalysis</button>
  </div>

  <div id="obs" class="tabcontent" style="display:block;">
    <iframe src="obs/index.html" style="border:none; width:100%; height:800px;"></iframe>
  </div>

  <div id="reanalysis" class="tabcontent">
    <iframe src="reanalysis/index.html" style="border:none; width:100%; height:800px;"></iframe>
  </div>

<script>
function openTab(evt, tabName) {{
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {{
    tabcontent[i].style.display = "none";
  }}
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {{
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }}
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}}
</script>

</body>
</html>
"""
    write_file(os.path.join(OUTPUT_DIR, "index.html"), html)

def generate_data_page(data_json_path, output_subdir, dropdown_fields):
    data = load_json(data_json_path)
    dropdown_html = ""
    for field in dropdown_fields:
        options = sorted(set(entry.get(field, "Unknown") for entry in data["sources"].values()))
        dropdown_html += f'<label for="{field}-select" style="font-weight:600;">{field.replace("_"," ").title()}: </label>'
        dropdown_html += f'<select id="{field}-select"><option value="">-- Select {field} --</option>'
        for opt in options:
            dropdown_html += f'<option value="{opt}">{opt}</option>'
        dropdown_html += '</select><br/><br/>'

    datasets_html = ""
    for key, entry in data["sources"].items():
        meta = entry.get("metadata", {})
        desc = meta.get("long_name", "No description")
        units = meta.get("units", "unknown")
        date_range = meta.get("date_range", "unknown")
        n_files = meta.get("n_files", "?")
        location = meta.get("data_location", "unknown")

        # Build data- attributes string safely for dropdown fields
        data_attrs = " ".join(
            f'data-{field}="{entry.get(field, "")}"' for field in dropdown_fields
        )

        datasets_html += f'''
<div class="dataset" {data_attrs}>
  <strong>{key.split("/")[-1]}</strong><br/>
  <em>{desc}</em><br/>
  <small>Units: {units} | Date Range: {date_range} | Files: {n_files}</small><br/>
  <small>Location: {location}</small>
</div>
<hr/>
'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ESPLab Data Catalog - {output_subdir.title()}</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    background-color: {OU_BG};
    color: {OU_TEXT};
    margin: 20px;
  }}
  h2 {{
    color: {OU_PRIMARY};
    border-bottom: 3px solid {OU_SECONDARY};
    padding-bottom: 5px;
  }}
  label {{
    font-weight: 600;
  }}
  select {{
    font-size: 14px;
    padding: 4px;
    margin-right: 10px;
  }}
  .dataset {{
    padding: 10px 0;
  }}
  hr {{
    border: 0;
    border-top: 1px solid #ccc;
  }}
</style>
</head>
<body>
  <h2>{output_subdir.title()} Data Catalog</h2>
  <div id="filters">
    {dropdown_html}
  </div>
  <div id="datasets">
    {datasets_html}
  </div>

<script>
const filters = {json.dumps(dropdown_fields)};
const selects = {{}};
filters.forEach(field => {{
  selects[field] = document.getElementById(field + '-select');
}});

function filterDatasets() {{
  const datasets = document.querySelectorAll('.dataset');
  datasets.forEach(ds => {{
    let visible = true;
    filters.forEach(field => {{
      const filterVal = selects[field].value;
      if (filterVal && ds.getAttribute('data-' + field) !== filterVal) {{
        visible = false;
      }}
    }});
    ds.style.display = visible ? 'block' : 'none';
  }});
}}

filters.forEach(field => {{
  selects[field].addEventListener('change', filterDatasets);
}});

filterDatasets();
</script>
</body>
</html>
"""

    output_path = os.path.join(OUTPUT_DIR, output_subdir, "index.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    write_file(output_path, html)

def main():
    generate_index_page()

    # Observations dropdown order: Domain, Dataset, Temporal Resolution, Variable
    generate_data_page(OBS_JSON, "obs", ["domain", "dataset", "temporal_resolution", "variable"])

    # Reanalysis dropdown order: Dataset, Temporal Resolution, Variable
    generate_data_page(REANALYSIS_JSON, "reanalysis", ["dataset", "temporal_resolution", "variable"])

if __name__ == "__main__":
    main()

