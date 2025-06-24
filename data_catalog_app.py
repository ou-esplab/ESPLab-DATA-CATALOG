import panel as pn
import intake

pn.extension()

print("Opening catalog...")
cat = intake.open_catalog("top_catalog.yaml")
print("Catalog opened.")

# Build hierarchy: category → subcategory → variable list
print("Building hierarchy tree...")
tree = {}
for name in cat._entries:
    parts = name.split('/')
    if len(parts) >= 3:
        top, mid, var = parts[0], parts[1], '/'.join(parts[2:])
        tree.setdefault(top, {}).setdefault(mid, []).append(var)
print("Hierarchy tree built.")

# Widgets
category_select = pn.widgets.Select(name="Category", options=list(tree))
subcategory_select = pn.widgets.Select(name="Subcategory", options=[])
variable_select = pn.widgets.Select(name="Variable", options=[])

info_pane = pn.pane.Markdown("Select a variable to view metadata.", width=400)
ds_pane = pn.pane.Markdown("Dataset preview will appear here.", sizing_mode='stretch_width', height=300)

def update_subcategories(event):
    category = event.new
    print(f"Category selected: {category}")
    subcats = list(tree.get(category, {}))
    subcategory_select.options = subcats
    if subcats:
        subcategory_select.value = subcats[0]
    else:
        subcategory_select.options = []
        variable_select.options = []
        info_pane.object = "No subcategories available."
        ds_pane.object = ""

def update_variables(event):
    subcat = event.new
    cat_value = category_select.value
    print(f"Subcategory selected: {subcat}")
    vars = tree.get(cat_value, {}).get(subcat, [])
    variable_select.options = vars
    if vars:
        variable_select.value = vars[0]
    else:
        variable_select.options = []
        info_pane.object = "No variables available."
        ds_pane.object = ""

def update_info(event):
    cat_val = category_select.value
    subcat_val = subcategory_select.value
    var_val = variable_select.value
    print(f"Variable selected: {var_val}")

    full_key = f"{cat_val}/{subcat_val}/{var_val}"
    if full_key in cat:
        entry = cat[full_key]
        try:
            md = entry.describe().get('metadata', {})
        except Exception as e:
            print(f"Error getting metadata: {e}")
            md = {}

        info_text = f"""### {var_val}
- **Units:** {md.get('units', 'N/A')}
- **Date Range:** {md.get('date_range', 'N/A')}
- **Number of Files:** {md.get('n_files', 'N/A')}
- **Data Path:** `{md.get('data_location', 'N/A')}`"""
        info_pane.object = info_text

        # Load dataset lazily and show summary (string repr)
        try:
            ds = entry()
            ds_summary = str(ds)
            ds_pane.object = f"```python\n{ds_summary}\n```"
        except Exception as e:
            ds_pane.object = f"**Failed to load dataset:** {e}"
            print(f"Failed to load dataset for {full_key}: {e}")
    else:
        info_pane.object = "No matching dataset."
        ds_pane.object = ""

# Connect watchers
category_select.param.watch(update_subcategories, 'value')
subcategory_select.param.watch(update_variables, 'value')
variable_select.param.watch(update_info, 'value')

# Trigger initial cascade to populate subcategory and variable dropdowns
update_subcategories(type("event", (), {"new": category_select.value}))
update_variables(type("event", (), {"new": subcategory_select.value}))
update_info(type("event", (), {"new": variable_select.value}))

# Layout
app = pn.Column(
    pn.Row(category_select, subcategory_select, variable_select),
    pn.Spacer(height=10),
    info_pane,
    ds_pane
)

# Make the app servable for panel serve and Binder
if __name__.startswith("bokeh"):
    app.servable()
