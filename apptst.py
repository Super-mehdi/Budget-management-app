from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# HADA CODE BeautifulSOUUUUUUP
def scrape_jumia(query):
    url = f'https://www.jumia.ma/catalog/?q={query}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.select('article.prd')[:5]
    results = []
    for item in items:
        title = item.select_one('h3.name')
        price = item.select_one('div.prc')
        if title and price:
            results.append(f"{title.text.strip()} : {price.text.strip()}")
    return results


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].replace(' ', '+')

    jumia = scrape_jumia(query)

    # Construction HTML
    html = "<h2>Résultats Jumia :</h2><ul>"
    for r in jumia:
        html += f"<li>{r}</li>"
    html += "</ul>"
    return html


if __name__ == '__main__':
    app.run(debug=True)
