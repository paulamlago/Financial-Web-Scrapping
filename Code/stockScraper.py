from bs4 import BeautifulSoup
import requests
import sys, getopt
import pandas as pd
import os
import datetime
# SELENIUM
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# API
import yfinance as yf

def get_page_selenium(ticker, startDate, endDate):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    # Generamos el driver para interactuar con la página web
    exe = os.path.join(os.getcwd(), 'chromedriver.exe')
    driver = webdriver.Chrome(chrome_options=options, executable_path=exe)
    # Abrimos la página
    driver.get('https://es.finance.yahoo.com')
    sleep=driver.implicitly_wait(10)
    # Aceptamos las políticas de datos
    driver.find_element_by_xpath("//button[@type='submit' and @value='agree']").click()
    sleep
    # Rellenamos el buscador de cotizaciones con el ticker que interesa mostrar
    driver.find_element_by_xpath("//input[@type='text' and @name='s']").send_keys(ticker, Keys.ENTER)# Añadir ticker como parametro
    sleep
    # Seleecionamos los datos históricos
    target = driver.find_element_by_xpath("//ul/li/a/span[text()='Datos históricos']").click()
    sleep
    # Abrimos el drop down de fechas
    driver.find_element_by_xpath("//div[@class='Pos(r) D(ib) Va(m) Mstart(8px)']").click()
    sleep
    # Añadimos fechas de inicio y fin
    startDate_element=driver.find_element_by_xpath("//input[@name='startDate']")
    # Limpiamos el textbox antes de añadir fechas
    startDate_element.clear()
    startDate_element.send_keys(startDate)# Añadir fecha como parametro
    endDate_element=driver.find_element_by_xpath("//input[@name='endDate']")
    endDate_element.clear()
    endDate_element.send_keys(endDate)# Añadir fecha como parametro
    sleep
    # Pulsamos el botón listo
    driver.find_element_by_xpath("//button/span[text()='Listo']").click()
    sleep
    # Aplicamos la búsqueda
    driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[1]/button").click()
    sleep
    # html para soap (actual response.text)
    return driver.page_source

############################################################################################
# Args esperados: 
#       - ticker de la acción (Apple -> AAPL, Tesla -> TSLA, Intel -> INTC)
#       - fecha de inicio
#       - fecha fin (opcional, si no se incluye, se obtienen datos hasta hoy)
#       - Api o web scraping (por defecto web scraping)
############################################################################################

if __name__ == "__main__":
    ticker = ''
    startDate = ''
    endDate = ''
    from_api = False
    # 1. Comprobamos que se ha pasado el argumento esperado
    try:
        opts, args = getopt.getopt(sys.argv[1:],"t:s:e:",["ticker=", "startDate=", "endDate=", "api"])

        for argument in opts:
            if argument[0] in ['--ticker', '-t']: 
                ticker = argument[1]
            elif argument[0] == '--api':
                from_api = True
            elif argument[0] in ['--startDate', '-s']:
                startDate = argument[1]
            elif argument[0] in ["--endDate", '-e']:
                endDate = argument[1]
        if ticker == '': #OBLIGATORIO
            print('stockSraper.py --ticker <stock ticker>')
            sys.exit(2)
        if startDate == '': #cogemos hoy - un año
            today = datetime.datetime.now()
            startDate = str(today.day) + '/' + str(today.month) + '/' + str(today.year - 1)
        if endDate == '': # cogemos hoy
            today = datetime.datetime.now()
            endDate = str(today.day) + '/' + str(today.month) + '/' + str(today.year)
    except getopt.GetoptError:
        print('stockSraper.py --ticker <stock ticker>')
        sys.exit(2)
    
    if not from_api: #WEB SCRAPPING
        #url = 'https://es.finance.yahoo.com/quote/' + ticker + '/history?p=' + ticker #ejemplo de TSLA: https://es.finance.yahoo.com/quote/TSLA/history?p=TSLA
        # Get the url using selenium
        web_page_text = get_page_selenium(ticker, startDate, endDate)
        #response = requests.get(url)
        soup = BeautifulSoup(web_page_text, 'html.parser')
        
        #buscamos la tabla de precios
        prices_table = soup.find_all('table', class_ = "W(100%) M(0)")[0] 
        #extraemos las cabeceras
        headers = prices_table.find('thead').find('tr')
        headers = [columna.text for columna in headers.find_all('th')]
        #La recorremos para extraer los datos mientras los guardamos en un dataFrame
        final_df = pd.DataFrame({head:[] for head in headers})
        cuerpo_tabla = prices_table.find('tbody')
        rows = cuerpo_tabla.find_all('tr')
        for row in rows:
            valores = [valor.text for valor in row.find_all('td')]
            if len(valores) == len(headers): #si no, es otro tipo de información, pero el día saldría duplicado
                #TODO: sería mejor que se guardasen los números como float y no como str
                final_df = final_df.append({h:valores[i] for i, h in enumerate(headers)}, ignore_index=True)
    else: #USANDO YAHOO FINANCE API
        try:
            ticker_info = yf.Ticker(ticker)
        except:
            print('Ese ticker no existe')
        
        startDate = datetime.datetime.strptime(startDate.replace('/', '-'), '%d-%m-%Y').strftime('%Y-%m-%d')
        endDate = datetime.datetime.strptime(endDate.replace('/', '-'), '%d-%m-%Y').strftime('%Y-%m-%d')
        all_info = ticker_info.history(preiod='max', start=startDate, end=endDate)
        final_df = pd.DataFrame(all_info)

    final_df.to_excel(os.path.dirname(os.getcwd()) + '\\Dataset\\' + ticker + 'history.xlsx')