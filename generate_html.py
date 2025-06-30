import os
import yaml

# Paths to your YAML catalogs
OBS_YAML = "catalogs/obs.yaml"
REANALYSIS_YAML = "catalogs/reanalysis.yaml"

# Output directory for generated HTML files
OUTPUT_DIR = "docs"

# Simple HTML template with placeholders
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p><strong>Description:</strong> {description}</p>
    <p><strong>Units:</strong> {units}</p>
    <p><strong>Date range:</strong> {date_range}</p>
    <p><strong>Number of files:</strong> {n_files}</p>
    <p><strong>Data location:</strong> {data_location}</p>
</body>
</html>
"""

def load_catalog(path):
    with open(path, "r") as f:
        catalog = yaml.safe_load(f)
    return catalog

def generate_html_for_catalog(catalog, category_name):
    sources = catalog.get("sources", {})
    print(f"Generating HTML pages for {category_name} ({len(sources)} datasets)...")
    
    for source_key, source_info in sources.items():
        # source_key example: "obs/gridded/atm/precip/monthly/NOAA-PRECL"
        # split key to get folder structure + filename
        parts = source_key.split("/")
        # last part is dataset name, use for filename
        filename = parts[-1] + ".html"
        # folders for path = everything except last part
        folder_path = os.path.join(OUTPUT_DIR, *parts[:-1])
        os.makedirs(folder_path, exist_ok=True)
        
        # gather metadata for HTML page
        description = source_info.get("description", "No description")
        meta = source_info.get("metadata", {})
        units = meta.get("units", "unknown")
        date_range = meta.get("date_range", "unknown")
        n_files = meta.get("n_files", "unknown")
        data_location = meta.get("data_location", "unknown")
        
        # build title from source key or long_name
        title = f"{source_key}"
        if meta.get("long_name"):
            title = meta.get("long_name")
        
        # fill template
        html_content = HTML_TEMPLATE.format(
            title=title,
            description=description,
            units=units,
            date_range=date_range,
            n_files=n_files,
            data_location=data_location
        )
        
        output_file = os.path.join(folder_path, filename)
        with open(output_file, "w") as f:
            f.write(html_content)
        
        print(f"  - Wrote {output_file}")

def generate_overview_page(category, entries, OUTPUT_DIR):
    # category: "obs" or "reanalysis"
    page_path = os.path.join(OUTPUT_DIR, f"{category}.html")
    with open(page_path, 'w') as f:
        f.write(f"<html><head><title>{category.capitalize()} Data Overview</title></head><body>\n")
        f.write(f"<h1>{category.capitalize()} Data</h1>\n<ul>\n")
        for key, info in sorted(entries.items()):
            # key example: obs/gridded/atm/precip/monthly/NOAA-PRECL
            # Build relative URL to detailed page HTML:
            # Assuming detailed pages are under OUTPUT_DIR/obs/... or output_dir/reanalysis/...
            relative_path = key.replace("/", "_") + ".html"  # or your existing naming scheme
            f.write(f'<li><a href="{category}/{relative_path}">{info["description"]}</a></li>\n')
        f.write("</ul>\n")
        f.write('<p><a href="index.html">Back to Home</a></p>\n')
        f.write("</body></html>\n")


def main():
    # Load and generate for obs
    obs_catalog = load_catalog(OBS_YAML)
    generate_html_for_catalog(obs_catalog, "Observations")
    
    # Load and generate for reanalysis
    reanalysis_catalog = load_catalog(REANALYSIS_YAML)
    generate_html_for_catalog(reanalysis_catalog, "Reanalysis")

    # Example usage after detailed pages generation:
    generate_overview_page("obs", obs_catalog["sources"], OUTPUT_DIR)
    generate_overview_page("reanalysis", reanalysis_catalog["sources"], OUTPUT_DIR)

if __name__ == "__main__":
    main()

