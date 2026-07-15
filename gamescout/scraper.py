import logging
import re
from typing import Any, Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)


class Scraper:

    BASE_URL: str = "https://sandbox.oxylabs.io/products"

    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def clean_price(self, raw_price: str) -> float:
        cleaned: str = raw_price.replace("€", "").replace(",", ".").strip()
        return float(cleaned)

    def extract_product_id(self, url: str) -> int:
        match = re.search(r"/products/(\d+)", url)
        if match:
            return int(match.group(1))
        raise ValueError(f"No se pudo extraer el product_id desde la URL: {url}")

    def scrape_pages(self, total_pages: int = 5) -> List[Dict[str, Any]]:
        extracted_data: List[Dict[str, Any]] = []

        try:
            for page in range(1, total_pages + 1):
                page_url: str = f"{self.BASE_URL}?page={page}"
                logging.info(f"Navegando a la página {page}: {page_url}")
                self.driver.get(page_url)

                wait = WebDriverWait(self.driver, 15)
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.product-card, a.product-card, [class*='card']")
                    )
                )

                cards = self.driver.find_elements(
                    By.CSS_SELECTOR, "div.product-card, a.product-card, [class*='card']"
                )

                for card in cards:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "h2, h3, .title, [class*='title']")
                        price_elem = card.find_element(By.CSS_SELECTOR, ".price, [class*='price']")
                        type_elem = card.find_element(By.CSS_SELECTOR, ".category, [class*='category']")

                        raw_url = card.get_attribute("href")
                        if not raw_url:
                            link_elem = card.find_element(By.TAG_NAME, "a")
                            raw_url = link_elem.get_attribute("href") or ""

                        title: str = title_elem.text.strip()
                        product_id: int = self.extract_product_id(raw_url)
                        price_eur: float = self.clean_price(price_elem.text)
                        type_name: str = type_elem.text.strip()

                        extracted_data.append(
                            {
                                "product_id": product_id,
                                "title": title,
                                "price_eur": price_eur,
                                "type_name": type_name,
                            }
                        )
                    except Exception as exc:
                        logging.warning(
                            f"Error al procesar tarjeta de producto: {exc}. Omitiendo tarjeta."
                        )

        finally:
            self.driver.quit()

        return extracted_data