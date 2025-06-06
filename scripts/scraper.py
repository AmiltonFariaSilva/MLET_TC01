import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"

def get_rating_value(rating_str):
    rating_map = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
    }
    return rating_map.get(rating_str, 0)

def scrape_books():
    all_books = []

    for page in range(1, 51):  # O site tem 50 páginas
        url = f"{BASE_URL}catalogue/page-{page}.html"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select("article.product_pod")

        for book in books:
            title = book.h3.a["title"]
            relative_url = book.h3.a["href"]
            book_url = urljoin(BASE_URL + "catalogue/", relative_url)

            # Detalhes do livro
            book_response = requests.get(book_url)
            book_soup = BeautifulSoup(book_response.text, "html.parser")

            price = book_soup.select_one("p.price_color").text.replace("£", "")
            rating = get_rating_value(book.select_one("p.star-rating")["class"][1])
            availability = book_soup.select_one("p.instock.availability").text.strip()
            category = book_soup.select("ul.breadcrumb li a")[-1].text.strip()
            image_rel_url = book_soup.select_one("div.item.active img")["src"]
            image_url = urljoin(BASE_URL, image_rel_url.replace("../", ""))

            all_books.append({
                "title": title,
                "price": float(price),
                "rating": rating,
                "availability": availability,
                "category": category,
                "image_url": image_url
            })

        print(f"Página {page} raspada com sucesso")

    return all_books

def save_to_csv(books, output_path="data/books.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(books)
    df.index += 1
    df.index.name = "id"
    df.to_csv(output_path, encoding="utf-8")
    print(f"Dados salvos em {output_path}")

if __name__ == "__main__":
    books = scrape_books()
    save_to_csv(books)
