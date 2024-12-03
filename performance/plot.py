import re
import sys

import matplotlib.pyplot as plt
import pandas as pd

TTFB = "ttfb"
TTPL = "ttpl"
TITLE = "title"
COLNAME = "colname"
YAXIS = "yaxis"

NAMES = {
    TTFB: {
        COLNAME: "first byte ms",
        TITLE: "Time to First Byte",
        YAXIS: "Time to first byte [ms]",
    },
    TTPL: {
        COLNAME: "page load ms",
        TITLE: "Page Load Time",
        YAXIS: "page load time [ms]",
    },
}

TARGETS = {
    "ethz": "ethz.ch",
    "ovgu": "netsys.ovgu.de",
    "ashburn": "dfw.source.kernel.org",
    "brazil": "ucdb.br",
    "ash-test": "Test dfw.source.kernel.org (Ashburn)",
    "bra-test": "Test ucdb.br (Brazil)",
    "accounts-ucdb": "accounts.ucdb.br",
}

SCENARIOS = {
    "scion & extension": "SCION via\nforward\nproxy",
    "ip & extension": "BGP/IP via\nforward\nproxy",
    "std & proxy": "Reference\nforward\nproxy",
    "ip & no extension": "BGP/IP",
}

HIST_PLOT_POSITIONS = {
    "scion & extension": (2, 2, 1),
    "ip & extension": (2, 2, 2),
    "std & proxy": (2, 2, 3),
    "ip & no extension": (2, 2, 4),
}

# read csvs and concat
dfs = []
types = []
dates = []
target_host = None
for filename in sys.argv[1:]:
    m = re.search(
        r"data-(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})-([a-z\-]+)(_[a-z]+){0,2}.csv",
        filename,
    )
    date = m.group(1)
    dates.append(date)
    type = m.group(2)
    types.append(type)

    known_type = False
    for target, _ in TARGETS.items():
        if target in type:
            known_type = True
            target_host = target
            break

    if not known_type:
        raise ValueError(f"unknown target '{type}'")

    df = pd.read_csv(filename, delimiter=",", index_col=0, header=[0, 1])
    dfs.append(df)

df = pd.concat(dfs, axis=1)
n = len(df)
print(df)

# create plots
for key in [TTFB, TTPL]:
    title = NAMES[key][TITLE]
    yaxis_title = NAMES[key][YAXIS]
    col_name = NAMES[key][COLNAME]

    # sequence plot
    seqplot_fig = plt.figure(figsize=(6, 4), dpi=300)
    seqplot_fig.suptitle(title, fontsize=12, fontweight="bold")
    seqplot_fig.autofmt_xdate()

    seqplot_ax = seqplot_fig.add_subplot(1, 1, 1)
    seqplot_ax.set_title(f"{TARGETS[target_host]} (n={n})")
    seqplot_ax.set_xlabel("Iteration")
    seqplot_ax.set_ylabel(yaxis_title)

    # box plot
    boxplot_fig = plt.figure(figsize=(6, 4), dpi=300)
    boxplot_fig.suptitle(title, fontsize=12, fontweight="bold")
    boxplot_fig.autofmt_xdate()

    boxplot_ax = boxplot_fig.add_subplot(1, 1, 1)
    boxplot_ax.set_title(f"{TARGETS[target_host]} (n={n})")
    boxplot_ax.set_xlabel("Scenarios")
    boxplot_ax.set_ylabel(yaxis_title)

    # hist plot
    histplot_fig = plt.figure(figsize=(6, 4), dpi=300)
    histplot_fig.suptitle(title, fontsize=12, fontweight="bold")
    histplot_fig.autofmt_xdate()

    data = []
    labels = []
    for scenario, label in SCENARIOS.items():
        if not scenario in df:
            print(scenario)
            continue

        values = df[scenario][col_name].values.flatten()
        data.append(values)
        labels.append(label)

        seqplot_ax.plot([*range(len(values))], values, label=label)

        histplot_ax = histplot_fig.add_subplot(*HIST_PLOT_POSITIONS[scenario])
        histplot_ax.set_title(f"{TARGETS[target_host]} (n={n})")
        histplot_ax.set_xlabel(label.replace("\n", " "))
        histplot_ax.set_ylabel(yaxis_title)

        histplot_ax.hist(values, density=False, bins=100)

    seqplot_ax.legend()

    boxplot_ax.set_xticklabels(labels, rotation=0)
    boxplot_ax.boxplot(data, showfliers=False)

    histplot_fig.tight_layout()

    file_name_part = "first-byte" if key == TTFB else "page-load"
    for plot, plot_type in [
        (seqplot_fig, "sequence"),
        (boxplot_fig, "boxplot"),
        (histplot_fig, "hist"),
    ]:
        plot_filename = f"plots/plot-{plot_type}-{file_name_part}-{'-'.join(dates)}-{target_host}_{n}.png"
        plot.savefig(plot_filename)
        print(plot_filename)
