🚗 OLX Smart Scraper (Keyword-Aware Search)

A smart, browser-based OLX web scraper built with Python + Flask + Selenium, designed to fetch only the most relevant ads based on keywords found in the title of each listing.
🎉 Live working project link: https://olx-scraper-wuef.onrender.com/
✨ What Makes This Project Different

Unlike traditional scrapers that collect everything from a results page, this scraper intelligently filters items — it only keeps listings whose title contains any of the search words (like “car” or “cover”).

So if you search for car cover, it skips irrelevant listings and fetches only those that actually have “car” or “cover” in the title.

🧠 How It Works

You enter or use a default OLX search URL — e.g.

https://www.olx.in/items/q-car-cover?isSearchCall=true


The scraper extracts the keywords (→ ["car", "cover"]) from the URL.

Using Selenium, it loads the OLX results page and automatically:

Scrolls and clicks “Load More” until all results are visible.

Extracts each item’s Title, Description, Price, and Link.

Filters only those items where any keyword appears in the title.

Displays the results beautifully in a web UI (with a table and CSV download option).

🧰 Tech Stack
Component	Technology
Backend	Flask (Python)
Web Automation	Selenium + ChromeDriver
Driver Manager	webdriver-manager
Frontend	HTML + CSS + JavaScript (AJAX)
Data Output	JSON + downloadable CSV
Parser	BeautifulSoup (for final HTML parsing)
🚀 Features

✅ Keyword-filtered scraping — Only includes listings with search words in the title.
✅ Smart automation — Automatically scrolls and clicks "Load More".
✅ Live progress tracking — UI shows scrape progress in real-time.
✅ Background processing — Scraping runs asynchronously in threads.
✅ Instant download — Export all filtered data to CSV with one click.
✅ Headless mode — Runs Chrome invisibly for faster, quieter scraping.

🪜 Installation & Setup
1️⃣ Clone this repository
git clone https://github.com/<your-username>/olx-smart-scraper.git
cd olx-smart-scraper

2️⃣ Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

3️⃣ Install dependencies
pip install -r requirements.txt


Or manually:

pip install flask selenium webdriver-manager beautifulsoup4 requests

4️⃣ Run the app
python app.py

5️⃣ Open in browser
http://127.0.0.1:5000


You’ll see a search box and a “Scrape” button.
Enter an OLX search URL or use the default one.

📊 Example

Input URL:

https://www.olx.in/items/q-car-cover?isSearchCall=true


Extracted keywords:

["car", "cover"]


Result:

Title	Description	Price	Link
Car body cover for Swift	Brand new, waterproof car cover...	₹500	View Ad

All weather cover for Alto	Perfect fit for small hatchbacks...	₹450	View Ad

⛔ Listings like “Bike seat cover” or “Motor cover for fan” are ignored because their titles don’t contain the keyword “car”.

🧩 Folder Structure
📂 olx-smart-scraper
 ┣ 📂 templates
 ┃ ┗ index.html          → Web UI
 ┣ 📂 static
 ┃ ┣ style.css           → Styling
 ┃ ┗ script.js           → Client-side JS logic
 ┣ 📂 scraped_data        → Auto-generated CSV files
 ┣ app.py                → Flask + Selenium backend
 ┣ requirements.txt      → Python dependencies
 ┗ README.md             → You’re here :)

🧠 Developer Notes

You can modify the keyword logic easily in:

def filter_title_keywords(items, keywords):
    if any(k in title for k in keywords):
        filtered.append(it)


Currently, it matches any keyword (logical OR).
If you want to require all words (logical AND), replace any with all.

The scraper uses a headless Chrome instance by default; you can toggle this in code or via UI.

🧩 Future Enhancements

🚧 Add support for:

Pagination across multiple OLX pages

Filtering by price range or location

Multi-keyword AND/OR toggles in the UI

Built-in keyword highlighting in results

❤️ Author

Chandra Sekhar Arasavalli
📧 Email
 | 🌐 GitHub: Prograto
