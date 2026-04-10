import os
import json

# Configure the paths to each of the relevant .json files
OBS_JSON = "docs/obs.json"
REANALYSIS_JSON = "docs/reanalysis.json"
MODEL_JSON = "docs/model.json"

# Define the directory where the output .html files will go
OUTPUT_DIR = "docs"
OBS_DIR = os.path.join(OUTPUT_DIR, "obs")
REANALYSIS_DIR = os.path.join(OUTPUT_DIR, "reanalysis")

# Define colors and the logo image to be used to create the catalog webpage
OU_RED = "#841617"
OU_GOLD = "#FFB81C"
ESPLAB_LOGO = "esplab_logo.png"

# Define a helper function to print a summary of the catalog structure (for debugging purposes)
def print_summary(d, level=0, max_level=2):
    indent = '  ' * level
    if level > max_level:
        print(f"{indent}...")
        return
    if isinstance(d, dict):
        for k, v in d.items():
            print(f"{indent}{k}:")
            print_summary(v, level + 1, max_level)
    elif isinstance(d, list):
        print(f"{indent}List with {len(d)} entries")
    else:
        print(f"{indent}{d}")

# Define a function to open a catalog .json file
def load_catalog_json(path):
    # Given the path to a .json file, open the file and load it
    with open(path) as f:
        return json.load(f)

# Define a function to get unique sorted values from a list (used for dropdown options)
def unique_sorted(lst):
    return sorted(set(lst))

# Define a function to dynamically generate the observations catalog page given the catalog.json file
def generate_obs_page_dynamic(catalog):
    """
    Generate the observations HTML page with dynamic dropdowns per dataset type.
    Handles indices (1 dropdowns) and gridded (variable depth) automatically.
    """
    # Create a nested dictionary to organize data by type and hierarchy
    data_dict = {}

    # For each key path and data source in the obs catalog .json file
    for key, source in catalog["sources"].items():
        # Split apart the key path based on /s (e.g., 'indices/index_name' or 'gridded/domain/variable/tempres/dataset/subdataset')
        parts = key.split("/")

        # Extract the dataset type from parts[1] (either 'gridded' or 'indices')
        dtype = parts[1]

        # Navigate/create nested dictionary structure based on path parts (starting at parts[2:])
        # For indices: just the index name (1 level)
        # For gridded: domain -> variable -> tempres -> dataset -> subdataset (5 levels)
        d = data_dict.setdefault(dtype, {})
        # For each remaining path part, create nested levels
        for p in parts[2:]:
            d = d.setdefault(p, {})
        
        # Store metadata under the special "_meta" key for display in JavaScript
        d["_meta"] = {
            "name": parts[-1],
            "long_name": source["metadata"].get("long_name", "No long name"),
            "description": source.get("description", "No description"),
            "units": source["metadata"].get("units", "unknown"),
            "date_range": source["metadata"].get("date_range", "unknown"),
            "files": source["metadata"].get("n_files", 0),
            "data_location": source["metadata"].get("data_location", ""),
        }

    # Post-process function: for nodes that have both metadata AND children (like CPC-UNI-CONUS-0.25deg 
    # which has RT), move the metadata to a "normal" child so both are selectable
    def process_variants(node):
        """Recursively process nodes. If a node has both _meta and other keys, create a 'normal' variant."""
        if not isinstance(node, dict):
            return
        
        # Get non-meta keys (children)
        children = [k for k in node.keys() if k != "_meta"]
        
        # If this node has both metadata and children, wrap the metadata
        if "_meta" in node and children:
            meta = node.pop("_meta")
            node["Normal"] = {"_meta": meta}
        
        # Recurse into children
        for key in node:
            if isinstance(node[key], dict):
                process_variants(node[key])
    
    # Apply post-processing to each dataset type
    for dtype in data_dict:
        process_variants(data_dict[dtype])

    # Define the structure of the labeled dropdowns per dataset type
    STRUCTURE = {
        "indices": ["Index"],
        "gridded": ["Domain", "Variable", "Temporal Resolution", "Dataset", "Subdataset"]
    }

# Generate the HTML for the observations page  
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Observations</title>
<link rel="stylesheet" href="style.css" />
</head>
<body>
<h1>Observations</h1>

<div id="dropdown-container"></div>
<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};
const STRUCTURE = {json.dumps(STRUCTURE)};

