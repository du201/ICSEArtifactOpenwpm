import requests
from regex_faker import solve_regex
from z3 import *
import requests
import string
import random
import logging
import time
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
SLEEP_TIME = 0

class Form:
    logger = logging.getLogger("openwpm")
    def __init__(self, current_url, form, webdriver, ith_form):
        self.current_url = current_url
        self.ith_form = ith_form
        self.form = form
        self.inputs = []
        self.selects = []
        self.textareas = []
        self.webdriver = webdriver

    def analyze(self):
        inputs = self.form.find_elements(By.TAG_NAME, 'input')
        self.logger.info("There are %d inputs on %s", len(inputs), self.current_url)
        for input in inputs:
            input = Input(input, self.webdriver)
            self.inputs.append(input)
            input.analyze()
            time.sleep(SLEEP_TIME) 
        self.collectPatternAttributes()

        selects = self.form.find_elements(By.TAG_NAME, 'select')
        self.logger.info("There are %d selects on %s", len(selects), self.current_url)
        for select in selects:
            select = Select(select)
            self.selects.append(select)
            select.analyze()
            time.sleep(SLEEP_TIME) 

        textareas = self.form.find_elements(By.TAG_NAME, 'textarea')
        self.logger.info("There are %d textareas on %s", len(textareas), self.current_url)
        for textarea in textareas:
            textarea = Textarea(textarea, self.webdriver)
            self.textareas.append(textarea)
            textarea.analyze()
            time.sleep(SLEEP_TIME)

    def collectPatternAttributes(self):
        patterns = []
        for input in self.inputs:
            if input.hasPattern():
                patterns.append(
                    { 'pattern': input.getPattern(), 
                    'has_input_text': input.has_input_text, 
                    'used_string': input.used_string,
                    'name': input.getName()})

        r = requests.post('http://localhost:3050/pattern_attribute', json={ "page_url": self.current_url, "pattern_input": patterns, "ith_form": self.ith_form})
        
    def submit(self):
        used_string = self.generateUsedString()
        r = requests.post('http://localhost:3050/used_string', json={ "page_url": self.current_url, "used_string": used_string, "ith_form": self.ith_form})
        self.webdriver.execute_script(''' 
            window.postMessage({
                direction: "from-page-script",
                message: "send_used_string",
                data: arguments[0],
                ith_form: arguments[1]
            }, "*");
            ''', used_string, self.ith_form) 
        r = requests.post('http://localhost:3050/on_submit', json= { "openAPI": self.generateOpenAPI(), 'page_url': self.current_url, 'is_successful_submit': False, "ith_form": self.ith_form })

        time.sleep(1) 
        self.clickSubmitButton()
        time.sleep(1) 

        self.webdriver.execute_script(''' 
            window.postMessage({
                direction: "from-page-script",
                message: "send_triggered_func_data"
            }, "*");
            ''')  

        time.sleep(1)  
        pass

    def generateUsedString(self):
        used_string = []
        for input in self.inputs:
            if input.has_input_text:
                used_string.append(input.used_string)

        return used_string

    def generateOpenAPI(self):
        openapi_dict = {}
        if self.form.get_attribute('action') != '' and self.form.get_attribute('method') != '':
            openapi_dict['action'] = self.form.get_attribute('action')
            openapi_dict['method'] = self.form.get_attribute('method')
            openapi_dict['inputs'] = []
            for input in self.inputs:
                if input.hasName():
                    if input.has_input_text:
                        openapi_dict['inputs'].append({'name': input.getName(), 'value': input.used_string})
                    elif input.hasValue():
                        openapi_dict['inputs'].append({'name': input.getName(), 'value': input.getValue()})
                    elif input.hasPlaceholder():
                        openapi_dict['inputs'].append({'name': input.getName(), 'value': input.getPlaceholder()})

            openapi_dict['selects'] = []
            for select in self.selects:
                if select.hasName():
                    options = select.options
                    optionValues = []
                    for option in options:
                        value = option.get_attribute('value')
                        if value != '':
                            optionValues.append(value)

                    openapi_dict['selects'].append({'name': select.getName(), 'values': optionValues})

            openapi_dict['textareas'] = []
            for textarea in self.textareas:
                if textarea.hasName():
                    openapi_dict['textareas'].append(
                        {'name': textarea.getName(), 
                        'placeholder': textarea.getPlaceholder(),
                        'maxlength': textarea.getMaxLength(),
                        'minlength': textarea.getMinLength()})

            return json.dumps(openapi_dict)

        return "Not Doable"
        pass

    def clickSubmitButton(self):
        buttons = self.form.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            if button.get_attribute('type') == 'submit' or button.get_attribute('class') == 'btn-submit':
                try:
                    self.preClickAction()
                    button.click()
                except:
                    self.logger.info("One button unclickable")
                    pass
                finally:
                    self.postClickAction()
                return

        inputs = self.form.find_elements(By.TAG_NAME, 'input')
        for input in inputs:
            if input.get_attribute('type') == 'submit':
                try:
                    self.preClickAction()
                    input.click()
                except:
                    self.logger.info("One button unclickable")
                    pass  
                finally:
                    self.postClickAction()
                return

    def preClickAction(self):
        self.webdriver.execute_script(''' 
            window.postMessage({
                direction: "from-page-script",
                message: "about-to-button-click"
            }, "*");
            sessionStorage.setItem('instrument', 'true');
            ''')  
        time.sleep(1) 
        
    def postClickAction(self):
        time.sleep(1)
        self.webdriver.execute_script(''' 
            window.postMessage({
                direction: "from-page-script",
                message: "finish-button-click"
            }, "*");
            sessionStorage.setItem('instrument', 'false');
            ''')   
        time.sleep(1) 

