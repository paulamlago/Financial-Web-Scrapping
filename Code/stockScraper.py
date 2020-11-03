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

import time

# Función para hacer scroll down sobre la página web
def scroll(driver):
    # Creamos una iteración para hacer un total de 4 scrolls
    for i in range(1,4):
        # Ejecutamos el script que permite realizar un scroll
        driver.execute_script("window.scrollTo(1,50000)")
        time.sleep(5)

def get_page_selenium(url, startDate, endDate):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument('log-level=3') # Mostrar solo información importante
    options.add_argument("--headless") #Para no mostrar las ventanas del navegador
    # Generamos el driver para interactuar con la página web
    exe = os.path.join(os.getcwd(), 'chromedriver.exe')
    driver = webdriver.Chrome(chrome_options=options, executable_path=exe)
    # Abrimos la página
    driver.get(url)
    sleep=driver.implicitly_wait(10)
    # Aceptamos las políticas de datos
    driver.find_element_by_xpath("//button[@type='submit' and @value='agree']").click()
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
    # llamamos a la función scroll para recoger todos los datos de la tabla haciendo scroll down
    scroll(driver)
    # html para soap
    return driver.page_source

############################################################################################
# Args esperados: 
#       - ticker de la acción (Apple -> AAPL, Tesla -> TSLA, Intel -> INTC)
#       - fecha de inicio
#       - fecha fin (opcional, si no se incluye, se obtienen datos hasta hoy)
#       - Api o web scraping (por defecto web scraping)
############################################################################################

if __name__ == "__main__":
    excelwriter = pd.ExcelWriter(os.path.dirname(os.getcwd()) + '\\Dataset\\AccionesSectorAutomovil.xlsx')
    startDate = ''
    endDate = ''
    # 1. Comprobamos que se ha pasado el argumento esperado
    try:
        #opts, args = getopt.getopt(sys.argv[1:],"t:s:e:",["ticker=", "startDate=", "endDate=", "api"])
        opts, args = getopt.getopt(sys.argv[1:],"s:e:",["startDate=", "endDate="])
        for argument in opts:
            if argument[0] in ['--startDate', '-s']:
                startDate = argument[1]
            elif argument[0] in ["--endDate", '-e']:
                endDate = argument[1]
            """elif argument[0] in ['--ticker', '-t']: 
                ticker = argument[1]
            elif argument[0] == '--api':
                from_api = True"""
        
        """if ticker == '': #OBLIGATORIO
            print('stockSraper.py --ticker <stock ticker>')
            sys.exit(2)"""
        if startDate == '': #cogemos hoy - un año
            today = datetime.datetime.now()
            startDate = str(today.day) + '/' + str(today.month) + '/' + str(today.year - 1)
        if endDate == '': # cogemos hoy
            today = datetime.datetime.now()
            endDate = str(today.day) + '/' + str(today.month) + '/' + str(today.year)
    except getopt.GetoptError:
        print('stockSraper.py --ticker <stock ticker>')
        sys.exit(2)
        
    # Diccionario de meses
    dict_dates={
        "ene.":"01",
        "feb.":"02",
        "mar.":"03",
        "abr.":"04",
        "may.":"05",
        "jun.":"06",
        "jul.":"07",
        "ago.":"08",
        "sept.":"09",
        "oct.":"10",
        "nov.":"11",
        "dic.":"12"
    }
    list_tickers = ['TSLA', 'PAH3.DE', 'NIO', 'RACE'] # Tickers de Tesla, Porsche, Nio, Ferrari
    df_all = pd.DataFrame()
    for ticker in list_tickers:
        url = 'https://es.finance.yahoo.com/quote/' + ticker + '/history?p=' + ticker #ejemplo de TSLA: https://es.finance.yahoo.com/quote/TSLA/history?p=TSLA
        # Get the url using selenium
        web_page_text = get_page_selenium(url, startDate, endDate)
        #response = requests.get(url)
        soup = BeautifulSoup(web_page_text, 'html.parser')
        
        #buscamos la tabla de precios
        prices_table = soup.find_all('table', class_ = "W(100%) M(0)")[0] 
        #extraemos las cabeceras
        headers = prices_table.find('thead').find('tr')
        headers = [columna.text for columna in headers.find_all('th')]
        #La recorremos para extraer los datos mientras los guardamos en un dataFrame
        ticker_df = pd.DataFrame({head:[] for head in headers})
        cuerpo_tabla = prices_table.find('tbody')
        rows = cuerpo_tabla.find_all('tr')
        for row in rows:
            valores = [valor.text for valor in row.find_all('td')]
            if len(valores) == len(headers): #si no, es otro tipo de información, pero el día saldría duplicado
                #TODO: sería mejor que se guardasen los números como float y no como str
                row_columns = {}
                for i, h in enumerate(headers):
                    # Para los valores de fechas cambiamos el formato de dd month. yyyy a dd/MM/yyyy
                    if i==0:
                        full_date=valores[i].split(" ")
                        day=str(full_date[0])
                        month=str(dict_dates.get((full_date[1])))
                        year=str(full_date[2])
                        full_date=str(day+"/"+month+"/"+year)
                        valor=full_date
                # Para el volumen lo convertimos a un entero y reemplazamos los valores - por 0
                    elif i==6:
                        valores[i]=valores[i].replace('-','0')
                        valor=int(valores[i].replace('.',''))
                # Para el resto de valores, los convertimos a float
                    else:      
                        valores[i]=valores[i].replace('-','0')
                        valor=float(valores[i].replace(',','.'))
                    row_columns[h] = valor
                ticker_df = ticker_df.append(row_columns, ignore_index=True)
        #ticker_df['Ticker'] = [ticker] * ticker_df.shape[0]
        #USANDO YAHOO FINANCE API
        try:
            ticker_info = yf.Ticker(ticker)
        except:
            print('Ese ticker no existe')
        
        """if '/' in startDate:
            startDate = datetime.datetime.strptime(startDate.replace('/', '-'), '%d-%m-%Y').strftime('%Y-%m-%d')
            endDate = datetime.datetime.strptime(endDate.replace('/', '-'), '%d-%m-%Y').strftime('%Y-%m-%d')
        api_info = ticker_info.history(preiod='max', start=startDate, end=endDate)[['Dividends', 'Stock Splits']]
        print(str(ticker_df.shape[0]))
        ticker_df = pd.concat([ticker_df, api_info], axis=1)"""
        #df_all = pd.concat([df_all, ticker_df], axis=0)
        ticker_df.to_excel(excelwriter, sheet_name = ticker)
    excelwriter.save()