// Helper to clear and disable a select element
function clearSelect(sel, placeholder="-- Select --") {{
    sel.innerHTML = `<option value="">${{placeholder}}</option>`;
    sel.disabled = true;
}}

// Recursive function to create dropdowns dynamically with labels
function createDropdowns(container, dtype, path=[]) {{
    const labels = STRUCTURE[dtype];
    const nextIndex = path.length;
    if (nextIndex >= labels.length) return;

    // Create a wrapper div for label + dropdown
    const wrapper = document.createElement("div");
    wrapper.style.display = "inline-block";
    wrapper.style.marginRight = "20px";
    
    // Create label
    const label = document.createElement("label");
    label.textContent = labels[nextIndex] + ":";
    label.style.marginRight = "10px";
    label.style.fontWeight = "bold";
    wrapper.appendChild(label);

    const sel = document.createElement("select");
    sel.id = "level" + nextIndex;
    sel.innerHTML = `<option value="">-- Select ${{labels[nextIndex]}} --</option>`;
    wrapper.appendChild(sel);
    container.appendChild(wrapper);

    sel.addEventListener("change", () => {{
        // Remove any deeper dropdowns
        let deeper = nextIndex + 1;
        while (document.getElementById("level" + deeper)) {{
            document.getElementById("level" + deeper).parentElement.remove();
            deeper++;
        }}
        document.getElementById("datasetList").innerHTML = "";

        // Get current catalog node
        let node = catalog[dtype];
        for (let p of path) {{
            node = node[p];
        }}
        const val = sel.value;
        if (!val) return;

        // Check if there are child nodes (excluding _meta)
        const hasChildren = node[val] && Object.keys(node[val]).filter(k => k !== "_meta").length > 0;
        
        if (hasChildren) {{
            // If there are child nodes, create the next dropdown level
            createDropdowns(container, dtype, path.concat([val]));
        }} else if (node[val] && node[val]["_meta"]) {{
            // Display metadata if we've reached a leaf node
            const meta = node[val]["_meta"];
            const div = document.createElement("div");
            div.className = "dataset-entry";
            div.style.marginTop = "20px";
            div.style.padding = "15px";
            div.style.backgroundColor = "#fffacd";
            div.style.border = "1px solid #ddd";
            div.style.borderRadius = "4px";
            div.innerHTML = `
                <div style="font-weight: bold; font-size: 1.1em; color: #841617;">${{meta.name}}</div>
                <div style="color: #000000;"><strong>Description:</strong> ${{meta.long_name}}</div>
                <div style="color: #000000;"><strong>Units:</strong> ${{meta.units}}</div>
                <div style="color: #000000;"><strong>Date Range:</strong> ${{meta.date_range}}</div>
                <div style="color: #000000;"><strong>Files:</strong> ${{meta.files}}</div>
                <div style="color: #000000;"><strong>Data Location:</strong> ${{meta.data_location}}</div>
            `;
            document.getElementById("datasetList").appendChild(div);
        }}
    }});

    // Populate the dropdown options for this level
    let node = catalog[dtype];
    for (let p of path) {{
        node = node[p];
    }}
    Object.keys(node).forEach(k => {{
        if (k !== "_meta") {{
            const option = document.createElement("option");
            option.value = k;
            option.textContent = k;
            sel.appendChild(option);
        }}
    }});
    sel.disabled = false;
}}

