pythons=""

for i do
  # Create virtualenv, upgrade pip, install the proper version of bytewax
  python -m venv .bytewax-"$i"
  .bytewax-"$i"/bin/pip install --upgrade pip
  .bytewax-"$i"/bin/pip install git+https://github.com/bytewax/bytewax.git@"$i"

  if [[ -z "$pythons" ]]; then
    pythons=.bytewax-"$i"/bin/python
  else
    pythons=$pythons,.bytewax-"$i"/bin/python
  fi
done

rm -rf results/
mkdir results

# Partitioned input
hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.partitioned:get_flow(long_input=False, heavy_map=False)\" -p16" \
  --export-json results/partitioned.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.partitioned:get_flow(long_input=True, heavy_map=False)\" -p16" \
  --export-json results/partitioned-long-input.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.partitioned:get_flow(long_input=False, heavy_map=True)\" -p16" \
  --export-json results/partitioned-heavy-map.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.partitioned:get_flow(long_input=True, heavy_map=True)\" -p16" \
  --export-json results/partitioned-long-input-heavy-map.json

# Dynamic input
hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.dynamic:get_flow(long_input=False, heavy_map=False)\" -p16" \
  --export-json results/dynamic.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.dynamic:get_flow(long_input=True, heavy_map=False)\" -p16" \
  --export-json results/dynamic-long-input.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.dynamic:get_flow(long_input=False, heavy_map=True)\" -p16" \
  --export-json results/dynamic-heavy-map.json

hyperfine \
  -L python $pythons \
  "{python} -m bytewax.run \"dataflows.dynamic:get_flow(long_input=True, heavy_map=True)\" -p16" \
  --export-json results/dynamic-long-input-heavy-map.json
