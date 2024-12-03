import matplotlib.pyplot as plt
import pandas as pd

files = {
    100: "data/data_2025-02-07_07:56:51_100_ethz.csv",
    200: "data/data_2025-02-07_08:21:42_200_ethz.csv",
    300: "data/data_2025-02-07_08:31:15_300_ethz.csv",
    400: "data/data_2025-02-07_08:32:03_400_ethz.csv",
    500: "data/data_2025-02-07_08:34:05_500_ethz.csv",
    600: "data/data_2025-02-07_08:51:15_600_ethz.csv",
    700: "data/data_2025-02-07_08:53:01_700_ethz.csv",
    800: "data/data_2025-02-07_08:53:49_800_ethz.csv",
    900: "data/data_2025-02-07_09:24:38_900_ethz.csv",
    1000: "data/data_2025-02-07_09:15:33_1000_ethz.csv",
}

data = list()
for vus, file_name in files.items():
    df = pd.read_csv(file_name, delimiter=",")
    durations = df.loc[df["metric_name"] == "http_req_duration"]
    values = durations["metric_value"]
    data.append(values)

fig = plt.figure(figsize=(6, 4), dpi=300)
fig.suptitle("Load Test Measurements", fontsize=12, fontweight="bold")
fig.autofmt_xdate()

ax = fig.add_subplot(1, 1, 1)
ax.set_title("HTTP forward proxy")
ax.set_xlabel("Concurrent Users")
ax.set_xticklabels([str(i) for i in range(100, 1001, 100)])
ax.set_ylabel("Request Duration [ms]")
bp = ax.boxplot(data, showfliers=False)

plot_filename = f"data/plot-load-test.png"
plt.savefig(plot_filename)
