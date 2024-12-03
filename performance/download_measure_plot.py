import matplotlib.pyplot as plt
import pycurl
from io import BytesIO
import datetime

ITERATIONS = 100

PROD_BRAZIL_TEST = "bra-test"
targets = {
    PROD_BRAZIL_TEST: [
        ("http://ucdb.br.scion/BOOK.pdf", "scion"),
        ("http://200.129.206.243/BOOK.pdf", "ip"),
        ("http://200.129.206.243/BOOK.pdf", "proxy"),
    ],
}

def measure_download(url, use_scion, use_proxy=False):
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.FOLLOWLOCATION, True)
            c.setopt(c.NOPROGRESS, True)
            c.setopt(c.TIMEOUT, 60)
            if use_scion:
                c.setopt(c.PROXY, "https://forward-proxy.scion:9443")
                c.setopt(c.PROXYUSERPWD, "policy:")
                c.setopt(c.PROXY_SSL_VERIFYPEER, 0)
                c.setopt(c.PROXY_SSL_VERIFYHOST, 0)
            elif use_proxy:
                c.setopt(c.PROXY, "http://forward-proxy.scion:80")
            c.perform()
            connect_time = c.getinfo(c.CONNECT_TIME)
            start_transfer_time = c.getinfo(c.STARTTRANSFER_TIME)
            total_time = c.getinfo(c.TOTAL_TIME)
            c.close()
            print(f"Connect: {connect_time}s\nStart Transfer: {start_transfer_time}s\nTotal: {total_time}s\n")
            return total_time

def plot_results(name, results):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    fig.suptitle("Download time for SCION book", fontsize=12, fontweight="bold")
    ax.set_title(f"TARGET: {name} (n={ITERATIONS})")
    ax.set_ylabel("Time in seconds")
    ax.set_xlabel("Protocol")
    ax.boxplot(results.values(), labels=results.keys(), showfliers=False)
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")
    filename = f"{name}_download_{date_str}.png"
    plt.savefig(f"plots/{filename}")
    plt.close()

if __name__ == "__main__":
    for name, urls in targets.items():
        results = dict()
        for url, protocol in urls:
            use_scion = protocol == "scion"
            use_proxy = protocol == "proxy"
            for i in range(ITERATIONS):
                result = measure_download(url, use_scion, use_proxy)
                results.setdefault(protocol, []).append(result)
        plot_results(name, results)