// Initialize the dropdown container with the first dropdown for each dataset type
const container = document.getElementById("dropdown-container");
Object.keys(catalog).forEach(dtype => {{
    const heading = document.createElement("h2");
    heading.textContent = dtype.charAt(0).toUpperCase() + dtype.slice(1);
    container.appendChild(heading);
    
    const dropdownWrapper = document.createElement("div");
    dropdownWrapper.style.marginBottom = "20px";
    container.appendChild(dropdownWrapper);
    
    createDropdowns(dropdownWrapper, dtype, []);
}});
</script>
</body>
</html>
"""
    return html

# Define the function to dynamically generate the reanalysis page based on the catalog .json file 
def generate_reanalysis_page_dynamic(catalog):
    """
    Generate the reanalysis HTML page with dynamic dropdowns.
    Hierarchy: Dataset -> Temporal Resolution -> Variable
    """
    data_dict = {}

    # For each key path and data source in the reanalysis catalog
    for key, source in catalog["sources"].items():
        # Split apart the key path (e.g., 'reanalysis/era5/daily/precip')
        parts = key.split("/")
        
        # Expecting: ['reanalysis', 'dataset', 'tempres', 'variable']
        if len(parts) != 4:
            continue
        
        _, dataset, tempres, variable = parts
        
        # Navigate/create the nested dictionary structure: dataset -> tempres -> variable
        d = data_dict.setdefault(dataset, {})
        d = d.setdefault(tempres, {})
        
        # Store metadata under the special "_meta" key
        d[variable] = {
            "_meta": {
                "name": variable,
                "long_name": source["metadata"].get("long_name", source.get("description", "No description")),
                "description": source.get("description", "No description"),
                "units": source["metadata"].get("units", "unknown"),
                "date_range": source["metadata"].get("date_range", "unknown"),
                "files": source["metadata"].get("n_files", 0),
                "data_location": source["metadata"].get("data_location", ""),
            }
        }

    # Define the structure of the labeled dropdowns
    STRUCTURE = {
        "reanalysis": ["Dataset", "Temporal Resolution", "Variable"]
    }

    # Generate the HTML for the reanalysis page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reanalysis</title>
<link rel="stylesheet" href="style.css" />
</head>
<body>
<h1>Reanalysis</h1>

<div id="dropdown-container"></div>
<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};
const STRUCTURE = {json.dumps(STRUCTURE)};

// Helper to clear and disable a select element
function clearSelect(sel, placeholder="-- Select --") {{
    sel.innerHTML = `<option value="">${{placeholder}}</option>`;
    sel.disabled = true;
}}

// Recursive function to create dropdowns dynamically with labels
function createDropdowns(container, dtype, path=[]) {{
    const labels = STRUCTURE[dtype];
    const nextIndex = path.length;
    if (nextIndex >= labels.length) return;

    // Create a wrapper div for label + dropdown
    const wrapper = document.createElement("div");
    wrapper.style.display = "inline-block";
    wrapper.style.marginRight = "20px";
    
    // Create label
    const label = document.createElement("label");
    label.textContent = labels[nextIndex] + ":";
    label.style.marginRight = "10px";
    label.style.fontWeight = "bold";
    wrapper.appendChild(label);

    const sel = document.createElement("select");
    sel.id = "level" + nextIndex;
    sel.innerHTML = `<option value="">-- Select ${{labels[nextIndex]}} --</option>`;
    wrapper.appendChild(sel);
    container.appendChild(wrapper);

    sel.addEventListener("change", () => {{
        // Remove any deeper dropdowns
        let deeper = nextIndex + 1;
        while (document.getElementById("level" + deeper)) {{
            document.getElementById("level" + deeper).parentElement.remove();
            deeper++;
        }}
        document.getElementById("datasetList").innerHTML = "";

        // Get current catalog node
        let node = catalog;
        for (let p of path) {{
            node = node[p];
        }}
        const val = sel.value;
        if (!val) return;

        // Check if there are child nodes (excluding _meta)
        const hasChildren = node[val] && Object.keys(node[val]).filter(k => k !== "_meta").length > 0;
        
        if (hasChildren) {{
            // If there are child nodes, create the next dropdown level
            createDropdowns(container, dtype, path.concat([val]));
        }} else if (node[val] && node[val]["_meta"]) {{
            // Display metadata if we've reached a leaf node
            const meta = node[val]["_meta"];
            const div = document.createElement("div");
            div.className = "dataset-entry";
            div.style.marginTop = "20px";
            div.style.padding = "15px";
            div.style.backgroundColor = "#fffacd";
            div.style.border = "1px solid #ddd";
            div.style.borderRadius = "4px";
            div.innerHTML = `
                <div style="font-weight: bold; font-size: 1.1em; color: #841617;">${{meta.name}}</div>
                <div style="color: #000000;"><strong>Description:</strong> ${{meta.long_name}}</div>
                <div style="color: #000000;"><strong>Units:</strong> ${{meta.units}}</div>
                <div style="color: #000000;"><strong>Date Range:</strong> ${{meta.date_range}}</div>
                <div style="color: #000000;"><strong>Files:</strong> ${{meta.files}}</div>
                <div style="color: #000000;"><strong>Data Location:</strong> ${{meta.data_location}}</div>
            `;
            document.getElementById("datasetList").appendChild(div);
        }}
    }});

    // Populate the dropdown options for this level
    let node = catalog;
    for (let p of path) {{
        node = node[p];
    }}
    Object.keys(node).forEach(k => {{
        if (k !== "_meta") {{
            const option = document.createElement("option");
            option.value = k;
            option.textContent = k;
            sel.appendChild(option);
        }}
    }});
    sel.disabled = false;
}}

// Initialize the dropdown container
const container = document.getElementById("dropdown-container");
createDropdowns(container, "reanalysis", []);
</script>
</body>
</html>
"""
    return html

