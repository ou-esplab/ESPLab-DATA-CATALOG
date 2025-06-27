import panel as pn
import intake
import xarray as xr
import glob
import pandas as pd

pn.extension()

# ----------------------------
# Load catalogs
# ----------------------------
obs_cat = intake.open_catalog("obs.yaml")
rean_cat = intake.open_catalog("reanalysis.yaml")

# ----------------------------
# OBS Hierarchy Tree
# ----------------------------
def is_valid_obs_key(key):
    parts = key.split('/')
    return len(parts) == 6 and parts[0] == 'obs' and parts[1] == 'gridded'

obs_tree = {}
for key in obs_cat._entries:
    if not is_valid_obs_key(key):
        continue
    _, _, domain, variable, temp_res, dataset = key.split('/')
    obs_tree.setdefault(temp_res, {}).setdefault(domain, {}).setdefault(variable, []).append(dataset)

# ----------------------------
# REANALYSIS Hierarchy Tree
# ----------------------------
def is_valid_reanalysis_key(key):
    parts = key.split('/')
    return len(parts) == 4 and parts[0] == 'reanalysis'

rean_tree = {}
for key in rean_cat._entries:
    if not is_valid_reanalysis_key(key):
        continue
    _, dataset, temp_res, variable = key.split('/')
    rean_tree.setdefault(temp_res, {}).setdefault(dataset, {}).setdefault(variable, [])

# ----------------------------
# OBS Widgets and Callbacks
# ----------------------------
obs_temp_select = pn.widgets.Select(name="Temporal Resolution", options=list(obs_tree))
obs_domain_select = pn.widgets.Select(name="Domain", options=[])
obs_variable_select = pn.widgets.Select(name="Variable", options=[])
obs_dataset_select = pn.widgets.Select(name="Dataset", options=[])

obs_info = pn.pane.Markdown("Select a dataset to view metadata.", width=400)
obs_ds_preview = pn.pane.Markdown("Dataset preview will appear here.", height=300)
load_obs_button = pn.widgets.Button(name="Load Dataset Preview", button_type="primary")

def update_obs_domains(event):
    temp = event.new
    domains = list(obs_tree.get(temp, {}))
    obs_domain_select.options = domains
    obs_domain_select.value = domains[0] if domains else None

def update_obs_variables(event):
    temp = obs_temp_select.value
    domain = event.new
    variables = list(obs_tree.get(temp, {}).get(domain, {}))
    obs_variable_select.options = variables
    obs_variable_select.value = variables[0] if variables else None

def update_obs_datasets(event):
    temp = obs_temp_select.value
    domain = obs_domain_select.value
    variable = event.new
    datasets = obs_tree.get(temp, {}).get(domain, {}).get(variable, [])
    obs_dataset_select.options = datasets
    obs_dataset_select.value = datasets[0] if datasets else None

def update_obs_info(event):
    temp = obs_temp_select.value
    domain = obs_domain_select.value
    variable = obs_variable_select.value
    dataset = obs_dataset_select.value
    key = f"obs/gridded/{domain}/{variable}/{temp}/{dataset}"
    
    if key in obs_cat:
        try:
            cat_entry = obs_cat._entries[key]
            md = getattr(cat_entry, '_metadata', {}) or {}   
        except Exception:
            md = {}     
        obs_info.object = f"""### {dataset}
- **Long Name**: {md.get('long_name', 'N/A')}
- **Units**: {md.get('units', 'N/A')}
- **Date Range**: {md.get('date_range', 'N/A')}
- **Files**: {md.get('n_files', 'N/A')}
- **Path**: `{md.get('data_location', 'N/A')}`"""

        obs_ds_preview.object = "*Press the button below to load a sample preview.*"
    else:
        obs_info.object = "No matching dataset."
        obs_ds_preview.object = ""
        
