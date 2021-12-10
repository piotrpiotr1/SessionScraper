import requests
from lxml import html
from bs4 import BeautifulSoup
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import csv
import re

# from multiprocessing import Pool

USERNAME = ""
PASSWORD = ""

df = pd.read_excel('wynik.xls', sheet_name='Wybrane')


# range(od ID,do ID) steruje pętlą
def main():
    for i in df.index:

        LOGIN_URL = "http://www.e"
        URL = df['url'][i]
        print(URL)
        session_requests = requests.session()

        # Login
        result = session_requests.get(LOGIN_URL)
        tree = html.fromstring(result.text)

        # Dane do logowania
        payload = {
            "login": USERNAME,
            "haslo": PASSWORD,

        }

        # logowanie
        result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))

        # pobieranie url
        result = session_requests.get(URL, headers=dict(referer=URL))

        tree = html.fromstring(result.content)

        cena_netto = str(tree.xpath('//span[@class="cena_netto"]/text()'))
        # sprawdzanie czy dany ID jest pusty
        if (len(cena_netto)) == 2:
            pass
        else:
            # pobieranie poszczególnych elementów HTML
            cena_brutto = str(tree.xpath('//span[@class="cena_brutto"]/text()'))
            modul_tytul = str(tree.xpath('//a[@class="modul_tytul"]/text()'))
            symbol = str(tree.xpath('//span[@class="tekst_tab_przedmiot1"]/text()'))
            inne = str(tree.xpath('//span[@class="tekst_tab_przedmiot2"]/text()'))
            res = requests.get(URL)
            soup = BeautifulSoup(res.content, 'lxml')
            nazwa_produktu_temp = str(soup.find('td', attrs={"class": "opis_nazwa_produktu"}))
            cechy = str(soup.find('td', attrs={"class": "wpis_tekst"}))
            foto_temp = str(soup.find('img', attrs={'class': 'example-image'}))

            # czyszczenie
            cena_netto = cena_netto.translate({ord(i): None for i in "'\\[]xaPLN'"})
            cena_netto = cena_netto.replace('.', ',')
            cena_brutto = cena_brutto.translate({ord(i): None for i in "'\\[]xaPLNEURUSD'"})
            cena_brutto = cena_brutto.replace('.', ',')
            modul_tytul = modul_tytul.translate({ord(i): None for i in "'\\[]'"})
            symbol = symbol[33:40]
            ean = inne[68:81]
            dostepnosc = inne[129:133]
            nazwa_prod_temp = re.compile('<.*?>')
            nazwa_produktu = re.sub(nazwa_prod_temp, '', nazwa_produktu_temp)
            foto = str(re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                                  foto_temp))
            photo = foto.translate({ord(i): None for i in "'\\[]'"})

            # zapis do wiersza
            row = [URL, modul_tytul, symbol, nazwa_produktu, cena_netto, cena_brutto, dostepnosc, ean, cechy, photo]

            # zapis do csv

            with open('wynik.csv', 'a', newline='', encoding="utf-8") as csvFile:
                writer = csv.writer(csvFile, delimiter=";")
                writer.writerow(row)

                csvFile.close()


if __name__ == '__main__':
    main()

