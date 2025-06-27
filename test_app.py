import intake

cat = intake.open_catalog("top_catalog.yaml")
print("Top-level entries:", list(cat))

for key in cat:
    print(f"--- {key} ---")
    subcat = cat[key]()
    print("Subentries:", list(subcat))
