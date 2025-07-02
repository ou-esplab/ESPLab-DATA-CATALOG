import json

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Earth System Prediction Data Catalog</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 1em; }
    nav a { margin: 1em; }
    .hidden { display: none; }
    pre { background-color: #f5f5f5; padding: 1em; }
  </style>
</head>
<body>
  <h1>Earth System Prediction Data Catalog</h1>
  <nav>
    <a href="#" onclick="showTab('obs')">Observations</a>
    <a href="#" onclick="showTab('reanalysis')">Reanalysis</a>
    <a href="#" onclick="showTab('model')">Models</a>
  </nav>

  <div id="obsTab" class="hidden">
    <h2>Observations</h2>
    <label>Domain:
      <select id="obsDomain"></select>
    </label>
    <label>Variable:
      <select id="obsVariable"></select>
    </label>
    <label>Temporal Res:
      <select id="obsTemporal"></select>
    </label>
    <label>Dataset:
      <select id="obsDataset"></select>
    </label>
    <pre id="obsMetadata"></pre>
  </div>

  <div id="reanalysisTab" class="hidden">
    <h2>Reanalysis</h2>
    <label>Dataset:
      <select id="reanDataset"></select>
    </label>
    <label>Temporal Res:
      <select id="reanTemporal"></select>
    </label>
    <label>Variable:
      <select id="reanVariable"></select>
    </label>
    <pre id="reanMetadata"></pre>
  </div>

  <div id="modelTab" class="hidden">
    <h2>Models</h2>
    <label>Category:
      <select id="modelCategory"></select>
    </label>
    <label>Project:
      <select id="modelProject"></select>
    </label>
    <label>Model:
      <select id="modelModel"></select>
    </label>
    <label>Variable:
      <select id="modelVariable"></select>
    </label>
    <pre id="modelMetadata"></pre>
  </div>

  <script>
    let obsCatalog = {};
    let reanCatalog = {};
    let modelCatalog = {};

    async function loadCatalogs() {
      [obsCatalog, reanCatalog, modelCatalog] = await Promise.all([
        fetch("catalogs/obs.json").then(r => r.json()),
        fetch("catalogs/reanalysis.json").then(r => r.json()),
        fetch("catalogs/model.json").then(r => r.json()),
      ]);
      populateObs();
      populateReanalysis();
      populateModel();
    }

    function showTab(tab) {
      document.getElementById("obsTab").classList.add("hidden");
      document.getElementById("reanalysisTab").classList.add("hidden");
      document.getElementById("modelTab").classList.add("hidden");
      document.getElementById(tab + "Tab").classList.remove("hidden");
    }

    function populateObs() {
      const domains = new Set();
      for (let key of Object.keys(obsCatalog.sources)) {
        const parts = key.split("/");
        if (parts.length >= 4) domains.add(parts[2]);
      }
      const obsDomainSelect = document.getElementById("obsDomain");
      obsDomainSelect.innerHTML = "<option>--Select--</option>";
      domains.forEach(d => obsDomainSelect.innerHTML += `<option value="${d}">${d}</option>`);
    }

    function populateReanalysis() {
      const datasets = new Set();
      for (let key of Object.keys(reanCatalog.sources)) {
        const parts = key.split("/");
        if (parts.length >= 2) datasets.add(parts[1]);
      }
      const reanDatasetSelect = document.getElementById("reanDataset");
      reanDatasetSelect.innerHTML = "<option>--Select--</option>";
      datasets.forEach(d => reanDatasetSelect.innerHTML += `<option value="${d}">${d}</option>`);
    }

    function populateModel() {
      const categories = new Set();
      for (let key of Object.keys(modelCatalog.sources)) {
        const parts = key.split("/");
        if (parts.length >= 2) categories.add(parts[1]);
      }
      const modelCategorySelect = document.getElementById("modelCategory");
      modelCategorySelect.innerHTML = "<option>--Select--</option>";
      categories.forEach(c => modelCategorySelect.innerHTML += `<option value="${c}">${c}</option>`);
    }

    // Obs drilldown
    document.getElementById("obsDomain").addEventListener("change", e => {
      const domain = e.target.value;
      const variables = new Set();
      for (let key of Object.keys(obsCatalog.sources)) {
        if (key.includes(`/${domain}/`)) {
          const parts = key.split("/");
          if (parts.length >= 4) variables.add(parts[3]);
        }
      }
      const vsel = document.getElementById("obsVariable");
      vsel.innerHTML = "<option>--Select--</option>";
      variables.forEach(v => vsel.innerHTML += `<option value="${v}">${v}</option>`);
    });

    // Reanalysis drilldown
    document.getElementById("reanDataset").addEventListener("change", e => {
      const ds = e.target.value;
      const temporals = new Set();
      for (let key of Object.keys(reanCatalog.sources)) {
        if (key.includes(`/${ds}/`)) {
          const parts = key.split("/");
          if (parts.length >= 3) temporals.add(parts[2]);
        }
      }
      const tsel = document.getElementById("reanTemporal");
      tsel.innerHTML = "<option>--Select--</option>";
      temporals.forEach(t => tsel.innerHTML += `<option value="${t}">${t}</option>`);
    });

    // Model drilldown
    document.getElementById("modelCategory").addEventListener("change", e => {
      const category = e.target.value;
      const projects = new Set();
      for (let key of Object.keys(modelCatalog.sources)) {
        if (key.startsWith(`model/${category}`)) {
          const parts = key.split("/");
          if (parts.length >= 3) projects.add(parts[2]);
        }
      }
      const psel = document.getElementById("modelProject");
      psel.innerHTML = "<option>--Select--</option>";
      projects.forEach(p => psel.innerHTML += `<option value="${p}">${p}</option>`);
    });

    document.getElementById("modelProject").addEventListener("change", e => {
      const category = document.getElementById("modelCategory").value;
      const project = e.target.value;
      const models = new Set();
      for (let key of Object.keys(modelCatalog.sources)) {
        if (key.startsWith(`model/${category}/${project}`)) {
          const parts = key.split("/");
          if (parts.length >= 4) models.add(parts[3]);
        }
      }
      const msel = document.getElementById("modelModel");
      msel.innerHTML = "<option>--Select--</option>";
      models.forEach(m => msel.innerHTML += `<option value="${m}">${m}</option>`);
    });

    document.getElementById("modelModel").addEventListener("change", e => {
      const category = document.getElementById("modelCategory").value;
      const project = document.getElementById("modelProject").value;
      const model = e.target.value;
      const variables = new Set();
      for (let key of Object.keys(modelCatalog.sources)) {
        if (key.startsWith(`model/${category}/${project}/${model}`)) {
          const parts = key.split("/");
          if (parts.length >= 5) variables.add(parts[4]);
        }
      }
      const vsel = document.getElementById("modelVariable");
      vsel.innerHTML = "<option>--Select--</option>";
      variables.forEach(v => vsel.innerHTML += `<option value="${v}">${v}</option>`);
    });

    // show model metadata
    document.getElementById("modelVariable").addEventListener("change", e => {
      const category = document.getElementById("modelCategory").value;
      const project = document.getElementById("modelProject").value;
      const model = document.getElementById("modelModel").value;
      const variable = e.target.value;
      const key = `model/${category}/${project}/${model}/${variable}`;
      const meta = modelCatalog.sources[key];
      if (meta) {
        document.getElementById("modelMetadata").textContent = JSON.stringify(meta.metadata, null, 2);
      }
    });

    loadCatalogs();
  </script>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(TEMPLATE)

print("✅ index.html with model, obs, and reanalysis tabs written.")

