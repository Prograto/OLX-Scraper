import os
import time
import csv
import uuid
import traceback
import threading
from flask import Flask, render_template, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

app = Flask(__name__, template_folder="templates", static_folder="static")
jobs = {}
jobs_lock = threading.Lock()
DEFAULT_URL = "https://www.olx.in/items/q-car-cover?isSearchCall=true"


def selenium_scrape(url, max_load_more=20, headless=False, wait_between_clicks=1.0, short_wait=1.0):
    results = []
    chrome_opts = Options()
    if headless:
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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    wait = WebDriverWait(driver, 12)

    try:
        driver.set_page_load_timeout(45)
        driver.get(url)
        time.sleep(short_wait)

        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-aut-id="itemBox3"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-aut-id="itemBox"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-aut-id="itemsList"]'))
                ),
                message="Timed out waiting for items"
            )
        except Exception:
            pass

        for _ in range(max_load_more):
            try:
                btn = driver.find_element(By.CSS_SELECTOR, '[data-aut-id="btnLoadMore"]')
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.3)
                try:
                    btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", btn)
                time.sleep(wait_between_clicks)
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                break

        for _ in range(5):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(0.5)

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

        cards = soup.find_all("li", attrs={"data-aut-id": "itemBox3"})
        if not cards:
            cards = soup.find_all("li", attrs={"data-aut-id": "itemBox"})
        if not cards:
            anchors = soup.find_all("a", href=True)
            anchors = [a for a in anchors if "/items/" in a["href"] or re.search(r"/o[^/]+/|/p/", a["href"])]
            for a in anchors:
                if a.parent:
                    cards.append(a.parent)

        for c in cards:
            try:
                a_tag = c.find("a", href=True)
                link = a_tag["href"].strip() if a_tag else ""

                price_tag = c.select_one('span[data-aut-id="itemPrice"]') or c.find("span", class_="_2Ks63")
                price = price_tag.get_text(" ", strip=True) if price_tag else ""

                details_tag = c.select_one('span[data-aut-id="itemDetails"]') or c.find("span", class_="YBbhy")
                details = details_tag.get_text(" ", strip=True) if details_tag else ""

                title_tag = c.select_one('span[data-aut-is="itemTitle"]') or c.find("span", class_="_2poNJ")
                title = title_tag.get_text(" ", strip=True) if title_tag else (a_tag.get_text(" ", strip=True) if a_tag else "")

                if title or price or link:
                    results.append({"title": title, "description": details, "price": price, "link": link})
            except Exception:
                continue

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return results


def worker(jobid, url, headless=False):
    with jobs_lock:
        jobs[jobid]["status"] = "running"
    try:
        results = selenium_scrape(url, headless=headless)
        os.makedirs("scraped_data", exist_ok=True)
        csv_path = os.path.join("scraped_data", f"{jobid}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Description", "Price", "Link"])
            for r in results:
                writer.writerow([r.get("title", ""), r.get("description", ""), r.get("price", ""), r.get("link", "")])
        with jobs_lock:
            jobs[jobid]["status"] = "finished"
            jobs[jobid]["results"] = results
            jobs[jobid]["error"] = None
            jobs[jobid]["csv_path"] = csv_path
    except Exception as e:
        tb = traceback.format_exc()
        with jobs_lock:
            jobs[jobid]["status"] = "error"
            jobs[jobid]["results"] = []
            jobs[jobid]["error"] = f"{str(e)}\n{tb}"
            jobs[jobid]["csv_path"] = None


@app.route("/")
def index():
    return render_template("index.html", default_url=DEFAULT_URL)


@app.route("/start_scrape", methods=["POST"])
def start_scrape():
    data = request.get_json() or {}
    url = data.get("url") or DEFAULT_URL
    headless = data.get("headless", False)
    jobid = str(uuid.uuid4())
    with jobs_lock:
        jobs[jobid] = {"status": "queued", "results": [], "error": None, "csv_path": None, "created_at": time.time()}
    t = threading.Thread(target=worker, args=(jobid, url, headless), daemon=True)
    t.start()
    return jsonify({"message": "Scrape started", "jobid": jobid, "status": "queued"}), 202


@app.route("/status/<jobid>")
def status(jobid):
    with jobs_lock:
        job = jobs.get(jobid)
        if not job:
            return jsonify({"error": "Unknown job id"}), 404
        return jsonify({
            "jobid": jobid,
            "status": job["status"],
            "items_found": len(job["results"]),
            "error": job["error"]
        })


@app.route("/results/<jobid>")
def results(jobid):
    with jobs_lock:
        job = jobs.get(jobid)
        if not job:
            return jsonify({"error": "Unknown job id"}), 404
        return jsonify({
            "jobid": jobid,
            "status": job["status"],
            "results": job["results"],
            "error": job["error"]
        })


@app.route("/download/<jobid>")
def download(jobid):
    with jobs_lock:
        job = jobs.get(jobid)
        if not job:
            return "Unknown job id", 404
        if job["status"] != "finished" or not job.get("csv_path"):
            return "Job not ready or CSV missing", 400
        path = job["csv_path"]
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


if __name__ == "__main__":
    os.makedirs("scraped_data", exist_ok=True)
    app.run(debug=True, host="127.0.0.1", port=5000)
