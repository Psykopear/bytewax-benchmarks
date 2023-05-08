"""This program shows `hyperfine` benchmark results as a groupeb bar chart."""

import argparse
import json

import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("file", help="JSON file with benchmark results")
parser.add_argument("-o", "--output", help="Save image to the given filename.")
args = parser.parse_args()

with open(args.file) as f:
    results = json.load(f)["results"]

black = "#171717"
grey = "#c7c7c7"
yellow = "#fab90f"
white = "#f5f5f5"

revisions = [i["command"].partition("/")[0] for i in results]
x = np.arange(3)  # the label locations
width = 0.20  # the width of the bars

fig, ax = plt.subplots(layout="constrained")
fig.set_size_inches(10, 5)
fig.patch.set_facecolor(white)
ax.set_facecolor(white)

colors = [black, grey, yellow, white]

multiplier = 0
for i, result in enumerate(results):
    offset = width * multiplier
    rects = ax.bar(
        x + offset,
        (result["mean"], result["user"], result["system"]),
        width,
        label=result["command"].partition("/")[0],
        color=colors[i % len(colors)],
        edgecolor=black,
        linewidth=1,
    )
    ax.bar_label(rects, padding=3, color=black, fmt="%.3f")
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("Time (s)", color=black)
ax.set_title("CPU times", color=black)
ax.set_xticks(x + (width * len(revisions)) / 2 - width / 2, ["Real", "System", "User"])
fig.legend(loc="outside upper left", ncols=len(revisions))

if args.output:
    plt.savefig(args.output, dpi=199)
else:
    plt.show()
