"""
Run a number of dataflows and print cpu usage statistics,
to detect if we have an unwanted spinning worker.
Completely unscientific benchmarks here, but it should
be enough to make this specific problem evident.
"""

import json
import psutil
import subprocess
import sys

from time import sleep, time


def save_results(results):
    with open("results.json", "w") as f:
        json.dump(results, f)


def get_saved():
    try:
        with open("results.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Results couldn't be loaded: {e}")
        return None


def run(processes, args_string, prev=None):
    print()
    print(f"======> {args_string}, processes={processes}")
    proc = psutil.Popen(
        [
            "python",
            "-m",
            "bytewax.run",
            f"examples.spinningworkers.partitioned_input:get_flow({args_string})",
            f"-p{processes}",
        ],
        stdout=subprocess.DEVNULL,
    )
    start = time()
    cpu_times = proc.cpu_times()
    while True:
        cpu_times = proc.cpu_times()
        if proc.poll() is not None:
            break
        sleep(0.001)
    elapsed = time() - start
    if prev is not None:
        prev_cpu = prev["cputimes"]
        print(f"Elapsed:\t\t{elapsed:.2f}s (prev: {prev['elapsed']:.2f})")
        print(f"cpu_user:\t\t{cpu_times.user}s (prev: {prev_cpu[0]})")
        print(f"cpu_system:\t\t{cpu_times.system}s (prev: {prev_cpu[1]})")
        print(f"cpu_children_user:\t{cpu_times.children_user}s (prev: {prev_cpu[2]})")
        print(f"cpu_children_sys:\t{cpu_times.children_system}s (prev: {prev_cpu[3]})")
        print(f"cpu_iowait:\t\t{cpu_times.iowait}s (prev: {prev_cpu[4]})")
    else:
        print(f"Elapsed:\t\t{elapsed:.2f}s")
        print(f"cpu_user:\t\t{cpu_times.user}s")
        print(f"cpu_system:\t\t{cpu_times.system}s")
        print(f"cpu_children_user:\t{cpu_times.children_user}s")
        print(f"cpu_children_system:\t{cpu_times.children_system}s")
        print(f"cpu_iowait:\t\t{cpu_times.iowait}s")
    print("======")
    return {f"{args} {processes}": {"elapsed": elapsed, "cputimes": cpu_times}}


results = {}
saved = get_saved() or {}

for heavy_map in (False, True):
    for long_input in (False, True):
        for processes in (1, 16):
            # Try partitioned input with different number  of partitions
            for partitions in (1, 16):
                args = f"partitions={partitions}, long_input={long_input}, heavy_map={heavy_map}"
                results.update(**run(processes, args, saved.get(f"{args} {processes}", None)))
            # Try with dynamic input
            args = f"dynamic_input=True, long_input={long_input}, heavy_map={heavy_map}"
            results.update(**run(processes, args, saved.get(f"{args} {processes}", None)))

if "--save" in sys.argv:
    save_results(results)
