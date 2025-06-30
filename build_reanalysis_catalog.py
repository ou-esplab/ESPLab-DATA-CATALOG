import os
import yaml
import xarray as xr
import pandas as pd

BASE_DIR = "/data/esplab/shared/reanalysis"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}

def get_netcdf_files(directory):
    return sorted([
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.endswith('.nc') and os.path.isfile(os.path.join(directory, f))
    ])

def extract_metadata(nc_files):
    try:
        ds = xr.open_dataset(nc_files[0], decode_times=True, use_cftime=True)
        var_name = list(ds.data_vars)[0] if ds.data_vars else "unknown"
        long_name = ds[var_name].attrs.get('long_name', var_name)
        units = ds[var_name].attrs.get('units', 'unknown')

        if 'time' in ds.coords:
            times = ds['time'].values
            times_str = [str(t) for t in times]
            date_range = f"{times_str[0]} to {times_str[-1]}"
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

def build_reanalysis_catalog(base_dir):
    catalog = {
        "metadata": {
            "title": "Reanalysis Data Catalog",
            "version": 1,
            "description": "Auto-generated reanalysis data catalog"
        },
        "sources": {}
    }

    print(f"Building Reanalysis catalog from base dir: {base_dir}")
    # Expected structure: reanalysis/<dataset>/<temporal_resolution>/<variable>
    if not os.path.isdir(base_dir):
        print(f"Error: base directory {base_dir} not found.")
        return catalog

    for dataset in sorted(os.listdir(base_dir)):
        if dataset in IGNORE_DIRS:
            continue
        dataset_path = os.path.join(base_dir, dataset)
        if not os.path.isdir(dataset_path):
            continue

        for temp_res in sorted(os.listdir(dataset_path)):
            if temp_res in IGNORE_DIRS:
                continue
            temp_path = os.path.join(dataset_path, temp_res)
            if not os.path.isdir(temp_path):
                continue

            for variable in sorted(os.listdir(temp_path)):
                if variable in IGNORE_DIRS:
                    continue
                variable_path = os.path.join(temp_path, variable)
                if not os.path.isdir(variable_path):
                    continue

                nc_files = get_netcdf_files(variable_path)
                if not nc_files:
                    print(f"⚠️ No NetCDF files found in {variable_path}, skipping.")
                    continue

                print(f"✔️ Processing reanalysis/{dataset}/{temp_res}/{variable}")
                meta = extract_metadata(nc_files)

                key = f"reanalysis/{dataset}/{temp_res}/{variable}"
                catalog["sources"][key] = {
                    "description": f"{meta['long_name']} ({meta['units']}), {meta['date_range']}",
                    "driver": "netcdf",
                    "args": {
                        "urlpath": os.path.join(variable_path, "*.nc"),
                        "engine": "netcdf4"
                    },
                    "metadata": {
                        "long_name": meta['long_name'],
                        "units": meta['units'],
                        "date_range": meta['date_range'],
                        "n_files": meta['n_files'],
                        "data_location": variable_path
                    }
                }

    return catalog

def write_catalog(catalog, output_path="reanalysis.yaml"):
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Catalog written to {output_path}")

# Main
if __name__ == "__main__":
    catalog = build_reanalysis_catalog(BASE_DIR)
    write_catalog(catalog)

