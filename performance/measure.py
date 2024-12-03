#!/usr/bin/python3

# http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
import logging
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("installing webdriver")
webdriver_manager = ChromeDriverManager(chrome_type=ChromeType.GOOGLE)
chromedriver_path = webdriver_manager.install()

# logger = logging.getLogger('selenium')
# logger.setLevel(logging.DEBUG)

EXTENSION_PATH = str(Path.home() / "browser-extension/chrome")

if not Path(EXTENSION_PATH + "/manifest.json").is_file():
    raise ValueError("no manifest found at extension path, maybe wrong path given?")

PROXY_ADDRESS = "http://forward-proxy.scion:80"


def withScionExtension(options):
    options.add_argument("--disable-extensions-except=" + EXTENSION_PATH)
    options.add_argument("--load-extension=" + EXTENSION_PATH)


def withoutScionExtension(options):
    options.add_argument("--disable-extensions")


def withProxy(options, address):
    options.add_argument("--disable-extensions")
    options.add_argument(f"--proxy-server={address}")


def navigate_to(driver, address):
    logging.debug("opening URL")
    driver.get(address)

    logging.debug("measure timing")
    navigationStart = driver.execute_script(
        "return window.performance.timing.navigationStart"
    )
    responseStart = driver.execute_script(
        "return window.performance.timing.responseStart"
    )
    domComplete = driver.execute_script("return window.performance.timing.domComplete")

    time_to_first_byte = responseStart - navigationStart
    time_to_full_page_load = domComplete - responseStart

    return (time_to_first_byte, time_to_full_page_load)


ITERATIONS = 100
TTFB = "first byte ms"
TTPL = "page load ms"

CONFIGURE_EXTENSION = 0
CONFIGURE_NO_EXTENSION = 1
CONFIGURE_PROXY = 2

# the browser extension is connection to the forward-proxy.scion host
# depending on the target environment (local, prod), the host has to point to different IPs
# 127.0.0.1         forward-proxy.scion# local (running scion locally)
# <IP-ADDRESS>   forward-proxy.scion# prod (using in-network proxy)

PROD_ETHZ = "prod-ethz"
PROD_OVGU = "prod-ovgu"
PROD_ASHBURN = "prod-ashburn"
PROD_BRAZIL = "prod-brazil"
IP_ETHZ = "ip-ethz"
IP_OVGU = "ip-ovgu"
IP_ASHBURN = "ip-ashburn"
IP_BRAZIL = "ip-brazil"
STD_ETHZ = "std-ethz"
STD_OVGU = "std-ovgu"
STD_ASHBURN = "std-ashburn"
STD_BRAZIL = "std-brazil"
PROD_ACCOUNTS = "prod-accounts-ucdb"
IP_ACCOUNTS = "ip-accounts-ucdb"
STD_ACCOUNTS = "std-accounts-ucdb"
PROD_ASHBURN_TEST = "prod-ash-test"
PROD_BRAZIL_TEST = "prod-bra-test"
IP_ASHBURN_TEST = "ip-ash-test"
IP_BRAZIL_TEST = "ip-bra-test"
STD_ASHBURN_TEST = "std-ash-test"
STD_BRAZIL_TEST = "std-bra-test"