class Input:
    logger = logging.getLogger("openwpm")
    def __init__(self, input, webdriver):
        self.input = input 
        self.has_input_text = False
        self.used_string = ''
        self.webdriver = webdriver
    
    def analyze(self):
        input_type = self.input.get_attribute('type')
        if input_type == 'date':
            self.analyzeInputTime('2021-01-01')  
        # elif input.get_attribute('type') == 'datetime-local': # firefox does not support this type -> degrade to text
        elif input_type == 'email':
            self.analyzeInputText('du304@gmail.com')
        # elif input.get_attribute('type') == 'month':
        elif input_type == 'number':
            self.analyzeInputNumber()
        elif input_type == 'password':
            self.analyzeInputText('WuIse0114!')
        elif input_type == 'radio':  
            if self.input.get_attribute('required'):
                self.input.click()
        elif input_type == 'search':
            self.analyzeInputText('What day is today?')
        elif input_type == 'tel':
            self.analyzeInputText('9586754300')
        elif input_type == 'time':
            self.analyzeInputTime('14:00')  
        elif input_type == 'url':
            self.analyzeInputText('https://example.com')
        # elif input.get_attribute('type') == 'week':
        elif input_type == 'text': # this includes no type, datetime-local, month, week
            self.analyzeInputText('')
        pass

    def analyzeInputTime(self, default_val) -> None:
        dateString = default_val
        if self.input.get_attribute('value') != '':
            dateString = self.input.get_attribute('value')
        elif self.input.get_attribute('max') != '':
            dateString = self.input.get_attribute('max')
        elif self.input.get_attribute('min') != '':
            dateString = self.input.get_attribute('min')
        self.sendKeys(dateString)

    def analyzeInputText(self, default_val) -> None:
        letters = string.ascii_letters
        inputString = ''

        if self.hasMinLength():
            length = int(self.input.get_attribute('minlength'))
            inputString = ''.join(random.choice(letters) for i in range(length))
        elif self.hasMaxLength():
            length = int(self.input.get_attribute('maxlength'))
            inputString = ''.join(random.choice(letters) for i in range(length))
        elif default_val != '':
            inputString = default_val
        else:
            length = 10
            inputString = ''.join(random.choice(letters) for i in range(length))

        if self.hasPlaceholder():
            inputString = self.input.get_attribute('placeholder')
        elif self.hasValue():
            inputString = self.input.get_attribute('value')
            self.has_input_text = True
            self.used_string = inputString
            return

        elif self.hasPattern():
            #inputString = exrex.getone(input.get_attribute('pattern'))
            try:
                inputString = solve_regex(
                    self.input.get_attribute('pattern'),
                    minLength=self.input.get_attribute('minlength') if self.hasMinLength() else 1,
                    maxLength=self.input.get_attribute('maxlength') if self.hasMaxLength() else 200)
            except:
                self.logger.info("regex solving failed")
                inputString = "test string"

        self.sendKeys(inputString)

    def analyzeInputNumber(self):
        inputNumber = '10' # default value
        if self.hasValue():
            inputString = self.input.get_attribute('value')
            self.has_input_text = True
            self.used_string = inputString
            return
            # self.sendKeys(inputNumber)
            # inputNumber = '' # if value attribute is present, it has already been inputed. So we input nothing
            # self.has_input_text = True
            # self.used_string = self.input.get_attribute('value')
        elif self.input.get_attribute('max') != '':
            inputNumber = self.input.get_attribute('max')
        elif self.input.get_attribute('min') != '':
            inputNumber = self.input.get_attribute('min')
        self.sendKeys(inputNumber)

    def clear(self, orig):
        try:
            self.input.clear()
            self.logger.info(f'cleared in {orig}')
        except:
            self.logger.info("one input is not clearable")

    def sendKeys(self, inputString):
        self.webdriver.execute_script(''' 
            sessionStorage.setItem('instrument', 'true');
        ''')

        time.sleep(0.5) 
        try:
            self.input.send_keys(inputString)
            # if self.has_input_text == False: # if self.has_input_text == True here, it means that it is some special cases
            self.has_input_text = True
            self.used_string = inputString
            self.logger.info(f'typed in {inputString}')
        except:
            self.logger.info("one input is not interactable")
            pass

        time.sleep(1) 

        self.webdriver.execute_script(''' 
            sessionStorage.setItem('instrument', 'false');
        ''')

    def getName(self):
        return self.input.get_attribute('name')

    def getValue(self):
        return self.input.get_attribute('value')

    def getPlaceholder(self):
        return self.input.get_attribute('placeholder')

    def hasName(self):
        attr = self.input.get_attribute('name')
        return attr != '' and attr != None

    def hasValue(self):
        attr = self.input.get_attribute('value')
        return attr != '' and attr != None

    def hasMaxLength(self):
        attr = self.input.get_attribute('maxlength')
        return attr != '' and attr != None

    def hasMinLength(self):
        attr = self.input.get_attribute('minlength')
        return attr != '' and attr != None

    def hasPlaceholder(self):
        attr = self.input.get_attribute('placeholder')
        return attr != '' and attr != None

    def hasPattern(self):
        attr = self.input.get_attribute('pattern')
        return attr != '' and attr != None

    def getPattern(self):
        return self.input.get_attribute('pattern')

