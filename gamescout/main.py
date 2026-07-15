from typing import List

from gamescout.database import create_db_and_tables
from gamescout.models import Product
from gamescout.repository import ProductRepository
from gamescout.scraper import Scraper


def main() -> None:
    create_db_and_tables()

    scraper = Scraper()
    scraped_data = scraper.scrape_pages(total_pages=5)

    repository = ProductRepository()
    repository.upsert_products(scraped_data)

    print("Consulta 1: Top 5 Productos Más Caros")

    top_products: List[Product] = repository.get_top_n(5)
    for p in top_products:
        type_name = p.type.name if p.type else "Sin tipo"
        print(f"• [{type_name}] {p.title} - {p.price_eur:.2f} € (ID: {p.product_id})")

    print("")

    if top_products and top_products[0].type:
        sample_type = top_products[0].type.name
        print(f"Consulta 2: Productos pertenecientes a '{sample_type}'")
        print("")
        by_type: List[Product] = repository.get_products_by_type(sample_type)
        for p in by_type:
            print(f"• {p.title} - {p.price_eur:.2f} €")
    print("")


if __name__ == "__main__":
    main()
