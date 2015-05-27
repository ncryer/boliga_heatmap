# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, re

pattern = re.compile("Næste")
# Startsiden der skal scrapes fra
STARTURL = "http://www.boliga.dk/salg/resultater?so=1&type=Villa&fraPostnr=8000&tilPostnr=8270&sort=omregnings_dato-d&minsaledate=2014-5-26&maxsaledate=today"
# basisurl som bygges videre på ved bladring
BASEURL = "http://www.boliga.dk/salg/resultater" 

def soupify(url):
    # Hent kilden fra en URL og returner et BeautifulSoup objekt
    # objektet har metoder til søgning og udtrækning
    source = requests.get(url)
    return BeautifulSoup(source.text)

def parse_row(row):
    # Fjern \t \r og del rækken op til CSV standard
    data = row.get_text().strip().replace("\t","").replace("\r","").split("\n")
    # Fjern tomme strenge fra listen og returner
    return [item for item in data if item is not ""]
    
def get_content(soup):
    # Find table elementet
    tables = soup.findChildren('table')
    # Tabellen med data er den fjerde tabel i listen
    table = tables[3]
    # Find rækker
    rows = table.findChildren(["tr"])
    # Header kan gemmes; opdel efter \n og fjern tomme strenge
    header = rows.pop(0).get_text().split("\n")
    header = [item for item in header if item is not ""]
    # Gem data til CSV i denne tabel
    CSV = [header]
    # Nu kan rækkerne med data parses
    for row in rows: 
        data = parse_row(row)
        # gem data
        CSV.append(data)
    # Find link til næste side
    next_url = soup.findAll("a", text=pattern)
    if not next_url: 
        # Linket findes ikke, vi er på sidste side
        next_url = False
    else:
        next_url = next_url[0]["href"]
    # Gem data og returner
    return (CSV, next_url)

def build_csv(starturl):
    # Parse alle sider af tabellen
    queue = [starturl]
    CSV = []
    has_header = False
    while len(queue) > 0:
        page = queue.pop()
        content = get_content(soupify(page))
        
        # Tilføj rækker til CSV, tilføj kun headeren en gang
        if has_header is False:
            CSV.append(content[0])
            has_header = True
        else:
            CSV.append(content[0][1:])
        # Tilføj næste side til køen hvis den er der
        nextpage = content[1]
        if nextpage is not False:
            queue.append(BASEURL+nextpage)
        else:
            # Færdig
            print("Finished...")
    return CSV

def write_csv(CSV, filename="boliga_data.csv"):
    # Skriv data til disk
    with open(filename, "w") as f:
        for page in CSV:
            for row in page:
                line = str(row).strip("[").strip("]").replace("'","")
                f.write(line + "\n")
    print("Wrote to file.")

if __name__ == "__main__":
#    test = get_content(soupify(STARTURL))
#    FINISHURL = "http://www.boliga.dk/salg/resultater?so=1&type=Villa&fraPostnr=8000&tilPostnr=8270&sort=omregnings_dato-d&minsaledate=2014-5-26&maxsaledate=today&p=19"
#    test2 = get_content(soupify(FINISHURL))
    all = build_csv(STARTURL)
    write_csv(all)