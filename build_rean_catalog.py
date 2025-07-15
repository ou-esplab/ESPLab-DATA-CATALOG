import os
import yaml
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = "/data/esplab/shared/reanalysis"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}

def get_netcdf_files(directory):
    return sorted([
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.nc') and os.path.isfile(os.path.join(directory, f))
    ])

def extract_metadata_all_files(nc_files):
    try:
        ds = xr.open_mfdataset(nc_files, combine='by_coords', parallel=False)
        var_name = list(ds.data_vars)[-1] if ds.data_vars else "unknown"
        long_name = ds[var_name].attrs.get('long_name', var_name)
        units = ds[var_name].attrs.get('units', 'unknown')
        if "time" in ds.coords:
            times = pd.to_datetime(ds.time.values, errors='coerce')
            times = times.dropna() if hasattr(times, 'dropna') else times
            date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}" if len(times) > 0 else "unknown"
        else:
            date_range = "unknown"
        ds.close()
        return {
            "long_name": long_name,
            "units": units,
            "date_range": date_range,
            "n_files": len(nc_files)
        }
    except Exception as e:
        print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e}")
        return {
            "long_name": "unknown",
            "units": "unknown",
            "date_range": "unknown",
            "n_files": len(nc_files)
        }

catalog = {
    "metadata": {
        "title": "Reanalysis Data Catalog",
        "version": 1,
        "description": "Auto-generated reanalysis data catalog"
    },
    "sources": {}
}

print(f"🔍 Scanning base directory: {BASE_DIR}")

for root, dirs, files in os.walk(BASE_DIR):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

    nc_files = get_netcdf_files(root)
    if not nc_files:
        continue

    rel_path = os.path.relpath(root, BASE_DIR)
    parts = rel_path.split(os.sep)

    if len(parts) != 3:
        continue  # Expecting reanalysis/<dataset>/<tempres>/<variable>

    dataset, tempres, variable = parts
    print(f"✔️ Processing reanalysis/{dataset}/{tempres}/{variable}")

    meta = extract_metadata_all_files(nc_files)
    key = f"reanalysis/{dataset}/{tempres}/{variable}"
    catalog["sources"][key] = {
        "description": meta['long_name'],
        "driver": "netcdf",
        "args": {
            "urlpath": os.path.join(root, "*.nc"),
            "engine": "netcdf4"
        },
        "metadata": {
            "units": meta['units'],
            "date_range": meta['date_range'],
            "n_files": meta['n_files'],
            "data_location": root
        }
    }

output_path = "catalogs/reanalysis.yaml"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    yaml.dump(catalog, f, sort_keys=False)
print(f"✅ Catalog written to {output_path}")