class Select:
    logger = logging.getLogger("openwpm")
    def __init__(self, select):
        self.select = select 
        self.options = []

    def analyze(self):
        self.options = self.select.find_elements(By.TAG_NAME, 'option')
        for option in self.options:
            if option.get_attribute('value') != '':
                try:
                    option.click()
                except:
                    self.logger.info("One select options unclickable")
                    pass
                break
    
    def hasName(self):
        attr = self.select.get_attribute('name')
        return attr != '' and attr != None

    def getName(self):
        return self.select.get_attribute('name')

class Textarea:
    logger = logging.getLogger("openwpm")
    def __init__(self, textarea, webdriver):
        self.textarea = textarea
        self.webdriver = webdriver 

    def analyze(self):
        input = Input(self.textarea, self.webdriver)
        input.analyzeInputText('')

    def hasName(self):
        attr = self.textarea.get_attribute('name')
        return attr != '' and attr != None

    def hasPlaceholder(self):
        attr = self.textarea.get_attribute('placeholder')
        return attr != '' and attr != None

    def hasMaxLength(self):
        attr = self.textarea.get_attribute('maxlength')
        return attr != '' and attr != None

    def hasMinLength(self):
        attr = self.textarea.get_attribute('minlength')
        return attr != '' and attr != None

    def getName(self):
        return self.textarea.get_attribute('name')

    def getPlaceholder(self):
        return self.textarea.get_attribute('placeholder')

    def getMaxLength(self):
        return self.textarea.get_attribute('maxlength')

    def getMinLength(self):
        return self.textarea.get_attribute('minlength')