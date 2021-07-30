from flask import Flask
from flask import request
from flask import jsonify
import json

import requests
import bs4
import os
import mysql.connector
import datetime
import random
import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

# # local testing
db_host = "localhost"
db_user = "root"
db_password = ""
db_name = "econsig_db"
server_host = "localhost"
server_port = 5005

# server testing
# db_host = "209.126.98.140"
# db_user = "pedro"
# db_password = "pedro123"
# db_name = "econsig_db"
# server_host = "209.126.98.140"
# server_port = 5005

app = Flask(__name__)

scraping_running = False

#check if an element with certain id exists
def check_exists_by_id(browser, elmId):
    try:
        browser.find_element_by_id(elmId)
    except NoSuchElementException:
        return False
    return True
#check if a certain element exists by css selector
def check_exists_by_css(browser, cssSelector):
    try:
        browser.find_element_by_css_selector(cssSelector)
    except NoSuchElementException:
        return False
    return True

def passCaptcha(browser, api_key):
    captcha_result = 'ERROR_CAPTCHA_UNSOLVABLE'
    captcha_img_old = None
    while captcha_result == 'ERROR_CAPTCHA_UNSOLVABLE':
        while check_exists_by_css(browser, 'div.captcha img[name="captcha_img"]')==False:
            sleep(1)
        captcha_img = browser.find_element_by_css_selector("div.captcha img[name='captcha_img']")
        captcha_img_base64 = captcha_img.screenshot_as_base64
        while captcha_img_base64 == captcha_img_old:
            while check_exists_by_css(browser, 'div.captcha img[name="captcha_img"]')==False:
                sleep(1)
            captcha_img = browser.find_element_by_css_selector("div.captcha img[name='captcha_img']")
            captcha_img_base64 = captcha_img.screenshot_as_base64
        captcha_img_old = captcha_img_base64
        captcha_response = requests.post("https://2captcha.com/in.php", data={'key': api_key, 'method': 'base64', 'regsense': 1, 'body': captcha_img_base64}).text
        while captcha_response.split('|')[0] != "OK":
            captcha_response = requests.post("https://2captcha.com/in.php", data={'key': api_key, 'method': 'base64', 'regsense': 1, 'body': captcha_img_base64}).text
        captcha_id = captcha_response.split('|')[1]
        captcha_result = requests.get("https://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text
        while captcha_result.split('|')[0] != "OK":
            captcha_result = requests.get("https://2captcha.com/res.php?key={}&action=get&id={}".format(api_key, captcha_id)).text
            if captcha_result == 'ERROR_CAPTCHA_UNSOLVABLE':
                btn_captcha_reload = browser.find_elements_by_css("div.captcha>a")[0]
                btn_captcha_reload.click()
                break;
    captcha_result = captcha_result.split('|')[1]
    return captcha_result

@app.route("/econsig", methods=['GET'])
def econsig():
    content = request.args
    if not 'cpf' in content or not 'matricula' in content:
        return "<h2>Missing parameters.</h2>"
    cpf_str = content['cpf']
    matricula_str = content['matricula']
    global scraping_running
    if scraping_running == True:
        return "<h2>Another instance of scraping is already running.</h2>"
    scraping_running = True
    browser = None
    try:
        username = "ES.ROGERIO"
        password = "Hd2939i24"

        api_key = "7e1bb28330b5d01bbd3399f19cb3c3dd"
        
        page_url = "https://www.econsig.com.br/es/v3/autenticarUsuario#no-back"

        # open mysql connection
        mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        database=db_name
        )
        mycursor = mydb.cursor()

        # linux server
        chrome_options = Options()
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        #browser.maximize_window()

        # Here i get path of current workind directory
        print ("Opening headless chrome")
        current_path = os.getcwd()
        # Chromedriver is just like a chrome. you can dowload latest by it website
        driver_path = os.path.join(os.getcwd(), 'chromedriver')
        browser = webdriver.Chrome(driver_path, options=chrome_options)
        # browser = webdriver.Chrome(driver_path)

        #open page
        print ("Loading page.")
        browser.get(page_url)
        login_success = False
        while login_success == False:
            #username and password input
            while check_exists_by_id(browser, 'username')==False:
                pass
            username_input = browser.find_element_by_id('username')
            username_input.clear()
            username_input.send_keys(username)

            # Form submit
            while check_exists_by_css(browser, 'form')==False:
                pass
            user_form = browser.find_element_by_css_selector('form')
            user_form.submit()

            while check_exists_by_css(browser, 'input[name="senha"]')==False:
                pass
            password_input = browser.find_element_by_css_selector('input[name="senha"]')
            password_input.clear()
            password_input.send_keys(password)

            print ("connecting 2captcha for login captcha")
            # solve captcha
            if check_exists_by_id(browser, 'captcha'):
                captcha_code = passCaptcha(browser, api_key)
                while check_exists_by_id(browser, 'captcha')==False:
                    sleep(0.1)
                captcha_input = browser.find_element_by_id("captcha")
                captcha_input.clear()
                captcha_input.send_keys(captcha_code)
                # btn_captcha_ok = browser.find_element_by_id("btnOK")
                # btn_captcha_ok.click()

            # Form submit
            while check_exists_by_css(browser, 'form')==False:
                pass
            passwd_form = browser.find_element_by_css_selector('form')
            passwd_form.submit()
            sleep(1)
            while check_exists_by_css(browser, 'body') == False:
                pass
            body_class = browser.find_element_by_css_selector('body').get_attribute('class')
            if "page-login" in body_class:
                login_success = False
            else:
                login_success = True
        print ("login success")
        # press search button
        while check_exists_by_css(browser, '#containerFavoritos a.btn')==False:
            pass
        searchButton = browser.find_element_by_css_selector('#containerFavoritos a.btn')
        searchButton.click() 

        info_error = True
        while info_error == True:
            # input for matricula and cpf
            while check_exists_by_id(browser, 'RSE_MATRICULA')==False:
                pass
            matricula_input = browser.find_element_by_id('RSE_MATRICULA')
            matricula_input.clear()
            matricula_input.send_keys(matricula_str)

            while check_exists_by_id(browser, 'SER_CPF')==False:
                pass
            cpf_input = browser.find_element_by_id('SER_CPF')
            cpf_input.clear()
            cpf_input.send_keys(cpf_str)
            
            print ("2captcha for cpf search")
            # check if requires captcha
            if check_exists_by_id(browser, 'captcha'):
                captcha_code = passCaptcha(browser, api_key)
                while check_exists_by_id(browser, 'captcha')==False:
                    sleep(0.1)
                captcha_input = browser.find_element_by_id("captcha")
                captcha_input.clear()
                captcha_input.send_keys(captcha_code)

            # Form submit
            while check_exists_by_css(browser, 'form')==False:
                pass
            passwd_form = browser.find_element_by_css_selector('form')
            passwd_form.submit()

            # data list
            info_error = False
            while check_exists_by_css(browser, 'dl.data-list')==False:
                while check_exists_by_css(browser, 'div.main>div.main-content>div.alert')==False:
                    pass
                error_msg = browser.find_element_by_css_selector('div.main>div.main-content>div.alert').text.strip()
                if error_msg == "O código informado é inválido.":
                    info_error = True
                    break
                pass
            if info_error == False:
                break
        
        print ("extracting data.")
        page_soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
        print ("Extracting data")

        dt_list = page_soup.select("dl.data-list dt")
        dd_list = page_soup.select("dl.data-list dd")
        estabelecimento1 = ""
        estabelecimento2 = ""
        servidor = ""
        cpf = ""
        data_admissao_categoria = ""
        margem_facultativa = ""

        data_count = len(dt_list)
        if data_count > 5:
            estabelecimento1 = dd_list[0].get_text().strip()
            estabelecimento2 = dd_list[1].get_text().strip()
            servidor = dd_list[2].get_text().strip()
            cpf = dd_list[3].get_text().strip()
            data_admissao_categoria = dd_list[4].get_text().strip()
            margem_facultativa = dd_list[5].get_text().strip()
            
            # database
            sql = (
                "INSERT INTO `consulta` (`cpf`,`Matrícula`,`Estabelecimento1`,`Estabelecimento2`,`Servidor`,`Data de admissão - Categoria`,`Margem Facultativa`)" \
                "VALUES" \
                "(%s,%s,%s,%s,%s,%s,%s);"
            )
            
            val = [cpf, matricula_str, estabelecimento1, estabelecimento2, servidor, data_admissao_categoria, margem_facultativa]
            mycursor.execute(sql, val)
            mydb.commit()

        print ("Extracted data")

        browser.close()
        print ('finished')
        scraping_running = False
        if data_count == 0:
            return "<h2>No data for CPF <span style='color: red;'>{}</span>.</h2>".format(cpf_str)
        else:
            return "<h2>Scraping for CPF <span style='color: red;'>{}</span> completed successfully.</h2>".format(cpf_str)
    except Exception as ex:
        print(ex)
        if browser is not None:
            browser.close()
        scraping_running = False
        return "<h2>Scraping for CPF <span style='color: red;'>{}</span> failed unexpectedly.</h2>".format(cpf_str)
    

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(server_host, port=server_port)