def preview_from_catalog(key, catalog, full_load_threshold=100):
    try:
        desc = catalog._entries[key].describe()
        urlpath = desc.get('args', {}).get('urlpath', None)
        file_list = sorted(glob.glob(urlpath))

        if not file_list:
            return "**No files found.**"
        if len(file_list) <= full_load_threshold:
            # Full open (lazy, not loading data into memory)
            ds = xr.open_mfdataset(file_list, combine='by_coords', parallel=True)
            return f"```python\n{ds}\n```"
            #load_type = "Full dataset preview"
        else:
            # Only sample first and last file
            files_to_open = [file_list[0], file_list[-1]]
            ds = xr.open_mfdataset(files_to_open, combine='by_coords', parallel=False)
            load_type = f"Preview from 2 of {len(file_list)} files"

        # Time range
        if "time" in ds:
            time_vals = ds.time.values
            time_range = f"{str(time_vals[0])[:10]} to {str(time_vals[-1])[:10]}"
        else:
            time_range = "N/A"

        # Dimensions
        dims_info = "\n".join([f"- `{dim}`: {size}" for dim, size in ds.dims.items()])
        
        # Coordinate bounds
        coords_preview = []
        for coord in ['latitude', 'lat', 'longitude', 'lon', 'level', 'lev']:
            if coord in ds:
                vals = ds[coord].values
                min_val, max_val = float(vals.min()), float(vals.max())
                coords_preview.append(f"- `{coord}`: {min_val:.2f} to {max_val:.2f}")
        coords_str = "\n".join(coords_preview) if coords_preview else "None"

        # Variables
        variables = ", ".join(ds.data_vars)

        return f"""**{load_type}**

**Time Range:** {time_range}

**Dimensions:**
{dims_info}

**Coordinate Ranges:**
{coords_str}

**Variables:** {variables}
"""

    except Exception as e:
        return f"**Failed to load dataset preview:** {e}"

def load_obs_preview(event):
    temp = obs_temp_select.value
    domain = obs_domain_select.value
    variable = obs_variable_select.value
    dataset = obs_dataset_select.value
    key = f"obs/gridded/{domain}/{variable}/{temp}/{dataset}"
    
    obs_ds_preview.object = "Loading preview..."
    
    preview_text = preview_from_catalog(key, obs_cat, full_load_threshold=100)
    obs_ds_preview.object = preview_text
            
# Attach OBS watchers
obs_temp_select.param.watch(update_obs_domains, 'value')
obs_domain_select.param.watch(update_obs_variables, 'value')
obs_variable_select.param.watch(update_obs_datasets, 'value')
obs_dataset_select.param.watch(update_obs_info, 'value')
load_obs_button.on_click(load_obs_preview)

# Initial OBS load
update_obs_domains(type("event", (), {"new": obs_temp_select.value}))
update_obs_variables(type("event", (), {"new": obs_domain_select.value}))
update_obs_datasets(type("event", (), {"new": obs_variable_select.value}))
update_obs_info(type("event", (), {"new": obs_dataset_select.value}))

obs_panel = pn.Column(
    "## Observational Data",
    pn.Row(obs_temp_select, obs_domain_select, obs_variable_select, obs_dataset_select),
    obs_info,
    load_obs_button,
    obs_ds_preview
)

# ----------------------------
# REANALYSIS Widgets and Callbacks
# ----------------------------
rean_temp_select = pn.widgets.Select(name="Temporal Resolution", options=list(rean_tree))
rean_dataset_select = pn.widgets.Select(name="Dataset", options=[])
rean_variable_select = pn.widgets.Select(name="Variable", options=[])

rean_info = pn.pane.Markdown("Select a variable to view metadata.", width=400)
rean_ds_preview = pn.pane.Markdown("Dataset preview will appear here.", height=300)
load_rean_button = pn.widgets.Button(name="Load Dataset Preview", button_type="primary")

def update_rean_datasets(event):
    temp = event.new
    datasets = list(rean_tree.get(temp, {}))
    rean_dataset_select.options = datasets
    rean_dataset_select.value = datasets[0] if datasets else None

def update_rean_variables(event):
    temp = rean_temp_select.value
    dataset = event.new
    variables = list(rean_tree.get(temp, {}).get(dataset, {}).keys())
    rean_variable_select.options = variables
    rean_variable_select.value = variables[0] if variables else None

