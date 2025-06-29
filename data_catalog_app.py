import yaml
import panel as pn

pn.extension()

def load_catalog(path):
    with open(path) as f:
        return yaml.safe_load(f)

def parse_sources(catalog):
    # Return a dict of keys -> metadata dict for all sources
    return catalog.get("sources", {})

def build_obs_controls(obs_sources):
    # Extract domain, variable, temp_res, dataset from keys
    # keys like: obs/gridded/atm/precip/daily/CMORPH
    domains = sorted(set(k.split('/')[2] for k in obs_sources))
    domain_select = pn.widgets.Select(name='Domain', options=domains)

    def update_variables(event):
        selected_domain = event.new
        variables = sorted(set(
            k.split('/')[3] for k in obs_sources if k.split('/')[2] == selected_domain
        ))
        variable_select.options = variables
        variable_select.value = variables[0] if variables else None

    domain_select.param.watch(update_variables, 'value')

    variables = sorted(set(
        k.split('/')[3] for k in obs_sources if k.split('/')[2] == domains[0]
    ))
    variable_select = pn.widgets.Select(name='Variable', options=variables)

    def update_temp_res(event):
        selected_domain = domain_select.value
        selected_variable = event.new
        temp_res = sorted(set(
            k.split('/')[4] for k in obs_sources
            if k.split('/')[2] == selected_domain and k.split('/')[3] == selected_variable
        ))
        temp_res_select.options = temp_res
        temp_res_select.value = temp_res[0] if temp_res else None

    variable_select.param.watch(update_temp_res, 'value')

    temp_res = sorted(set(
        k.split('/')[4] for k in obs_sources
        if k.split('/')[2] == domains[0] and k.split('/')[3] == variables[0]
    ))
    temp_res_select = pn.widgets.Select(name='Temporal Resolution', options=temp_res)

    def update_dataset(event):
        selected_domain = domain_select.value
        selected_variable = variable_select.value
        selected_temp_res = event.new
        datasets = sorted(set(
            k.split('/')[5] for k in obs_sources
            if k.split('/')[2] == selected_domain and
               k.split('/')[3] == selected_variable and
               k.split('/')[4] == selected_temp_res
        ))
        dataset_select.options = datasets
        dataset_select.value = datasets[0] if datasets else None

    temp_res_select.param.watch(update_dataset, 'value')

    datasets = sorted(set(
        k.split('/')[5] for k in obs_sources
        if k.split('/')[2] == domains[0] and
           k.split('/')[3] == variables[0] and
           k.split('/')[4] == temp_res[0]
    ))
    dataset_select = pn.widgets.Select(name='Dataset', options=datasets)

    return pn.Column(domain_select, variable_select, temp_res_select, dataset_select)

def show_metadata(obs_sources, domain, variable, temp_res, dataset):
    key = f"obs/gridded/{domain}/{variable}/{temp_res}/{dataset}"
    if key not in obs_sources:
        return pn.pane.Markdown(f"**No metadata found for {key}**")
    meta = obs_sources[key].get('metadata', {})
    lines = [f"### Metadata for `{key}`"]
    for k, v in meta.items():
        lines.append(f"- **{k}**: {v}")
    return pn.pane.Markdown('\n'.join(lines), width=400)

def main():
    obs_catalog = load_catalog("obs.yaml")
    rean_catalog = load_catalog("reanalysis.yaml")

    obs_sources = parse_sources(obs_catalog)
    rean_sources = parse_sources(rean_catalog)

    obs_controls = build_obs_controls(obs_sources)

    metadata_pane = pn.pane.Markdown("Select data to see metadata", width=400)

    def update_metadata(event):
        domain = obs_controls[0].value
        variable = obs_controls[1].value
        temp_res = obs_controls[2].value
        dataset = obs_controls[3].value
        metadata_pane.object = show_metadata(obs_sources, domain, variable, temp_res, dataset).object

    for widget in obs_controls:
        widget.param.watch(update_metadata, 'value')

    layout = pn.Row(
        pn.Column("# Observational Data Catalog", obs_controls),
        metadata_pane
    )

    layout.servable()

    return layout

#if __name__.startswith("bokeh"):
#    main()

if __name__ == "__main__":
    app = main()
    pn.serve(app, port=5006)
