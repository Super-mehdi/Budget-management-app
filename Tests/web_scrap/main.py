from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

#tekhlita dyal beautifulsoup and selenium ;)

# JUMIA – BEAUTIFULSOUP
def scrape_jumia(query):
    url = f"https://www.jumia.ma/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    for item in soup.select('article.prd')[:5]:
        title = item.select_one('h3.name')
        price = item.select_one('div.prc')
        if title and price:
            results.append(f"{title.text.strip()} : {price.text.strip()}")
    return results if results else ["Aucun résultat trouvé."]


# MARJANE – SELENIUM
def scrape_marjane(query):
    url = f"https://www.marjane.ma/"
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(4)
    results = []

    try:
        items = driver.find_elements(By.CLASS_NAME, 'product-item-info')[:5]
        for item in items:
            title = item.find_element(By.CLASS_NAME, 'product-item-name').text
            price = item.find_element(By.CLASS_NAME, 'price').text
            results.append(f"{title} : {price}")
    except:
        results.append("Erreur de chargement ou aucun résultat.")

    driver.quit()
    return results


# CARREFOUR – SELENIUM
def scrape_carrefour(query):
    url = f"https://www.carrefour.ma/"
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(4)
    results = []

    try:
        items = driver.find_elements(By.CLASS_NAME, 'product-item-info')[:5]
        for item in items:
            title = item.find_element(By.CLASS_NAME, 'product-item-name').text
            price = item.find_element(By.CLASS_NAME, 'price').text
            results.append(f"{title} : {price}")
    except:
        results.append("Erreur de chargement ou aucun résultat.")

    driver.quit()
    return results


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']

    jumia_results = scrape_jumia(query)
    marjane_results = scrape_marjane(query)
    carrefour_results = scrape_carrefour(query)

    html = f"<h2>Résultats Jumia :</h2><ul>{''.join(f'<li>{r}</li>' for r in jumia_results)}</ul>"
    html += f"<h2>Résultats Marjane :</h2><ul>{''.join(f'<li>{r}</li>' for r in marjane_results)}</ul>"
    html += f"<h2>Résultats Carrefour :</h2><ul>{''.join(f'<li>{r}</li>' for r in carrefour_results)}</ul>"

    return html


if __name__ == '__main__':
    app.run(debug=True)
