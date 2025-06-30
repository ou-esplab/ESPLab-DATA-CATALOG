import os
import json
import yaml

OUTPUT_DIR = "docs"  # adjust as needed
OBS_JSON = os.path.join(OUTPUT_DIR, "obs.json")
REANALYSIS_JSON = os.path.join(OUTPUT_DIR, "reanalysis.json")

OU_BLUE = "#0076A8"
OU_ORANGE = "#EE7624"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def generate_dropdown(id_, label, options):
    options_html = ['<option value="">-- Select --</option>']
    for opt in sorted(options):
        options_html.append(f'<option value="{opt}">{opt}</option>')
    return f'''
    <label for="{id_}">{label}:</label>
    <select id="{id_}" name="{id_}">
      {''.join(options_html)}
    </select>
    '''

def generate_page(title, dropdowns, datasets, output_file):
    dropdown_html = "\n".join(dropdowns)

    # Dataset items with data- attributes and initially hidden
    dataset_items_html = []
    for key, info in datasets.items():
        # parse keys like 'obs/gridded/atm/precip/daily/CMORPH'
        parts = key.split('/')
        # Depending on catalog, obs or reanalysis, keys differ. 
        # Here for obs: parts = ['obs','gridded','atm','precip','daily','CMORPH']
        # For reanalysis: ['reanalysis','era5','daily','z500','CPC-UNI-GLOBAL']
        # We'll make data attributes based on available parts:
        attrs = {}
        if parts[0] == 'obs':
            # obs/gridded/<domain>/<variable>/<temporal>/<dataset>
            attrs['domain'] = parts[2]
            attrs['variable'] = parts[3]
            attrs['temporal'] = parts[4]
            attrs['dataset'] = parts[5]
        elif parts[0] == 'reanalysis':
            # reanalysis/<dataset>/<temporal>/<variable>
            attrs['dataset'] = parts[1]
            attrs['temporal'] = parts[2]
            attrs['variable'] = parts[3]
        else:
            # fallback all as empty
            attrs = {'domain':'', 'variable':'', 'temporal':'', 'dataset':''}

        meta = info.get("metadata", {})
        description = meta.get("long_name", info.get("description", "No description"))
        units = meta.get("units", "unknown")
        date_range = meta.get("date_range", "unknown")
        n_files = meta.get("n_files", "unknown")
        data_loc = meta.get("data_location", "unknown")

        # Compose metadata html visible by default
        meta_html = f'''
        <div style="margin-left:1em; font-size:0.9em; color:#444;">
          <div><b>Description:</b> {description}</div>
          <div><b>Units:</b> {units}</div>
          <div><b>Date Range:</b> {date_range}</div>
          <div><b>Files:</b> {n_files}</div>
          <div><b>Data Location:</b> {data_loc}</div>
        </div>
        '''

        data_attrs_str = ' '.join([f'data-{k}="{v}"' for k,v in attrs.items()])

        dataset_html = f'''
        <div class="dataset-item" {data_attrs_str} style="display:none; padding: 0.5em; border-bottom:1px solid #ddd;">
          <b>{attrs.get("dataset","Unknown Dataset")}</b>
          {meta_html}
        </div>
        '''
        dataset_items_html.append(dataset_html)

    # JavaScript for filtering datasets on dropdown change
    js_code = '''
    function filterDatasets() {
      const domain = document.getElementById('domain-select') ? document.getElementById('domain-select').value : null;
      const variable = document.getElementById('variable-select') ? document.getElementById('variable-select').value : null;
      const temporal = document.getElementById('temporal-select') ? document.getElementById('temporal-select').value : null;
      const dataset = document.getElementById('dataset-select') ? document.getElementById('dataset-select').value : null;

      const datasets = document.querySelectorAll('.dataset-item');
      datasets.forEach(ds => {
        let show = true;
        if(domain && ds.dataset.domain !== domain) show = false;
        if(variable && ds.dataset.variable !== variable) show = false;
        if(temporal && ds.dataset.temporal !== temporal) show = false;
        if(dataset && ds.dataset.dataset !== dataset) show = false;

        ds.style.display = show ? 'block' : 'none';
      });
    }

    document.querySelectorAll('select').forEach(sel => {
      sel.addEventListener('change', filterDatasets);
    });

    // Initially hide all
    filterDatasets();
    '''

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{title}</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 2em;
          background: #f9f9f9;
          color: #222;
        }}
        h1 {{
          color: {OU_BLUE};
          border-bottom: 3px solid {OU_ORANGE};
          padding-bottom: 0.2em;
        }}
        label {{
          margin-right: 0.5em;
          font-weight: bold;
        }}
        select {{
          margin-right: 1.5em;
          padding: 0.3em;
          border: 1px solid #ccc;
          border-radius: 4px;
          min-width: 150px;
        }}
        .dataset-item:hover {{
          background-color: #eef6fc;
        }}
      </style>
    </head>
    <body>
      <h1>{title}</h1>
      <div id="filters">
        {dropdown_html}
      </div>
      <hr/>
      <div id="datasets">
        {''.join(dataset_items_html)}
      </div>
      <script>{js_code}</script>
    </body>
    </html>
    '''

    with open(output_file, "w") as f:
        f.write(html)
    print(f"Generated {output_file}")

def main():
    # Load catalogs
    obs = load_json(OBS_JSON)
    reanalysis = load_json(REANALYSIS_JSON)

    # Gather unique values for obs dropdowns
    obs_sources = obs.get("sources", {})
    domains = set()
    variables = set()
    temporals = set()
    datasets = set()

    for k in obs_sources.keys():
        parts = k.split('/')
        if len(parts) == 6 and parts[0] == 'obs':
            domains.add(parts[2])
            variables.add(parts[3])
            temporals.add(parts[4])
            datasets.add(parts[5])

    # For reanalysis dropdowns
    re_sources = reanalysis.get("sources", {})
    re_datasets = set()
    re_temporals = set()
    re_variables = set()

    for k in re_sources.keys():
        parts = k.split('/')
        if len(parts) == 4 and parts[0] == 'reanalysis':
            re_datasets.add(parts[1])
            re_temporals.add(parts[2])
            re_variables.add(parts[3])

    # Generate obs page
    obs_dropdowns = [
        generate_dropdown("domain-select", "Domain", domains),
        generate_dropdown("variable-select", "Variable", variables),
        generate_dropdown("temporal-select", "Temporal Resolution", temporals),
        generate_dropdown("dataset-select", "Dataset", datasets)
    ]
    generate_page("ESPLab Data Catalog - Observations", obs_dropdowns, obs_sources, os.path.join(OUTPUT_DIR, "obs.html"))

    # Generate reanalysis page
    reanalysis_dropdowns = [
        generate_dropdown("dataset-select", "Dataset", re_datasets),
        generate_dropdown("temporal-select", "Temporal Resolution", re_temporals),
        generate_dropdown("variable-select", "Variable", re_variables)
    ]
    generate_page("ESPLab Data Catalog - Reanalysis", reanalysis_dropdowns, re_sources, os.path.join(OUTPUT_DIR, "reanalysis.html"))

if __name__ == "__main__":
    main()

