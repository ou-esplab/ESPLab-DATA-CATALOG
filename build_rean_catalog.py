### Import the needed packages and disable warnings
import os
import yaml
import xarray as xr
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Define the base directory to build the reanalysis catalog off of and ignore certain subdirectories and files
BASE_DIR = "/data/esplab/shared/reanalysis"
IGNORE_DIRS = {'tmp', 'old_versions', '.ipynb_checkpoints'}
IGNORE_FILES = {"land_sea_mask.nc", "era5_precip_daily.1979-01-01.2020-12-31.nc"}

# Define a function to find all the .nc files under a certain directory
def get_netcdf_files(directory):
    # Get the files in the directory, join their paths and sort them if the file ends with .nc and .nc4 while ignoring specific files
    files = sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if ((f.endswith(".nc") or f.endswith(".nc4"))
            and os.path.isfile(os.path.join(directory, f))
            and f not in IGNORE_FILES)])
    # Print out a statement that no .nc files were found in the directory and that the code will be looking deeper
    if len(files) == 0:
        print(f" No NetCDF files found in {directory}, looking deeper...")
        print()
    # Print out how many netCDF files were found in the directory and return them if they exist
    if len(files) > 0:
        print(f"Found {len(files)} NetCDF files in {directory}")
    return files

# Define a function to extract the metadata from all of the .nc files in a list
def extract_metadata_all_files(nc_files):
    # From a list of .nc files, try to
    try:
        # Open all the files in the list and combine them into one dataset by their coordinates
        ds = xr.open_mfdataset(nc_files, combine='by_coords', parallel=False)
        var_name = list(ds.data_vars)[-1] if ds.data_vars else "unknown" # Get the last variable name of the data if there are data variables
        long_name = ds[var_name].attrs.get('long_name', var_name) # Get the long name of the variable from the attributes of the data
        units = ds[var_name].attrs.get('units', 'unknown') # Get the units of the variable from the attributes of the data
        # If time is a coordinate of the datafile
        if "time" in ds.coords:
            times = pd.to_datetime(ds.time.values, errors='coerce') # Convert all the time values to datetime times
            times = times.dropna() if hasattr(times, 'dropna') else times # If the times object has the ability to drop NaNs, then drop any NaNs
            # If the number of times is equal to zero, return the date range as unknown
            if len(times) == 0:
                date_range = "unknown"
            # If the number of times is more than zero, get the date range as strings of the minimum and maximum time
            else:
                date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}"
        # If time is not a coordinate of the data file, return the date range as unknown
        else:
            date_range = "unknown"
        # Close the combined dataset of data files
        ds.close()
        # Return the long name, units, date range of the data, and the number of .nc files found and set them to a dictionary
        return {
            "long_name": long_name,
            "units": units,
            "date_range": date_range,
            "n_files": len(nc_files)
        }
    # If combining all files fails, try reading metadata from one file and date range from all files
    except Exception as e:
        print(f"⚠️ Failed to combine files, falling back to single file + aggregate date range: {e}")
        try:
            # Open just the first file to get variable metadata
            ds = xr.open_dataset(nc_files[0])
            var_name = list(ds.data_vars)[-1] if ds.data_vars else "unknown"
            long_name = ds[var_name].attrs.get('long_name', var_name)
            units = ds[var_name].attrs.get('units', 'unknown')
            ds.close()
            
            # Extract date range by reading time from ALL files individually
            all_times = []
            for f in nc_files:
                try:
                    ds_temp = xr.open_dataset(f)
                    if "time" in ds_temp.coords:
                        t = pd.to_datetime(ds_temp.time.values, errors='coerce')
                        all_times.extend(pd.Series(t).dropna().tolist())
                    ds_temp.close()
                except Exception:
                    continue  # Skip files that can't be opened
            
            if len(all_times) > 0:
                times = pd.Series(all_times)
                date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}"
            else:
                date_range = "unknown"
            
            return {
                "long_name": long_name,
                "units": units,
                "date_range": date_range,
                "n_files": len(nc_files)
            }
        except Exception as e2:
            print(f"⚠️ Failed to extract metadata from {nc_files[0]}: {e2}")
            return {
                "long_name": "unknown",
                "units": "unknown",
                "date_range": "unknown",
                "n_files": len(nc_files)
            }