# Define a function to dynamically generate the model page based on the catalog .json file
def generate_model_page_dynamic(catalog):
    """
    Generate the model HTML page with dynamic dropdowns.
    Handles NCAR-CESM2-CLIMO structure: Experiment -> Data Type -> Variable
    Handles NCAR-CESM2-SMYLE structure: Temporal Resolution -> Variable
    Handles NMME models: Model -> Temporal -> Variable
    Handles SubC models: Model -> Temporal -> Variable
    """
    data_dict = {}
    
    # For each key path and data source in the model catalog
    for key, source in catalog["sources"].items():
        # Split apart the key path into parts
        parts = key.split('/')
        
        # Handle the CESM2-CLIMO catalog structure
        # Expected format: model/initialized/<MODEL-NAME>/<EXPERIMENT>/<DATATYPE>/<VARIABLE>
        if len(parts) >= 6 and parts[1] == "initialized" and parts[2] == "NCAR-CESM2-CLIMO":
            category = parts[1]  # "initialized"
            model = parts[2]     # "NCAR-CESM2-CLIMO"
            experiment = parts[3]
            datatype = parts[4]
            variable = parts[5]
            
            # Build nested dict structure
            if category not in data_dict:
                data_dict[category] = {}
            if model not in data_dict[category]:
                data_dict[category][model] = {}
            if experiment not in data_dict[category][model]:
                data_dict[category][model][experiment] = {}
            if datatype not in data_dict[category][model][experiment]:
                data_dict[category][model][experiment][datatype] = {}
            if variable not in data_dict[category][model][experiment][datatype]:
                data_dict[category][model][experiment][datatype][variable] = []
            
            # Append metadata entry
            data_dict[category][model][experiment][datatype][variable].append({
                "name": variable,
                "long_name": source.get("metadata", {}).get("long_name", "") or source.get("description", "unknown"),
                "units": source.get("metadata", {}).get("units", "unknown"),
                "date_range": source.get("metadata", {}).get("date_range", "unknown"),
                "files": source.get("metadata", {}).get("n_files", "unknown"),
                "ensemble_members": source.get("metadata", {}).get("ensemble_members", "unknown"),
                "data_location": source.get("metadata", {}).get("data_location", "unknown")
            })

        # Handle the CESM2-SMYLE catalog structure
        # Expected format: model/initialized/NCAR-CESM2-SMYLE/<TEMPRES>/<VARIABLE>
        elif len(parts) >= 5 and parts[1] == "initialized" and parts[2] == "NCAR-CESM2-SMYLE":
            category = parts[1]  # "initialized"
            model = parts[2]     # "NCAR-CESM2-SMYLE"
            tempres = parts[3]   # "daily"
            variable = parts[4]  # "PRECC"
            
            # Build nested dict structure
            if category not in data_dict:
                data_dict[category] = {}
            if model not in data_dict[category]:
                data_dict[category][model] = {}
            if tempres not in data_dict[category][model]:
                data_dict[category][model][tempres] = {}
            if variable not in data_dict[category][model][tempres]:
                data_dict[category][model][tempres][variable] = []
            
            # Append metadata entry
            data_dict[category][model][tempres][variable].append({
                "name": variable,
                "long_name": source.get("metadata", {}).get("long_name", "") or source.get("description", "unknown"),
                "units": source.get("metadata", {}).get("units", "unknown"),
                "date_range": source.get("metadata", {}).get("date_range", "unknown"),
                "files": source.get("metadata", {}).get("n_files", "unknown"),
                "ensemble_members": source.get("metadata", {}).get("ensemble_members", "unknown"),
                "data_location": source.get("metadata", {}).get("data_location", "unknown")
            })

        # Handle the NMME catalog structure
        # Expected format: nmme-backup/<MODEL>/<TEMPRES>/<VARIABLE>
        elif len(parts) >=5 and parts[1] == "nmme-backup":
            model = parts[2]
            tempres = parts[3]
            variable = parts[4]
            
            # Build nested dict structure
            if "nmme" not in data_dict:
                data_dict["nmme"] = {}
            if model not in data_dict["nmme"]:
                data_dict["nmme"][model] = {}
            if tempres not in data_dict["nmme"][model]:
                data_dict["nmme"][model][tempres] = {}
            if variable not in data_dict["nmme"][model][tempres]:
                data_dict["nmme"][model][tempres][variable] = []
            
            # Append metadata entry
            data_dict["nmme"][model][tempres][variable].append({
                "name": variable,
                "long_name": source.get("metadata", {}).get("long_name", "") or source.get("description", "unknown"),
                "units": source.get("metadata", {}).get("units", "unknown"),
                "date_range": source.get("metadata", {}).get("date_range", "unknown"),
                "files": source.get("metadata", {}).get("n_files", "unknown"),
                "ensemble_members": source.get("metadata", {}).get("ensemble_members", "unknown"),
                "data_location": source.get("metadata", {}).get("data_location", "unknown")
            })
        
        # Handle the SubC catalog structure
        # Expected format: subc-backup/<MODEL>/<TEMPRES>/<VARIABLE>
        elif len(parts) >=5 and parts[1] == "subc-backup":
            category = "subc"
            model = parts[2]     # "ECCC-GEPS8", "COLA-CCSM4-RSMAS"
            tempres = parts[3]   # "forecast", "hindcast"
            variable = parts[4]  # "pr", "tas", "zg"
            
            # Build nested dict structure
            if category not in data_dict:
                data_dict[category] = {}
            if model not in data_dict[category]:
                data_dict[category][model] = {}
            if tempres not in data_dict[category][model]:
                data_dict[category][model][tempres] = {}
            if variable not in data_dict[category][model][tempres]:
                data_dict[category][model][tempres][variable] = []
            
            # Append metadata entry
            data_dict[category][model][tempres][variable].append({
                "name": variable,
                "long_name": source.get("metadata", {}).get("long_name", "") or source.get("description", "unknown"),
                "units": source.get("metadata", {}).get("units", "unknown"),
                "date_range": source.get("metadata", {}).get("date_range", "unknown"),
                "files": source.get("metadata", {}).get("n_files", "unknown"),
                "ensemble_members": source.get("metadata", {}).get("ensemble_members", "unknown"),
                "data_location": source.get("metadata", {}).get("data_location", "unknown")
            })
    
    # Define the structure with labels for dropdowns
    STRUCTURE = {
        "initialized": {
            "NCAR-CESM2-CLIMO": ["Experiment", "Data Type", "Variable"],
            "NCAR-CESM2-SMYLE": ["Temporal Resolution", "Variable"]
        },
        "nmme": {},
        "subc": {},
    }

    # Add all NMME models to STRUCTURE dynamically
    if "nmme" in data_dict:
        for model_name in sorted(data_dict["nmme"].keys()):
            STRUCTURE["nmme"][model_name] = ["Temporal", "Variable"]

    # Add all SubC models to STRCUTURE dynamically
    if "subc" in data_dict:
        for model_name in sorted(data_dict["subc"].keys()):
            STRUCTURE["subc"][model_name] = ["Temporal", "Variable"]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Model</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>

