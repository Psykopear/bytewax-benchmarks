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

yellow = "#fab90f"
black = "#171717"
white = "#e5e5e5"

commands = [i["command"].partition("/")[0] for i in results]
x = np.arange(3)  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots(layout="constrained")
fig.patch.set_facecolor(white)
ax.set_facecolor(white)

edgecolor = yellow
color = black

multiplier = 0
for result in results:
    offset = width * multiplier
    rects = ax.bar(
        x + offset,
        (result["mean"], result["user"], result["system"]),
        width,
        label=result["command"].partition("/")[0],
        color=color,
        edgecolor=edgecolor,
        linewidth=1,
    )
    color, edgecolor = edgecolor, color
    ax.bar_label(rects, padding=3, color=black)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("Time (s)", color=black)
ax.set_title("CPU times", color=black)
ax.set_xticks(x + width / 2, ["Real", "System", "User"])
fig.legend(loc="outside upper left", ncols=len(commands))

if args.output:
    plt.savefig(args.output)
else:
    plt.show()