# Define a function to get all the dataset variables and their metadata from the MERRA-2 reanalysis dataset
def get_merra2_metadata(nc_files):
    # From a list of .nc files, try to
    try:
        # Open only one file to get the variable metadata
        ds_sample = xr.open_dataset(nc_files[0])

        # Get all the variables in the dataset
        variables = list(ds_sample.data_vars)

        # Set an empty dictionary for the variable metadata
        var_metadata = {}

        # For each variable in the dataset, get the long name and units of the variable and add them to the dictionary
        for var in variables:
            var_metadata[var] = {
                "long_name": ds_sample[var].attrs.get("long_name", var),
                "units": ds_sample[var].attrs.get("units", "unknown")}
        # Close the single MERRA-2 file
        ds_sample.close()

        # Set an empty list for the times of the MERRA-2 dataset
        all_times = []

        # For each file in the MERRA-2 files
        for f in nc_files:
            # Try to open the file
            try:
                ds_temp = xr.open_dataset(f)
                # If time is a coordinate of the data, convert the time values to datetime and add them to the all times list while dropping NaNs
                if "time" in ds_temp.coords:
                    t = pd.to_datetime(ds_temp.time.values, errors="coerce")
                    all_times.extend(pd.Series(t).dropna().tolist())
                # Close the file
                ds_temp.close()
            except Exception:
                # Skip files that can't be opened
                continue

        # If the length of MERRA-2 dataset times is more than one, convert the list of times to a pandas series
        if len(all_times) > 0:
            times = pd.Series(all_times)
            # Get the date range as strings of the minimum and maximum time
            date_range = f"{times.min().strftime('%Y-%m-%d')} to {times.max().strftime('%Y-%m-%d')}"
        # If the length of MERRA-2 dataset times is zero, return the date range as unknown
        else:
            date_range = "unknown"
        # Return the variable metadata and the date range of the MERRA-2 dataset
        return var_metadata, date_range
    # If an error occurs, print that the metadata extraction failed, the error, return the metadata as blank, and date range of the data as unknown
    except Exception as e:
        print(f"⚠ MERRA metadata extraction failed: {e}")
        return {}, "unknown"
    
# Create an empty catalog to append to
catalog = {
    "metadata": {
        "title": "Reanalysis Data Catalog",
        "version": 1,
        "description": "Auto-generated reanalysis data catalog"
    },
    "sources": {}
}

# Print a statement that the defined base directory is being scanned for reanalysis files
print(f"🔍 Scanning base directory: {BASE_DIR}")

##### Filepath to the data is usually as follows: reanalysis/<dataset>/<tempres>/<variable #####
#####                                         Ex: reanalysis/era5/daily/q                  #####
#####                                         Ex: reanalysis/era5-land/hourly/precip       #####
#####                                         Ex: reanalysis/merra-2/daily/zg500           #####

# For the directory itself and all directories and files inside of it
for root, dirs, files in os.walk(BASE_DIR):
    # Set the list of directories for those that are not in the ignored directories
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

    # Use the function to get and sort all of the files in the root base directory
    nc_files = get_netcdf_files(root)
    # If there are no .nc files in the root base directory, continue
    if not nc_files:
        continue

    # Compute the relative path to each folder or file compared to the base directory
    rel_path = os.path.relpath(root, BASE_DIR)
    # Calculate how many directories there are to get from the base directory to the folder or file by splitting the relative path
    parts = rel_path.split(os.sep)

    # Check for MERRA-2 3-hourly special case FIRST (before the path length check)
    # This structure is reanalysis/<dataset>/<tempres> with all variables in one directory
    if len(parts) == 2 and parts[0].lower() == "merra-2" and parts[1] == "3-hourly":
        print(f"✔ Processing MERRA-2 3-hourly dataset at {root}")
        print()

        # Use the function to get and sort all of the files in the directory
        nc_files = get_netcdf_files(root)
        # If there are no .nc files in the directory, continue
        if not nc_files:
            continue

        # Use the MERRA-2 metadata function to get the metadata for each variable and the date range of the dataset
        var_meta, date_range = get_merra2_metadata(nc_files)

        # For each variable and its metadata in the variable metadata dictionary
        for var_name, meta_info in var_meta.items():
            # Define the key path to where the subdirectory data is found
            key = f"reanalysis/{parts[0]}/{parts[1]}/{var_name}"
            # Append the catalog for a subdirectory filepath with the resulting metadata
            catalog["sources"][key] = {
                "description": meta_info["long_name"],
                "driver": "netcdf",
                "args": {
                    "urlpath": os.path.join(root, "*.nc4"),
                    "engine": "netcdf4"
                },
                "metadata": {
                    "long_name": meta_info["long_name"],
                    "units": meta_info["units"],
                    "date_range": date_range,
                    "n_files": len(nc_files),
                    "data_location": root
                }
            }

            print(f"Processed variable {var_name} in the MERRA-2 3-hourly dataset and added it to the catalog.")
            print()

        continue

    # For all other datasets, enforce the 3-part path structure: reanalysis/<dataset>/<tempres>/<variable>
    if len(parts) != 3:
        continue  # Expecting reanalysis/<dataset>/<tempres>/<variable>

    # From the split relative path get the dataset, temporal resolution, and variable and show that this relative path is being processed
    dataset, tempres, variable = parts
    print(f"✔️ Processing reanalysis/{dataset}/{tempres}/{variable}")
    print()

    # Use the function to extract the metadata from all the .nc files in a directory
    meta = extract_metadata_all_files(nc_files)
    # Define the key path to where the subdirectory data is found
    key = f"reanalysis/{dataset}/{tempres}/{variable}"
    # Append the catalog for a subdirectory filepath with the resulting metadata
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

# Define the output path for the written .yaml file
output_path = "catalogs/reanalysis.yaml"

# Make the output directory and path if it does not exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Write to the output path the updated catalog as a .yaml file and print that it was written
with open(output_path, 'w') as f:
    yaml.dump(catalog, f, sort_keys=False)
print(f"✅ Catalog written to {output_path}")
