import os
import glob
import xarray as xr
import yaml
from tqdm import tqdm

def get_metadata_from_sample_file(filepath):
    try:
        with xr.open_dataset(filepath, decode_times=False) as ds:
            time = ds['time']
            date_range = (str(xr.decode_cf(ds).time.min().values)[:10],
                          str(xr.decode_cf(ds).time.max().values)[:10]) if 'time' in ds else ('unknown', 'unknown')
            metadata = {
                "long_name": getattr(time, 'long_name', 'unknown'),
                "units": getattr(time, 'units', 'unknown'),
                "date_range": f"{date_range[0]} to {date_range[1]}"
            }
            # Optionally include other dims
            for dim in ['latitude', 'longitude', 'level']:
                if dim in ds:
                    metadata[f"{dim}_size"] = ds[dim].size
            return metadata
    except Exception as e:
        return {
            "long_name": "unknown",
            "units": "unknown",
            "date_range": "unknown",
            "error": str(e)
        }

def build_catalog(rean_dir="/data/esplab/shared/reanalysis", output_yaml="reanalysis.yaml"):
    catalog = {
        "metadata": {
            "title": "Reanalysis Data Catalog",
            "version": 1,
            "description": "Auto-generated reanalysis data catalog"
        },
        "sources": {}
    }

    for root, dirs, files in os.walk(rean_dir):
        if not files:
            continue
        nc_files = sorted(glob.glob(os.path.join(root, "*.nc")))
        if not nc_files:
            continue

        rel_path = os.path.relpath(root, rean_dir)
        parts = rel_path.split(os.sep)
        if len(parts) != 3:
            continue  # Expecting dataset/temp_res/variable

        dataset, temp_res, variable = parts
        entry_name = f"reanalysis/{dataset}/{temp_res}/{variable}"

        sample_file = nc_files[0]
        metadata = get_metadata_from_sample_file(sample_file)
        metadata["n_files"] = len(nc_files)
        metadata["data_location"] = root

        catalog["sources"][entry_name] = {
            "description": f"{metadata.get('long_name', 'unknown')} ({metadata.get('units', 'unknown')}), {metadata.get('date_range', 'unknown')}",
            "driver": "netcdf",
            "args": {
                "urlpath": os.path.join(root, "*.nc"),
                "engine": "netcdf4"
            },
            "metadata": metadata
        }

    with open(output_yaml, "w") as f:
        yaml.dump(catalog, f, sort_keys=False)

    print(f"Catalog written to {output_yaml}")

if __name__ == "__main__":
    build_catalog()