<h1>Model</h1>

<div id="dropdown-container"></div>
<div id="datasetList"></div>

<script>
const catalog = {json.dumps(data_dict)};
const STRUCTURE = {json.dumps(STRUCTURE)};

// Helper to clear and disable a select element
function clearSelect(sel, placeholder="-- Select --") {{
    sel.innerHTML = `<option value="">${{placeholder}}</option>`;
    sel.disabled = true;
}}

// Recursive function to create dropdowns dynamically with labels
function createDropdowns(container, category, model, path=[]) {{
    const labels = STRUCTURE[category][model];
    const nextIndex = path.length;
    if (nextIndex >= labels.length) return;

    // Create a wrapper div for label + dropdown
    const wrapper = document.createElement("div");
    wrapper.style.display = "inline-block";
    wrapper.style.marginRight = "20px";
    wrapper.style.whiteSpace = "nowrap";
    
    // Create label
    const label = document.createElement("label");
    label.textContent = labels[nextIndex] + ":";
    label.style.marginRight = "10px";
    label.style.fontWeight = "bold";
    wrapper.appendChild(label);

    const sel = document.createElement("select");
    sel.id = "level-" + category + "-" + nextIndex;
    sel.innerHTML = `<option value="">-- Select ${{labels[nextIndex]}} --</option>`;
    wrapper.appendChild(sel);
    container.appendChild(wrapper);

    sel.addEventListener("change", () => {{
        // Remove any deeper dropdowns
        let deeper = nextIndex + 1;
        while (document.getElementById("level-" + category + "-" + deeper)) {{
            document.getElementById("level-" + category + "-" + deeper).parentElement.remove();
            deeper++;
        }}
        document.getElementById("datasetList").innerHTML = "";

        const val = sel.value;
        if (!val) return;

        // Get current catalog node
        let node = catalog[category][model];
        for (let p of path) {{
            node = node[p];
        }}

        // Check if this is a leaf node (array) or intermediate node (object)
        const isLeafNode = Array.isArray(node[val]);
        
        if (!isLeafNode && node[val] && Object.keys(node[val]).length > 0) {{
            // If there are child nodes, create the next dropdown level
            createDropdowns(container, category, model, path.concat([val]));
        }} else if (isLeafNode) {{
            // If this is a leaf node (array of entries), display them
            const entries = node[val];
            const div = document.createElement("div");
            div.style.marginTop = "20px";
            entries.forEach(entry => {{
                const entryDiv = document.createElement("div");
                entryDiv.className = "dataset-entry";
                entryDiv.style.padding = "15px";
                entryDiv.style.backgroundColor = "#fffacd";
                entryDiv.style.border = "1px solid #ddd";
                entryDiv.style.borderRadius = "4px";
                entryDiv.style.marginBottom = "15px";
                entryDiv.innerHTML = `
                    <div style="font-weight: bold; font-size: 1.1em; color: #841617;">${{entry.name}}</div>
                    <div style="color: #000000;"><strong>Description:</strong> ${{entry.long_name}}</div>
                    <div style="color: #000000;"><strong>Units:</strong> ${{entry.units}}</div>
                    <div style="color: #000000;"><strong>Date Range:</strong> ${{entry.date_range}}</div>
                    <div style="color: #000000;"><strong>Files:</strong> ${{entry.files}}</div>
                    <div style="color: #000000;"><strong>Ensemble Members:</strong> ${{entry.ensemble_members}}</div>
                    <div style="color: #000000;"><strong>Data Location:</strong> ${{entry.data_location}}</div>
                `;
                div.appendChild(entryDiv);
            }});
            document.getElementById("datasetList").appendChild(div);
        }}
    }});

    // Populate the dropdown options for this level
    let node = catalog[category][model];
    for (let p of path) {{
        node = node[p];
    }}
    Object.keys(node).forEach(k => {{
        const option = document.createElement("option");
        option.value = k;
        option.textContent = k;
        sel.appendChild(option);
    }});
    sel.disabled = false;
}}