def update_rean_info(event):
    temp = rean_temp_select.value
    dataset = rean_dataset_select.value
    variable = rean_variable_select.value
    key = f"reanalysis/{dataset}/{temp}/{variable}"
    
    print("UPDATE REAN: trying key ",key)

    try:
        cat_entry = rean_cat._entries[key]
        md = getattr(cat_entry, '_metadata', {}) or {}  
        print("UPDATE REAN md: ",md)
        rean_info.object = f"""### {variable}
- **Long Name**: {md.get('long_name', 'N/A')}
- **Units**: {md.get('units', 'N/A')}
- **Date Range**: {md.get('date_range', 'N/A')}
- **Files**: {md.get('n_files', 'N/A')}
- **Path**: `{md.get('data_location', 'N/A')}`"""

        rean_ds_preview.object = "*Press the button below to load a sample preview.*"
    except KeyError:
        print("UPDATE REAN: key not found")
        rean_info.object = "No matching dataset."
        read_ds_preview.object=""
 
        
def preview_reanalysis_dataset(key, rean_cat, full_load_threshold=10):
    print("PREVIEW: ",rean_cat,key)
    try:
        cat_entry = rean_cat._entries[key]  # LocalCatalogEntry
        print("PREVIEW TRY: ",cat_entry)
    except KeyError:
        return "PREVIEW ERROR: No matching dataset."

    md = cat_entry.metadata or {}
    args = cat_entry.args or {}
    
    urlpath = args.get("urlpath", "")
    file_list = sorted(glob.glob(urlpath)) if urlpath else []
    n_files = len(file_list)

    # Prepare metadata info string
    info_md = f"""### {key.split('/')[-1]}
- **Units**: {md.get('units', 'N/A')}
- **Date Range**: {md.get('date_range', 'N/A')}
- **Files**: {n_files}
- **Path**: `{md.get('data_location', urlpath)}`"""

    if n_files == 0:
        return info_md + "\n\n**No data files found.**"

    # Try loading dataset preview or full data depending on file count
    try:
        source = rean_cat[key]  # intake source object

        if n_files <= full_load_threshold:
            ds = source.to_dask()
            preview = f"```python\n{ds}\n```"
        else:
            # For large sets, just load first and last files info
            first_ds = source.subset(urlpath=file_list[0])()
            last_ds = source.subset(urlpath=file_list[-1])()
            preview = f"**Large dataset, previewing first and last files:**\n\n"
            preview += f"```python\n{first_ds}\n```\n---\n```python\n{last_ds}\n```"

        return info_md + "\n\n" + preview

    except Exception as e:
        return info_md + f"\n\n**Failed to load dataset preview:** {e}"

def load_rean_preview(event):
    key = f"reanalysis/{rean_dataset_select.value}/{rean_temp_select.value}/{rean_variable_select.value}"
    rean_ds_preview.object = "Loading dataset preview..."
    preview_md = preview_from_catalog(key,rean_cat)
    rean_ds_preview.object = preview_md

# Attach REAN watchers
rean_temp_select.param.watch(update_rean_datasets, 'value')
rean_dataset_select.param.watch(update_rean_variables, 'value')
rean_variable_select.param.watch(update_rean_info, 'value')
load_rean_button.on_click(load_rean_preview)

# Initial REAN load
update_rean_datasets(type("event", (), {"new": rean_temp_select.value}))
update_rean_variables(type("event", (), {"new": rean_dataset_select.value}))
update_rean_info(type("event", (), {"new": rean_variable_select.value}))

rean_panel = pn.Column(
    "## Reanalysis Data",
    pn.Row(rean_temp_select, rean_dataset_select, rean_variable_select),
    rean_info,
    load_rean_button,
    rean_ds_preview
)

# ----------------------------
# Final App Tabs
# ----------------------------
app = pn.Tabs(
    ("Observational Data", obs_panel),
    ("Reanalysis Data", rean_panel)
)

# Serve
if __name__.startswith("bokeh"):
    app.servable()
