#!/bin/bash

BASE="/data/esplab/shared/model/initialized/NCAR-CESM2-CLIMO"

echo "Reorganizing under: $BASE"

# find experiments
for experiment in "$BASE"/*; do
  [ -d "$experiment" ] || continue

  # find datatypes
  for datatype in "$experiment"/*; do
    [ -d "$datatype" ] || continue

    ncar_dir="$datatype/NCAR-CESM2"
    if [ ! -d "$ncar_dir" ]; then
      continue
    fi

    for variable in "$ncar_dir"/*; do
      [ -d "$variable" ] || continue

      var_name=$(basename "$variable")
      target="$datatype/$var_name"

      if [ -e "$target" ]; then
        echo "⚠️  $target already exists, skipping"
        continue
      fi

      echo "✅ Moving $variable --> $target"
      mv "$variable" "$target"
    done

    # remove empty NCAR-CESM2 dir if now empty
    if [ ! "$(ls -A "$ncar_dir")" ]; then
      echo "🗑️  Removing empty $ncar_dir"
      rmdir "$ncar_dir"
    fi

  done
done

echo "🎉 Done."

