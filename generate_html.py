import os
import yaml
import json

OUTPUT_DIR = "docs"  # Github Pages root folder
OBS_YAML = "catalogs/obs.yaml"
REAN_YAML = "catalogs/reanalysis.yaml"

def yaml_to_json(yaml_path, json_path):
    with open(yaml_path, 'r') as f:
        catalog = yaml.safe_load(f)
    with open(json_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    print(f"✅ Wrote JSON catalog: {json_path}")

def generate_index_html(output_dir):
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Climate Data Catalog</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  .tabs { overflow: hidden; background: #eee; }
  .tab-button {
    background: #ddd;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    float: left;
    font-weight: bold;
  }
  .tab-button.active { background: white; border-bottom: 2px solid #000; }
  .tab-content { clear: both; padding: 20px; border: 1px solid #ddd; background: white; }
  select, button { margin: 5px 10px 20px 0; padding: 5px; }
  .dataset-list { margin-top: 20px; }
  .dataset-item { margin-bottom: 10px; }
  .dataset-name { font-weight: bold; cursor: pointer; }
  .metadata { margin-left: 20px; font-style: italic; display: none; }
</style>
</head>
<body>

<h1>Climate Data Catalog</h1>

<div class="tabs">
  <button class="tab-button active" onclick="showTab('obs')">Observations</button>
  <button class="tab-button" onclick="showTab('reanalysis')">Reanalysis</button>
</div>

<div id="obs" class="tab-content">
  <h2>Observations</h2>
  <label>Domain:
    <select id="obs-domain"></select>
  </label>
  <label>Dataset:
    <select id="obs-dataset" disabled></select>
  </label>
  <label>Temporal Resolution:
    <select id="obs-tempres" disabled></select>
  </label>
  <label>Variable:
    <select id="obs-variable" disabled></select>
  </label>
  <div id="obs-datasets" class="dataset-list"></div>
</div>

<div id="reanalysis" class="tab-content" style="display:none;">
  <h2>Reanalysis</h2>
  <label>Dataset:
    <select id="rean-dataset"></select>
  </label>
  <label>Temporal Resolution:
    <select id="rean-tempres" disabled></select>
  </label>
  <label>Variable:
    <select id="rean-variable" disabled></select>
  </label>
  <div id="rean-datasets" class="dataset-list"></div>
</div>

<script>
let obsCatalog = null;
let reanCatalog = null;

function showTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(div => div.style.display = 'none');
  document.getElementById(tabName).style.display = 'block';
  document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
  event.currentTarget.classList.add('active');
}

// Utilities to get unique sorted values from catalog keys
function uniqueSorted(arr) {
  return [...new Set(arr)].sort();
}

// --- OBSERVATIONS --- //
function initObsDropdowns() {
  const keys = Object.keys(obsCatalog.sources);

  // Extract domain, dataset, tempres, variable from keys like:
  // obs/gridded/<domain>/<variable>/<tempres>/<dataset>
  let domains = new Set();
  keys.forEach(k => {
    const parts = k.split('/');
    if(parts.length === 6) {
      domains.add(parts[2]);
    }
  });
  const domainSelect = document.getElementById('obs-domain');
  domainSelect.innerHTML = '<option value="">--Select Domain--</option>';
  uniqueSorted([...domains]).forEach(d => {
    domainSelect.innerHTML += `<option value="${d}">${d}</option>`;
  });

  // Clear and disable others initially
  disableSelect('obs-dataset');
  disableSelect('obs-tempres');
  disableSelect('obs-variable');
  clearDiv('obs-datasets');

  domainSelect.onchange = () => {
    const domain = domainSelect.value;
    if(!domain) {
      disableSelect('obs-dataset');
      disableSelect('obs-tempres');
      disableSelect('obs-variable');
      clearDiv('obs-datasets');
      return;
    }

    // Populate datasets for this domain
    const datasets = new Set();
    keys.forEach(k => {
      const parts = k.split('/');
      if(parts.length === 6 && parts[2] === domain) {
        datasets.add(parts[5]);
      }
    });
    const datasetSelect = document.getElementById('obs-dataset');
    datasetSelect.innerHTML = '<option value="">--Select Dataset--</option>';
    uniqueSorted([...datasets]).forEach(ds => {
      datasetSelect.innerHTML += `<option value="${ds}">${ds}</option>`;
    });
    datasetSelect.disabled = false;

    disableSelect('obs-tempres');
    disableSelect('obs-variable');
    clearDiv('obs-datasets');
  };

  document.getElementById('obs-dataset').onchange = () => {
    const domain = domainSelect.value;
    const dataset = document.getElementById('obs-dataset').value;
    if(!dataset) {
      disableSelect('obs-tempres');
      disableSelect('obs-variable');
      clearDiv('obs-datasets');
      return;
    }
    // Populate temporal resolutions
    const tempresSet = new Set();
    Object.keys(obsCatalog.sources).forEach(k => {
      const parts = k.split('/');
      if(parts.length === 6 && parts[2] === domain && parts[5] === dataset) {
        tempresSet.add(parts[4]);
      }
    });
    const tempresSelect = document.getElementById('obs-tempres');
    tempresSelect.innerHTML = '<option value="">--Select Temporal Resolution--</option>';
    uniqueSorted([...tempresSet]).forEach(tr => {
      tempresSelect.innerHTML += `<option value="${tr}">${tr}</option>`;
    });
    tempresSelect.disabled = false;

    disableSelect('obs-variable');
    clearDiv('obs-datasets');
  };

  document.getElementById('obs-tempres').onchange = () => {
    const domain = domainSelect.value;
    const dataset = document.getElementById('obs-dataset').value;
    const tempres = document.getElementById('obs-tempres').value;
    if(!tempres) {
      disableSelect('obs-variable');
      clearDiv('obs-datasets');
      return;
    }
    // Populate variables
    const varsSet = new Set();
    Object.keys(obsCatalog.sources).forEach(k => {
      const parts = k.split('/');
      if(parts.length === 6 && parts[2] === domain && parts[5] === dataset && parts[4] === tempres) {
        varsSet.add(parts[3]);
      }
    });
    const varSelect = document.getElementById('obs-variable');
    varSelect.innerHTML = '<option value="">--Select Variable--</option>';
    uniqueSorted([...varsSet]).forEach(v => {
      varSelect.innerHTML += `<option value="${v}">${v}</option>`;
    });
    varSelect.disabled = false;
    clearDiv('obs-datasets');
  };

  document.getElementById('obs-variable').onchange = () => {
    const domain = domainSelect.value;
    const dataset = document.getElementById('obs-dataset').value;
    const tempres = document.getElementById('obs-tempres').value;
    const variable = document.getElementById('obs-variable').value;
    if(!variable) {
      clearDiv('obs-datasets');
      return;
    }
    // Show matching datasets
    const listDiv = document.getElementById('obs-datasets');
    listDiv.innerHTML = '';
    Object.entries(obsCatalog.sources).forEach(([k,v]) => {
      const parts = k.split('/');
      if(parts.length === 6 && parts[2] === domain && parts[3] === variable && parts[4] === tempres && parts[5] === dataset) {
        listDiv.innerHTML += `
          <div class="dataset-item">
            <div class="dataset-name" onclick="toggleMetadata(this.nextElementSibling)">${parts[5]}</div>
            <div class="metadata">
              <div><b>Description:</b> ${v.description}</div>
              <div><b>Files:</b> ${v.metadata.n_files}</div>
              <div><b>Data Location:</b> ${v.args.urlpath}</div>
            </div>
          </div>`;
      }
    });
  };
}

// --- REANALYSIS --- //
function initReanDropdowns() {
  const keys = Object.keys(reanCatalog.sources);

  // keys like: reanalysis/<dataset>/<tempres>/<variable>
  let datasets = new Set();
  keys.forEach(k => {
    const parts = k.split('/');
    if(parts.length === 4) {
      datasets.add(parts[1]);
    }
  });

  const datasetSelect = document.getElementById('rean-dataset');
  datasetSelect.innerHTML = '<option value="">--Select Dataset--</option>';
  uniqueSorted([...datasets]).forEach(d => {
    datasetSelect.innerHTML += `<option value="${d}">${d}</option>`;
  });

  disableSelect('rean-tempres');
  disableSelect('rean-variable');
  clearDiv('rean-datasets');

  datasetSelect.onchange = () => {
    const dataset = datasetSelect.value;
    if(!dataset) {
      disableSelect('rean-tempres');
      disableSelect('rean-variable');
      clearDiv('rean-datasets');
      return;
    }

    // Populate temporal resolution
    const tempresSet = new Set();
    keys.forEach(k => {
      const parts = k.split('/');
      if(parts.length === 4 && parts[1] === dataset) {
        tempresSet.add(parts[2]);
      }
    });

    const tempresSelect = document.getElementById('rean-tempres');
    tempresSelect.innerHTML = '<option value="">--Select Temporal Resolution--</option>';
    uniqueSorted([...tempresSet]).forEach(t => {
      tempresSelect.innerHTML += `<option value="${t}">${t}</option>`;
    });
    tempresSelect.disabled = false;

    disableSelect('rean-variable');
    clearDiv('rean-datasets');
  };

  document.getElementById('rean-tempres').onchange = () => {
    const dataset = datasetSelect.value;
    const tempres = document.getElementById('rean-tempres').value;
    if(!tempres) {
      disableSelect('rean-variable');
      clearDiv('rean-datasets');
      return;
    }

    // Populate variables
    const varsSet = new Set();
    keys.forEach(k => {
      const parts = k.split('/');
      if(parts.length === 4 && parts[1] === dataset && parts[2] === tempres) {
        varsSet.add(parts[3]);
      }
    });

    const varSelect = document.getElementById('rean-variable');
    varSelect.innerHTML = '<option value="">--Select Variable--</option>';
    uniqueSorted([...varsSet]).forEach(v => {
      varSelect.innerHTML += `<option value="${v}">${v}</option>`;
    });
    varSelect.disabled = false;
    clearDiv('rean-datasets');
  };

  document.getElementById('rean-variable').onchange = () => {
    const dataset = datasetSelect.value;
    const tempres = document.getElementById('rean-tempres').value;
    const variable = document.getElementById('rean-variable').value;
    if(!variable) {
      clearDiv('rean-datasets');
      return;
    }
    const listDiv = document.getElementById('rean-datasets');
    listDiv.innerHTML = '';
    Object.entries(reanCatalog.sources).forEach(([k,v]) => {
      const parts = k.split('/');
      if(parts.length === 4 && parts[1] === dataset && parts[2] === tempres && parts[3] === variable) {
        listDiv.innerHTML += `
          <div class="dataset-item">
            <div class="dataset-name" onclick="toggleMetadata(this.nextElementSibling)">${variable}</div>
            <div class="metadata">
              <div><b>Description:</b> ${v.description}</div>
              <div><b>Files:</b> ${v.metadata.n_files}</div>
              <div><b>Data Location:</b> ${v.args.urlpath}</div>
            </div>
          </div>`;
      }
    });
  };
}

// Helpers
function disableSelect(id) {
  const el = document.getElementById(id);
  el.disabled = true;
  el.innerHTML = '<option value="">--Select--</option>';
}
function clearDiv(id) {
  document.getElementById(id).innerHTML = '';
}
function toggleMetadata(elem) {
  if(elem.style.display === 'none' || elem.style.display === '') {
    elem.style.display = 'block';
  } else {
    elem.style.display = 'none';
  }
}

// Load catalogs and initialize
async function loadCatalogs() {
  try {
    const [obsResp, reanResp] = await Promise.all([
      fetch('obs.json'),
      fetch('reanalysis.json')
    ]);
    obsCatalog = await obsResp.json();
    reanCatalog = await reanResp.json();

    initObsDropdowns();
    initReanDropdowns();
  } catch(err) {
    console.error('Failed to load catalogs:', err);
  }
}

window.onload = loadCatalogs;

</script>

</body>
</html>'''
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w") as f:
        f.write(html)
    print(f"✅ Wrote {index_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Convert YAML to JSON for JS usage
    yaml_to_json(OBS_YAML, os.path.join(OUTPUT_DIR, "obs.json"))
    yaml_to_json(REAN_YAML, os.path.join(OUTPUT_DIR, "reanalysis.json"))

    # Generate index.html with tabs and dropdowns
    generate_index_html(OUTPUT_DIR)

if __name__ == "__main__":
    main()

