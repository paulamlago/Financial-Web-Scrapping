from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
# Generamos opciones para cuando se abra la ventana de chrome
options = Options()
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
# Generamos el driver para interactuar con la página web
exe = os.path.join(os.getcwd(), '\\chromedriver.exe')
driver = webdriver.Chrome(chrome_options=options, executable_path=exe)
# Abrimos la página
driver.get('https://es.finance.yahoo.com')
sleep=driver.implicitly_wait(10)
# Aceptamos las políticas de datos
driver.find_element_by_xpath("//button[@type='submit' and @value='agree']").click()
sleep
# Rellenamos el buscador de cotizaciones con el ticker que interesa mostrar
driver.find_element_by_xpath("//input[@type='text' and @name='s']").send_keys('TSLA', Keys.ENTER)# Añadir ticker como parametro
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
startDate_element.send_keys('01/10/2018')# Añadir fecha como parametro
endDate_element=driver.find_element_by_xpath("//input[@name='endDate']")
endDate_element.clear()
endDate_element.send_keys('01/10/2019')# Añadir fecha como parametro
sleep
# Pulsamos el botón listo
driver.find_element_by_xpath("//button/span[text()='Listo']").click()
sleep
# Aplicamos la búsqueda
driver.find_element_by_xpath("//*[@id='Col1-1-HistoricalDataTable-Proxy']/section/div[1]/div[1]/button").click()
sleep
# html para soap (actual response.text)
url=driver.page_source