// Initialize the dropdown container
const container = document.getElementById("dropdown-container");
Object.keys(catalog).forEach(category => {{
    // Create category heading
    const categoryLabel = category === "initialized" ? "Initialized Models" : 
                     category === "subc" ? "SubC" :
                     category.toUpperCase();
    const heading = document.createElement("h2");
    heading.textContent = categoryLabel;
    heading.style.marginTop = category === "initialized" ? "0" : "30px";
    container.appendChild(heading);
    
    // Create wrapper for this category's controls
    const categoryWrapper = document.createElement("div");
    categoryWrapper.style.marginBottom = "30px";
    container.appendChild(categoryWrapper);

    // Create model selector dropdown
    const modelWrapper = document.createElement("div");
    modelWrapper.style.display = "inline-block";
    modelWrapper.style.marginRight = "20px";

    const modelLabel = document.createElement("label");
    modelLabel.textContent = "Model:";
    modelLabel.style.marginRight = "10px";
    modelLabel.style.fontWeight = "bold";
    modelWrapper.appendChild(modelLabel);

    const modelSelect = document.createElement("select");
    modelSelect.id = "model-" + category;
    modelSelect.innerHTML = "<option value=''>-- Select Model --</option>";
    modelWrapper.appendChild(modelSelect);
    categoryWrapper.appendChild(modelWrapper);

    // Populate model options
    Object.keys(catalog[category]).forEach(model => {{
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    }});

    // Create a div to hold the subsequent dropdowns (inside categoryWrapper, not separate)
    const dropdownDiv = document.createElement("div");
    dropdownDiv.id = "dropdowns-" + category;
    dropdownDiv.style.display = "flex";
    dropdownDiv.style.flexWrap = "wrap";
    dropdownDiv.style.gap = "20px";
    categoryWrapper.appendChild(dropdownDiv);
    
    // Handle model selection
    modelSelect.addEventListener("change", () => {{
        // Clear the dropdown div for this category
        document.getElementById("dropdowns-" + category).innerHTML = "";
        document.getElementById("datasetList").innerHTML = "";
        
        const selectedModel = modelSelect.value;
        if (!selectedModel) return;
        
        // Create subsequent dropdowns for this model
        createDropdowns(document.getElementById("dropdowns-" + category), category, selectedModel, []);
    }});
}});
</script>

