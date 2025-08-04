import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

def scrape_books():
    base_url = 'http://books.toscrape.com/catalogue/page-{}.html'
    base_image_url = 'http://books.toscrape.com/'

    books = []
    page = 1

    while True:
        url = base_url.format(page)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Página {page} não encontrada. Fim da coleta.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.product_pod')
        if not articles:
            print("Nenhum livro encontrado nesta página. Encerrando.")
            break

        print(f"Coletando dados da página {page}...")

        for article in articles:
            title = article.h3.a['title']
            price = article.select_one('.price_color').text
            rating = article.p['class'][1]
            availability = article.select_one('.availability').text.strip()
            category = 'Books'
            image_url = base_image_url + article.img['src'].replace('../', '')

            books.append({
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'category': category,
                'image_url': image_url
            })

        page += 1
        time.sleep(1)  # Pequena pausa para não sobrecarregar o servidor

    df = pd.DataFrame(books)

    # Salvar em /opt/airflow/data
    output_path = Path("/opt/airflow/data/books.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✅ Arquivo salvo com {len(df)} livros em: {output_path}")

if __name__ == "__main__":
    scrape_books()
