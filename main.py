from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import pandas
from Reader import Reader
from selenium.common.exceptions import TimeoutException
import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

def getdata():
    rd = Reader()
    rd.openExplorer()
    data = pandas.read_csv(filepath_or_buffer=rd.path, sep  = ";")
    return data.iloc[:, 0]

def split_text(input_string):
    # Definiere die Trennzeichen (Semikolon, Schrägstrich, Leerzeichen)
    delimiters = r'[;/¬†¬†\s]+'

    # Verwende re.split, um den String bei den definierten Trennzeichen zu splitten
    elements = re.split(delimiters, input_string)

    # Entferne leere Strings aus der Liste (falls vorhanden)
    elements = [element for element in elements if element]

    # Gib die Elemente zurück
    return elements

def get_last_element_after_split(input_string):
    # Definiere die Trennzeichen
    delimiters = [';', '/', '¬†¬†', ' ']

    # Überprüfen, ob eines der Trennzeichen im String enthalten ist
    if any(delimiter in input_string for delimiter in delimiters):
        # Splitte den String und gib das letzte Element zurück
        elements = split_text(input_string)
        return elements[-1] if elements else "Kein gültiges Element gefunden"
    else:
        # Gib eine Nachricht zurück, wenn kein Trennzeichen enthalten ist
        return input_string

def popups(driver):
    try:
        WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i'))).click()
    except Exception:
        pass

def tableAvailable(driver):
    try:
        WebDriverWait(driver, 0.5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'historyTab')))
        # print("Tabelle vorhanden")
        return True
    except Exception:
        print("Keine Tabelle vorhanden bei: " + str(driver.current_url))
        return False

daten = getdata()
# options = uc.ChromeOptions

# driver = uc.Chrome(service = ChromeDriverManager().install())
driver = webdriver.Chrome()

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

def load_page_with_timeout(url, timeout, retries):
    attempt = 0
    while attempt < retries:
        try:
            # print(f"Versuch {attempt + 1}, lade Seite: {url}")
            # Setze die maximale Ladezeit für die Seite
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            # Wenn die Seite erfolgreich geladen wird, beenden wir die Schleife
            return
        except TimeoutException:
            # print(f"Seite hat nach {timeout} Sekunden nicht geladen. Versuch {attempt + 1} von {retries}.")
            attempt += 1
            if attempt < retries:
                # print("Seite neu laden...")
                driver.refresh()
                time.sleep(1)  # Warte ein wenig bevor du es erneut versuchst
            else:
                # print("Seite konnte nicht geladen werden. Alle Versuche fehlgeschlagen.")
                raise

final_data = []

for link in daten:
    # driver.get(link)
    try:
        load_page_with_timeout(link, 6, 2)
    except Exception:
        continue
    popups(driver)
    if tableAvailable(driver):
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find("tbody")
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            data = [get_last_element_after_split(td.get_text(strip=True)) for td in tds]
            data.append(link)
            final_data.append(data)
        # print("Tabelle vorhanden")
    else:
        continue

columns = ['Geschichte', 'Periodenende', 'EPS', 'Prognose', 'Umsatz', 'Prognose', 'Link']

df = pandas.DataFrame(final_data, columns=columns)

df2 = pandas.DataFrame(final_data)

filename = "quartalszahlen_" + datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y_%H%M") + ".csv"

filename2 = "quartalszahlen_" + datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y_%H%M") + "_" + str(2) + ".csv"

try:
    df.to_csv('/Users/justinwild/Downloads/' + filename, sep = ";", index = False, encoding = 'utf-8')
   # df.to_csv('//Master/F/User/Microsoft Excel/Privat/Börse/Investing/' + filename, sep = ";", index = False, encoding = 'utf-8')

except Exception:
    print("Spalten passen nicht, daher ohne Bezeichnung ausgeworfen!")
    df2.to_csv('/Users/justinwild/Downloads/' + filename2, sep = ";", index = False, encoding = 'utf-8')
    # df2.to_csv('//Master/F/User/Microsoft Excel/Privat/Börse/Investing/' + filename2, sep=";", index=False, encoding='utf-8')