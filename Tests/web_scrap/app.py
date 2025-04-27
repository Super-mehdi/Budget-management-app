from flask import Flask, request, render_template_string
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
except ImportError:
    webdriver = None  # Placeholder in case selenium is not installed

# CODE DYAL SELENIUM 7it ma khdemch liya beautifulsoup
app = Flask(__name__)
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)


def scrape_with_selenium(url, item_selector, title_class, price_class):
    if not webdriver:
        return ["Selenium non disponible dans cet environnement."]

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # laisser le temps au site de charger

    results = []
    try:
        items = driver.find_elements(By.CLASS_NAME, item_selector)[:5]
        for item in items:
            try:
                title = item.find_element(By.CLASS_NAME, title_class).text
                price = item.find_element(By.CLASS_NAME, price_class).text
                results.append(f"{title} : {price}")
            except:
                continue
    except:
        results.append("Erreur de chargement ou site modifié.")

    driver.quit()
    return results if results else ["Aucun résultat trouvé."]


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        query = request.form['query']

        # Scraper Jumia
        jumia_url = f"https://www.jumia.ma/"
        results['Jumia'] = scrape_with_selenium(jumia_url, 'info', 'name', 'prc')

        # Scraper Marjane
        marjane_url = f"https://www.marjane.ma/"
        results['Marjane'] = scrape_with_selenium(marjane_url, 'product-item-info', 'product-item-name', 'price')

        # Scraper Carrefour
        carrefour_url = f"https://www.carrefour.ma/"
        results['Carrefour'] = scrape_with_selenium(carrefour_url, 'product-item-info', 'product-item-name', 'price')

    return render_template_string('''
        <h2>Comparateur de prix (Méthode Selenium)</h2>
        <form method="post">
            <input type="text" name="query" placeholder="Nom du produit" required>
            <button type="submit">Rechercher</button>
        </form>
        {% if results %}
            {% for site, items in results.items() %}
                <h3>{{ site }}</h3>
                <ul>{% for item in items %}<li>{{ item }}</li>{% endfor %}</ul>
            {% endfor %}
        {% endif %}
    ''', results=results)