# ADAPT YOUR CONFIGURATIONS HERE
# some may require an entry in /etc/hosts to make the pan library work
configs = {
    PROD_ETHZ: [
        ("https://inf.ethz.ch","scion & extension",CONFIGURE_EXTENSION),
    ],
    IP_ETHZ: [
        ("https://inf.ethz.ch", "ip & extension", CONFIGURE_EXTENSION),
        ("https://inf.ethz.ch","ip & no extension",CONFIGURE_NO_EXTENSION),

    ],
    STD_ETHZ: [
        ("https://inf.ethz.ch", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_OVGU: [
        ("https://www.ovgu.de","scion & extension",CONFIGURE_EXTENSION),
    ],
    IP_OVGU: [
        ("https://www.ovgu.de", "ip & extension", CONFIGURE_EXTENSION),
        ("https://www.ovgu.de", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_OVGU: [
        ("https://www.ovgu.de", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_ASHBURN: [
        ("https://dfw.source.kernel.org","scion & extension",CONFIGURE_EXTENSION),
    ],
    IP_ASHBURN: [
        ("https://dfw.source.kernel.org", "ip & extension", CONFIGURE_EXTENSION),
        ("https://dfw.source.kernel.org", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_ASHBURN: [
        ("https://dfw.source.kernel.org", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_BRAZIL: [
        ("https://site.ucdb.br/", "scion & extension", CONFIGURE_EXTENSION),
    ],
    IP_BRAZIL: [
        ("https://site.ucdb.br/", "ip & extension", CONFIGURE_EXTENSION),
        ("https://site.ucdb.br/", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_BRAZIL: [
        ("https://site.ucdb.br/", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_ACCOUNTS: [
        ("https://accounts.ucdb.br/", "scion & extension", CONFIGURE_EXTENSION),
    ],
    IP_ACCOUNTS: [
        ("https://accounts.ucdb.br/", "ip & extension", CONFIGURE_EXTENSION),
        ("https://accounts.ucdb.br/", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_ACCOUNTS: [
        ("https://accounts.ucdb.br/", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_ASHBURN_TEST: [
        ("http://book.scion/index.html", "scion & extension", CONFIGURE_EXTENSION),
    ],
    IP_ASHBURN_TEST: [
        ("http://145.40.89.243/index.html", "ip & extension", CONFIGURE_EXTENSION),
        ("http://145.40.89.243/index.html", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_ASHBURN_TEST: [
        ("http://145.40.89.243/index.html", "std & proxy", CONFIGURE_PROXY),
    ],
    PROD_BRAZIL_TEST: [
        ("http://ucdb.br.scion/index.html", "scion & extension", CONFIGURE_EXTENSION),
    ],
    IP_BRAZIL_TEST: [
        ("http://200.129.206.243/index.html", "ip & extension", CONFIGURE_EXTENSION),
        ("http://200.129.206.243/index.html", "ip & no extension", CONFIGURE_NO_EXTENSION),
    ],
    STD_BRAZIL_TEST: [
        ("http://200.129.206.243/index.html", "std & proxy", CONFIGURE_PROXY),
    ],
}
# YOUR TAGET HERE
#config_targets = [PROD_BRAZIL, PROD_OVGU, PROD_ETHZ, STD_BRAZIL, STD_OVGU, STD_ETHZ]
config_targets = [PROD_BRAZIL, STD_BRAZIL]
#config_targets = [IP_ACCOUNTS]
#config_targets = [PROD_BRAZIL_TEST, IP_BRAZIL_TEST, STD_BRAZIL_TEST]
#config_targets = [IP_BRAZIL, IP_OVGU, IP_ETHZ]
for config_name in config_targets:
    dfs = list()
    for address, name, type in configs[config_name]:
        logging.info(f"running {address}/{name}")

        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        if type == CONFIGURE_EXTENSION:
            withScionExtension(options)
        elif type == CONFIGURE_NO_EXTENSION:
            withoutScionExtension(options)
        elif type == CONFIGURE_PROXY:
            withProxy(options, PROXY_ADDRESS)
        else:
            raise ValueError(f"unknown type '{type}'")

        times_to_first_byte = list()
        times_to_full_page_load = list()

        for i in range(ITERATIONS):
            if i % 5 == 4:
                duration = 5
                logging.info(f"cooling down for {duration} seconds")
                time.sleep(duration)

            logging.info(f"running {i+1}/{ITERATIONS}")

            logging.debug("creating driver")
            driver = webdriver.Chrome(
                service=Service(chromedriver_path),
                options=options,
            )
            try:
                # disable browser cache
                driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

                time_to_first_byte, time_to_full_page_load = navigate_to(driver, address)

                times_to_first_byte.append(time_to_first_byte)
                times_to_full_page_load.append(time_to_full_page_load)

                logging.info(f"Time to first byte: {time_to_first_byte} ms")
                logging.info(f"Time to full page load: {time_to_full_page_load} ms")
            finally:
                driver.quit()

        dfs.append(
            pd.DataFrame(
                {
                    TTFB: times_to_first_byte,
                    TTPL: times_to_full_page_load,
                },
            ),
        )

    df = pd.concat(dfs, axis=1)
    df.columns = pd.MultiIndex.from_product(
        [
            [config[1] for config in configs[config_name]],
            [TTFB, TTPL],
        ],
    )
    logging.info(f"\n{df}")
    filename = (
        f"./data/data-{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}-{config_name}.csv"
    )
    df.to_csv(filename)
    logging.info(f"written to {filename}")
