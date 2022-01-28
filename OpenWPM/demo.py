from pathlib import Path

from custom_command import LinkCountingCommand, FormAnalyzingCommand, DatabaseCheckCommand, JSInstrumentCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager
import requests
import sys
import json
import datetime

f = open('../../OpenWPMListInput.json',) 

START = 0
FINISH = 10000

# The list of sites that we wish to crawl
NUM_BROWSERS = 1
sites = json.load(f)
# sites = [
#     'https://actionnetwork.org/users/sign_in',
# ]

f.close()

# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = False
    # Record Navigations
    browser_param.navigation_instrument = False
    # Record JS Web API calls
    browser_param.js_instrument = False
    browser_param.js_instrument_settings = ["collection_fingerprinting"]
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = False
    # Record DNS resolution
    browser_param.dns_instrument = False

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True

# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )
            if not success:
                file1 = open("history2.txt", "a")  # append mode
                file1.write(f'0: {val}\n')
                r = requests.post('http://localhost:3050/log_track', json={ 'page_url': val, 'is_successful': False, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'ith_start': START, 'ith_end': FINISH })
                file1.close()
            else:
                file1 = open("history2.txt", "a")  # append mode
                file1.write(f'1: {val}\n')
                r = requests.post('http://localhost:3050/log_track', json={ 'page_url': val, 'is_successful': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'ith_start': START, 'ith_end': FINISH })
                file1.close()

        command_sequence = CommandSequence(
            site,
            callback=callback,
            )

        # Start by visiting the page
        command_sequence.get(sleep=5, timeout=60)
        # command_sequence.append_command(LinkCountingCommand())
        command_sequence.append_command(JSInstrumentCommand(), timeout=10)

        # 60 here means the timeout for this specific command "FormAnalyzingCommand" is 60 seconds.
        command_sequence.append_command(FormAnalyzingCommand(), timeout=80)
        # command_sequence.append_command(DatabaseCheckCommand())

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
