""" This file aims to demonstrate how to write custom commands in OpenWPM

Steps to have a custom command run as part of a CommandSequence

1. Create a class that derives from BaseCommand
2. Implement the execute method
3. Append it to the CommandSequence
4. Execute the CommandSequence

"""
import logging
import time
import sqlite3
import json
import string
import random
import exrex
import requests
from form import Form

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

import yaml
# SLEEP_TIME = 0

class LinkCountingCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "LinkCountingCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        current_url = webdriver.current_url
        link_count = len(webdriver.find_elements(By.TAG_NAME, "a"))
        self.logger.info("There are %d links on %s", link_count, current_url)

class JSInstrumentCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "JSInstrumentCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        current_url = webdriver.current_url
        webdriver.execute_script(''' 
            window.postMessage({
                            direction: "from-page-script",
                            message: "clear_triggered_func_data",
                        }, "*");

            let stringSet = new Set();

            sessionStorage.setItem('instrument', 'false');

            function logFunc(regex, string, funcName) {
                if (typeof string != 'string' || typeof regex != 'string' || typeof funcName != 'string') {
                    return;
                }

                if (stringSet.has(string)) {
                    return;
                } else {
                    stringSet.add(string);
                }

                if (sessionStorage.getItem('instrument') == 'false') {
                    return;
                }
                
                let update = {
                    regex,
                    used_string: string,
                    page_url: window.location.href,
                    domain: window.location.host,
                    triggered_func: funcName,
                    timestamp: new Date().toString(),
                };

                //let options = {
                //    method: 'POST',
                //    headers: {
                //        'Content-Type': 'application/json',
                //    },
                //    body: JSON.stringify(update),
                //};

                //window.console.log(`oh no! It is ${update.triggered_func} with ${update.used_string} and ${update.regex}`)
                //if (update.used_string == "localhost" || update.used_string == "localhost:3050" || update.used_string == "http://localhost:3050/triggered_func") {
                //    window.console.log('useless request. Cancel it');
                //    return;
                //}
                    
                window.postMessage({
                            direction: "from-page-script",
                            message: "triggered_func",
                            data: update,
                        }, "*");

                //fetch('http://localhost:3050/triggered_func', options)
                //.then(data => console.log);
            };

            let SURF_temp0 = RegExp.prototype.test; 
            window.RegExp.prototype.test = function (text) { 
                logFunc(this.source, text, 'RegExp.prototype.test');
                return SURF_temp0.apply(this, arguments); 
            };

            let SURF_temp1 = RegExp.prototype.exec;
            window.RegExp.prototype.exec = function (text) { 
                logFunc(this.source, text, 'RegExp.prototype.exec');
                return SURF_temp1.apply(this, arguments); 
            };

            let SURF_temp2 = String.prototype.match;
            window.String.prototype.match = function (text) { 
                logFunc(text.source, this, 'String.prototype.match');
                return SURF_temp2.apply(this, arguments); 
            };

            let SURF_temp3 = String.prototype.matchAll;
            window.String.prototype.matchAll = function (text) { 
                logFunc(text.source, this, 'String.prototype.matchAll');
                return SURF_temp3.apply(this, arguments); 
            };

            let SURF_temp4 = String.prototype.search;
            window.String.prototype.search = function (text) { 
                logFunc(text.source, this, 'String.prototype.search');
                return SURF_temp4.apply(this, arguments); 
            };

            let SURF_temp5 = Element.prototype.setAttribute;
            window.Element.prototype.setAttribute = function (name, value) { 
                if (name === 'pattern') {
                    logFunc(value, '', 'Element.prototype.setAttribute');
                }
                return SURF_temp5.apply(this, arguments); 
            };

            ''')   
        time.sleep(1) 
    

class FormAnalyzingCommand(BaseCommand):

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")
        self.webdriver = None

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "FormAnalyzingCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        self.webdriver = webdriver
        # forms = webdriver.find_elements(By.TAG_NAME, "div")
        # try:
        #     element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.TAG_NAME, "form"))
        #     )
        # except:
        #     pass
        # finally:
        #     pass

        forms = webdriver.find_elements(By.TAG_NAME, "form")

        current_url = webdriver.current_url
        self.logger.info("There are %d forms on %s", len(forms), current_url)
        r = requests.post('http://localhost:3050/form_num_count', json={ "page_url": current_url, "num_form": len(forms)})

        for index, form in enumerate(forms):
            form = Form(current_url, form, webdriver, index)
            try:
                form.analyze()
                form.submit()
            except StaleElementReferenceException:
                pass


        # For each form, build an open_api_dict. Examine the input tags within, then click the submit button
        # for form in forms:
        #     open_api_dict = {
        #         'openapi': '3.0.0',
        #         'info': {
        #             'title': 'The number 1 form in this url',
        #             'version': '1.0.0'
        #         },
        #         'servers': [
        #             {'url': 'http://localhost:3000'} 
        #         ],
        #         'paths': {
        #             '/': {
        #                 'post': {
        #                     'summary': 'a form post request generated from OpenWPM',
        #                     'requestBody': {
        #                         'required': True,
        #                         'content': {
        #                             'application/x-www-form-urlencoded': {
        #                                 'schema': {
        #                                     'type': 'object',
        #                                     'properties': {
        #                                         'name': {
        #                                             'type': 'string'
        #                                         },
        #                                         'pass': {
        #                                             'type': 'string'
        #                                         }
        #                                     },
        #                                     'required': [
        #                                         'name', 'pass'
        #                                     ]
        #                                 }
        #                             }
        #                         }
        #                     }                            
        #                 }
        #             }
        #         }
        #     }

        #     inputs = form.find_elements(By.TAG_NAME, 'input')
        #     for input in inputs:
        #         self.logger.info(f"The name of the input is {input.get_attribute('name')}")
        #         input.send_keys("some text")
        #         # if input.get_attribute('pattern') is not None:

        #     with open(r'store_file.yaml', 'w') as file:
        #         documents = yaml.dump(open_api_dict, file)
            

class DatabaseCheckCommand(BaseCommand):

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "DatabaseCheckCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        conn = sqlite3.connect('./datadir/crawl-data.sqlite')

        c = conn.cursor()

        c.execute("SELECT post_body FROM http_requests WHERE id = 3166;")

        rows = c.fetchall()
        for row in rows:
            for key in row:
                obj = json.loads(key)
                print(obj['FirstName'])


        c.close()

        time.sleep(5) 

        
