import intake

cat = intake.open_catalog("obs.yaml")
print(cat._entries["obs/gridded/atm/precip/monthly/CPC-UNI-HIRES"].metadata)
