from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime


class Login:
    @staticmethod
    def show():
        import PySimpleGUI as sg

        sg.theme('default1')
        layout = [[sg.T('Usuário: ', pad=((10, 0), (0, 0))), sg.In(key='-USER-', size=(15, 1), pad=((0, 10), (0, 0)))],
                  [sg.T('Senha:   ', pad=((10, 0), (0, 0))), sg.In(key='-PASSWORD-', password_char='*', size=(15, 1),
                                                                   pad=((0, 10), (0, 0)))],
                  [sg.OK()]]
        window = sg.Window('LogIn', layout, finalize=True)
        event, values = window.read()

        import sys
        if event == sg.WINDOW_CLOSED:
            sys.exit()

        _user = values['-USER-']
        _password = values['-PASSWORD-']

        window.close()
        return _user, _password


class SatScraper:
    def __init__(self, _user: str, _password: str):
        self.user = _user
        self.password = _password
        options = webdriver.ChromeOptions()
        options.add_argument('lang=pt-br')
        s = Service('chromedriver.exe')
        self.driver = webdriver.Chrome(service=s)
        self.driver.implicitly_wait(10)

    def run(self):
        self.driver.get('https://sat.sef.sc.gov.br/tax.net/Sat.Efd.Web/Cruzamento/EfdDeclaracoes.aspx')
        time.sleep(5)

        user_input_xpath = '//*[@id="Body_pnlMain_tbxUsername"]'
        password_input_xpath = '//*[@id="Body_pnlMain_tbxUserPassword"]'
        user_input = self.driver.find_element(By.XPATH, user_input_xpath)
        user_input.send_keys(self.user)

        password_input = self.driver.find_element(By.XPATH, password_input_xpath)
        password_input.send_keys(self.password)

        enter_button_xpath = '//*[@id="Body_pnlMain_btnLogin"]'
        enter_button = self.driver.find_element(By.XPATH, enter_button_xpath)
        enter_button.click()
        time.sleep(5)

        with open('cnpjs.txt', 'r') as fin, open('resultado.txt', 'w') as fout:
            for cnpj in fin.readlines():
                if cnpj.split():
                    print(self.get_values(cnpj.split()), file=fout)

    def get_values(self, cnpj):
        text = ''
        try:
            cnpj_arrow_xpath = '//*[@id="s2id_Body_Main_sepBusca_ctbInformante_hid_single_ctbInformante_value"]/a/' \
                               'span[2]/b'
            cnpj_arrow = self.driver.find_element(By.XPATH, cnpj_arrow_xpath)
            cnpj_arrow.click()
        except:
            self.driver.execute_script('$0.click()')
        time.sleep(3)

        cnpj_input_xpath = '//*[@id="select2-drop"]/div/input'
        cnpj_input = self.driver.find_element(By.XPATH, cnpj_input_xpath)
        cnpj_input.send_keys(cnpj)
        time.sleep(5)
        cnpj_input.send_keys(Keys.ENTER)

        start_date_xpath = '//*[@id="Body_Main_sepBusca_mopPeriodoInicio"]'
        start_date_input = self.driver.find_element(By.XPATH, start_date_xpath)
        start_date_input.send_keys('01/2021')

        end_date_xpath = '//*[@id="Body_Main_sepBusca_mopPeriodoFim"]'
        end_date_input = self.driver.find_element(By.XPATH, end_date_xpath)
        end_date_input.send_keys('12/2021')

        search_button_xpath = '//*[@id="Body_Main_sepBusca_btnBuscar"]'
        search_button = self.driver.find_element(By.XPATH, search_button_xpath)
        search_button.click()
        time.sleep(5)

        company_data_xpath = '//*[@id="s2id_Body_Main_sepBusca_ctbInformante_hid_single_' \
                             'ctbInformante_value"]/a/span[1]'
        company_data = self.driver.find_element(By.XPATH, company_data_xpath)
        company_data = company_data.text
        text += f'\n{company_data}:\n'

        columns = ('ICMS a Recolher', 'Saldo Credor', 'Entradas', 'Saídas')
        last_month = datetime.now().month if datetime.now().month > 1 else 13
        for i in range(1, last_month):
            try:
                for j in range(4, 8):
                    element_xpath = f'//*[@id="Body_Main_grpEfd_gridView"]/tbody/tr[{i}]/td[{j}]'
                    values = self.driver.find_element(By.XPATH, element_xpath)
                    values = values.text.splitlines()
                    values = [float(value.replace('.', '').replace(',', '.')) for value in values]
                    if abs(values[0] - values[1]) > 1:
                        text += f'\t{columns[j - 4]} ({i}/{datetime.now().year}): {values[0]}, {values[1]}\n'
            except:
                text += f'ERRO AO EXTRAIR VALORES\n'
                break

        return text


if __name__ == '__main__':
    user, password = Login().show()
    if user and password:
        SatScraper(user, password).run()