</body>
</html>
"""
    
    return html

# Define a function to generate the HTML for the index page, including the banner and tab structure
# to hold the three different data type pages within iframes
def generate_index_html():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ESPLab Data Catalog</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>

<!-- Banner -->
<div class="banner" style="background-color:#f1f1f1; padding:20px; display:flex; align-items:center;">
  <img src="{ESPLAB_LOGO}" alt="ESPLab logo" style="height:90px; margin-right:15px;">
  <h1 style="margin:0; color:{OU_RED}; font-size:2.0em;">ESPLab Data Catalog</h1>
</div>

<div class="tab" style="margin-top:10px;">
  <button class="tablinks active" onclick="openTab(event, 'obs')">Observations</button>
  <button class="tablinks" onclick="openTab(event, 'reanalysis')">Reanalysis</button>
  <button class="tablinks" onclick="openTab(event, 'model')">Model</button>
</div>

<div id="obs" class="tabcontent" style="display: block;">
  <iframe src="obs.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="reanalysis" class="tabcontent" style="display: none;">
  <iframe src="reanalysis.html" style="width:100%; height:600px; border:none;"></iframe>
</div>
<div id="model" class="tabcontent" style="display: none;">
  <iframe src="model.html" style="width:100%; height:600px; border:none;"></iframe>
</div>

<script>
function openTab(evt, tabName) {{
  var tabcontent = document.getElementsByClassName("tabcontent");
  for (var i = 0; i < tabcontent.length; i++) {{
    tabcontent[i].style.display = "none";
  }}
  var tablinks = document.getElementsByClassName("tablinks");
  for (var i = 0; i < tablinks.length; i++) {{
    tablinks[i].classList.remove("active");
  }}
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}}
</script>

</body>
</html>
"""
    return html

# Define a function to write the generated HTML content to a file
def write_html(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {path}")

# Define the main function to load the catalogs, as well as generate and write the HTMLs for each page
def main():
    # Make sure the output directory exists and load in the .json files for each of the data types
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    obs_catalog = load_catalog_json(OBS_JSON)
    reanalysis_catalog = load_catalog_json(REANALYSIS_JSON)
    model_catalog = load_catalog_json(MODEL_JSON)
    
    # Use the written functions to generate each of the .html pages
    obs_html = generate_obs_page_dynamic(obs_catalog)
    reanalysis_html = generate_reanalysis_page_dynamic(reanalysis_catalog)
    model_html = generate_model_page_dynamic(model_catalog)
    index_html = generate_index_html()

    # Write the resulting .html files to the defined output directory
    write_html(os.path.join(OUTPUT_DIR, "index.html"), index_html)
    write_html(os.path.join(OUTPUT_DIR, "obs.html"), obs_html)
    write_html(os.path.join(OUTPUT_DIR, "reanalysis.html"), reanalysis_html)
    write_html(os.path.join(OUTPUT_DIR, "model.html"), model_html)

# If this script is directly run, then execute the main function
if __name__ == "__main__":
    main()

