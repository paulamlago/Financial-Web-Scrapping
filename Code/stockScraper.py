from bs4 import BeautifulSoup
import requests
import sys, getopt #to manage arguments
import pandas as pd
import os
import yfinance as yf

############################################################################################
# Args esperados: 
#       - ticker de la acción (Apple -> AAPL, Tesla -> TSLA, Intel -> INTC)
#       - fecha de inicio
#       - fecha fin (opcional, si no se incluye, se obtienen datos hasta hoy)
############################################################################################

if __name__ == "__main__":
    
    ticker = ''
    from_api = False
    # 1. Comprobamos que se ha pasado el argumento esperado
    try:
        opts, args = getopt.getopt(sys.argv[1:],"t",["ticker=", "api"]) #TODO: añadir fechas

        for argument in opts:
            if argument[0] == '--ticker':
                ticker = argument[1]
            if argument[0] == '--api':
                from_api = True
        if ticker == '':
            print('stockSraper.py --ticker <stock ticker>')
            sys.exit(2)

    except getopt.GetoptError:
        print('stockSraper.py --ticker <stock ticker>')
        sys.exit(2)
    
    #TODO: implementar que se pueda obtener información de web scraping o de la api según una flag que se pase como parámetro, así abarcamos más del enunciado de la práctica
    if not from_api:
        url = 'https://es.finance.yahoo.com/quote/' + ticker + '/history?p=' + ticker #ejemplo de TSLA: https://es.finance.yahoo.com/quote/TSLA/history?p=TSLA
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        all_info = ticker_info.history(preiod='max')
        final_df = pd.DataFrame(all_info)

    final_df.to_csv(os.path.dirname(os.getcwd()) + '\\Dataset\\' + ticker + 'history.csv')