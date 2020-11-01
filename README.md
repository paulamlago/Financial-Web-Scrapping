# Financial-Web-Scrapping
Repositorio creado para la Práctica 1 de la asignatura Tipología y Ciclo de Vida de los Datos del Máster de Ciencia de Datos de la UOC.

Este repositorio contiene cinco directiorios: 

 - Dataset: Se encuentra el dataset generado por el script
 - Code: El script generado para extraer el dataset
 - Robot: El fichero robot.txt de la página donde se va a realizar web scrapping
 - Document: Fichero PDF que contiene las respuestas de la PRAC1.
 - References: Referencias utilizadas para la eralización de la práctica
 
# Requerimientos
Para ejecutar el script, se deben instalar previamente los siguientes paquetes de python:
- BeautifulSoup
- pandas
- selenium
- yfinance

# Ejecución

Sin determinar el marco temporal (Se establece automáticamente un año atrás desde el momento de la ejecución):
``` 
>>> python stockScraper.py
```

Escogiendo la fecha de inicio y finalización de los datos:
``` 
>>> python stockScraper.py --startDate <fecha en formato dd/mm/yy> --endDate <fecha en formato dd/mm/yy>
```
