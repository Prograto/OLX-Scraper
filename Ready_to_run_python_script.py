"""
Simple, user-friendly OLX scraper using Selenium.
Scrapes title, price, description, and link from OLX search results.
"""

import time
import csv
import os
import sys
import argparse
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Command-line setup ---
parser = argparse.ArgumentParser(description="Friendly OLX Selenium scraper")
parser.add_argument("--url", "-u", help="OLX search URL (e.g. https://www.olx.in/items/q-car-cover?isSearchCall=true)")
parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
parser.add_argument("--wait", type=float, default=1.0, help="Seconds to wait between actions")
args = parser.parse_args()

# Ask for URL if not passed via CLI
url = args.url or input("Enter OLX search URL: ").strip()
if not url:
    print("No URL provided. Exiting.")
    sys.exit(1)

# --- Chrome setup ---
chrome_opts = Options()
if args.headless:
    # Headless Chrome mode (no visible window)
    try:
        chrome_opts.add_argument("--headless=new")
    except Exception:
        chrome_opts.add_argument("--headless")
chrome_opts.add_argument("--no-sandbox")
chrome_opts.add_argument("--disable-dev-shm-usage")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_opts.add_experimental_option("useAutomationExtension", False)

# Initialize browser driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_opts)
wait = WebDriverWait(driver, 12)


# --- Helper functions ---
def safe_text(element):
    """Get clean text safely from an element"""
    try:
        return element.text.strip()
    except Exception:
        return ""


def click_load_more():
    """Keep clicking 'Load more' until it disappears"""
    clicks = 0
    while True:
        try:
            btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="btnLoadMore"]')))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.3)
            try:
                btn.click()
            except Exception:
                # fallback JS click
                driver.execute_script("arguments[0].click();", btn)
            clicks += 1
            print(f"Load more clicked ({clicks})")
            time.sleep(args.wait)
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            break
    print(f"Done clicking Load more. Total clicks: {clicks}")


def ensure_items_present():
    """Wait until the product list is visible"""
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-aut-id="itemsList"], li[data-aut-id="itemBox3"], li[data-aut-id="itemBox"]')))
        return True
    except TimeoutException:
        return False


def extract_items():
    """Pull item data (title, price, description, link)"""
    found = []
    elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-aut-id="itemBox3"], li[data-aut-id="itemBox"]')
    print(f"Found {len(elements)} item elements")
    for el in elements:
        try:
            # Try to extract link
            link = ""
            try:
                a = el.find_element(By.XPATH, ".//a[@href]")
                link = a.get_attribute("href") or ""
            except Exception:
                pass

            # Get price
            price = ""
            try:
                price_el = el.find_element(By.CSS_SELECTOR, 'span[data-aut-id="itemPrice"], span._2Ks63')
                price = safe_text(price_el)
            except Exception:
                pass

            # Get details / short description
            details = ""
            try:
                details_el = el.find_element(By.CSS_SELECTOR, 'span[data-aut-id="itemDetails"], span.YBbhy')
                details = safe_text(details_el)
            except Exception:
                try:
                    details_el = el.find_element(By.CSS_SELECTOR, 'div[data-aut-id="itemDetails"]')
                    details = safe_text(details_el)
                except Exception:
                    pass

            # Get title
            title = ""
            try:
                title_el = el.find_element(By.CSS_SELECTOR, 'span[data-aut-is="itemTitle"], span._2poNJ, div[data-aut-id="itemTitle"], div._2poNJ')
                title = title_el.get_attribute("title") or safe_text(title_el)
            except Exception:
                try:
                    a = el.find_element(By.XPATH, ".//a[@href]")
                    title = safe_text(a)
                except Exception:
                    pass

            # Keep only non-empty results
            if title or price or link:
                found.append({"title": title, "description": details, "price": price, "link": link})

        except StaleElementReferenceException:
            continue
        except Exception as e:
            print("Skipping an item due to error:", e)
            continue

    return found


# --- Main scraper flow ---
try:
    print("Opening page...")
    driver.get(url)
    time.sleep(1.0)
    click_load_more()

    # Make sure items exist before scraping
    if not ensure_items_present():
        print("No items found on the page. Exiting.")
        driver.quit()
        sys.exit(1)

    items = extract_items()
    print(f"Scraped {len(items)} items.")

    # Save results
    os.makedirs("scraped_data", exist_ok=True)
    try:
        qpart = url.split("/")[-1] or "olx_results"
        filename_base = qpart.replace("?", "_").replace("&", "_")
    except Exception:
        filename_base = "olx_results"

    out_csv = os.path.join("scraped_data", f"{filename_base}.csv")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Price", "Link"])
        for it in items:
            writer.writerow([it.get("title", ""), it.get("description", ""), it.get("price", ""), it.get("link", "")])

    print(f"✅ Saved {len(items)} results to {out_csv}")

except Exception:
    print("❌ Unexpected error occurred:")
    traceback.print_exc()

finally:
    try:
        driver.quit()
        print("Browser closed.")
    except Exception:
        pass
