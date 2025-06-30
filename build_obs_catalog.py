import os
import yaml
import xarray as xr
import pandas as pd

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

BASE_DIR = "/data/esplab/shared/obs"
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
            times = ds['time'].values  # numpy array of cftime or datetime64
            
            # Convert to strings for formatting
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

def build_obs_catalog(base_dir):
    catalog = {
        "metadata": {
            "title": "Observational Data Catalog",
            "version": 1,
            "description": "Auto-generated obs data catalog"
        },
        "sources": {}
    }

    gridded_path = os.path.join(base_dir, "gridded")

    for domain in sorted(os.listdir(gridded_path)):
        domain_path = os.path.join(gridded_path, domain)
        if not os.path.isdir(domain_path):
            continue

        for variable in sorted(os.listdir(domain_path)):
            variable_path = os.path.join(domain_path, variable)
            if not os.path.isdir(variable_path):
                continue

            for temp_res in sorted(os.listdir(variable_path)):
                temp_path = os.path.join(variable_path, temp_res)
                if not os.path.isdir(temp_path):
                    continue

                for dataset in sorted(os.listdir(temp_path)):
                    dataset_path = os.path.join(temp_path, dataset)
                    if not os.path.isdir(dataset_path):
                        continue

                    # Check if dataset_path has subdirectories with files
                    subdirs = [d for d in sorted(os.listdir(dataset_path))
                               if os.path.isdir(os.path.join(dataset_path, d))]

                    if subdirs:
                        # Use each subdir as dataset variant
                        for sub in subdirs:
                            sub_path = os.path.join(dataset_path, sub)
                            nc_files = get_netcdf_files(sub_path)
                            if not nc_files:
                                continue
                            key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}/{sub}"
                            meta = extract_metadata(nc_files)
                            catalog["sources"][key] = {
                                "description": meta['long_name'],
                                "driver": "netcdf",
                                "args": {
                                    "urlpath": os.path.join(sub_path, "*.nc"),
                                    "engine": "netcdf4"
                                },
                                "metadata": {
                                    "long_name": meta['long_name'],
                                    "units": meta['units'],
                                    "date_range": meta['date_range'],
                                    "n_files": meta['n_files'],
                                    "data_location": sub_path
                                }
                            }
                    else:
                        # No subdirs, use dataset_path as dataset
                        nc_files = get_netcdf_files(dataset_path)
                        if not nc_files:
                            continue
                        key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}"
                        meta = extract_metadata(nc_files)
                        catalog["sources"][key] = {
                            "description": meta['long_name'],
                            "driver": "netcdf",
                            "args": {
                                "urlpath": os.path.join(dataset_path, "*.nc"),
                                "engine": "netcdf4"
                            },
                            "metadata": {
                                "long_name": meta['long_name'],
                                "units": meta['units'],
                                "date_range": meta['date_range'],
                                "n_files": meta['n_files'],
                                "data_location": dataset_path
                            }
                        }

    return catalog

def write_catalog(catalog, output_path="catalogs/obs.yaml"):
    with open(output_path, 'w') as f:
        yaml.dump(catalog, f, sort_keys=False)
    print(f"✅ Catalog written to {output_path}")

# Main
if __name__ == "__main__":
    catalog = build_obs_catalog(BASE_DIR)
    write_catalog(catalog)
