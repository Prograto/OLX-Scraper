You can run only the python script (Ready_to_run_python_script.py) along withoutUI, It will generate a CSV file

🚗 OLX Smart Scraper (Keyword-Aware Search)

A smart, browser-based OLX web scraper built with Python + Flask + Selenium, designed to fetch only the most relevant ads based on keywords found in the title of each listing.

🎥 Live Video Demo: [Watch on Google Drive](https://drive.google.com/file/d/1r7inY0mVFNabESB3eOx_iEavVrYR5VT2/view?usp=drivesdk)

🌐 Live Project: https://olx-scraper-wuef.onrender.com/

✨ What Makes This Project Different

Unlike traditional scrapers that collect everything on a results page, this scraper thinks — it filters intelligently.

🧩 It only keeps listings whose title contains any of the search words (like “car” or “cover”).

💡 It can be further enhanced with LLMs to understand the meaning of titles, not just literal matches.

Example: Searching for “car cover” skips irrelevant results like “Bike seat cover” or “Fan motor cover”, fetching only relevant items like “Car cover for Swift”.

🧠 How It Works

Enter or use the default OLX search URL

https://www.olx.in/items/q-car-cover?isSearchCall=true


The scraper extracts keywords → ["car", "cover"]

Selenium loads the page and:

Scrolls and clicks “Load More” to reveal all items

Extracts Title, Description, Price, and Link

Keeps only ads whose title contains any keyword

Displays results in an interactive web UI with:

A dynamic table

CSV download option

🧰 Tech Stack
Component	Technology
Backend	Flask (Python)
Web Automation	Selenium + ChromeDriver
Driver Manager	webdriver-manager
Frontend	HTML + CSS + JavaScript (AJAX)
Data Output	JSON + downloadable CSV
Parser	BeautifulSoup (HTML parsing)
🚀 Features

✅ Keyword-filtered scraping — Only titles matching any search word are included.
✅ Smart automation — Automatically clicks “Load More” and scrolls.
✅ Live progress tracking — UI updates as scraping runs.
✅ Background processing — Runs asynchronously via threads.
✅ Instant CSV download — One click to export filtered data.
✅ Headless mode — Chrome runs silently for faster, cleaner scraping.

🪜 Installation & Setup
1️⃣ Clone this repository
git clone https://github.com/<your-username>/olx-smart-scraper.git
cd olx-smart-scraper

2️⃣ Create and activate a virtual environment
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt


Or manually:

pip install flask selenium webdriver-manager beautifulsoup4 requests

4️⃣ Run the app
python app.py

5️⃣ Open your browser
http://127.0.0.1:5000


Use the default OLX URL or paste your own — then click “Scrape”.

📊 Example Output

Input URL:

https://www.olx.in/items/q-car-cover?isSearchCall=true


Extracted keywords:

["car", "cover"]


Filtered Results:

Title	Description	Price	Link
Car body cover for Swift	Brand new, waterproof car cover	₹500	View Ad

All weather cover for Alto	Perfect fit for small hatchbacks	₹450	View Ad

❌ Items like “Bike seat cover” or “Motor cover for fan” are skipped automatically.

📂 Folder Structure
📦 olx-smart-scraper
 ┣ 📂 templates
 ┃ ┗ index.html          → Web UI
 ┣ 📂 static
 ┃ ┣ style.css           → Styling
 ┃ ┗ script.js           → Client-side logic
 ┣ 📂 scraped_data        → Auto-generated CSV files
 ┣ app.py                → Flask + Selenium backend
 ┣ requirements.txt      → Python dependencies
 ┗ README.md             → You’re here ✨

🧠 Developer Notes

You can easily tweak keyword logic inside:

def filter_title_keywords(items, keywords):
    if any(k in title for k in keywords):
        filtered.append(it)


Default behavior: OR condition (any word match)

To enforce AND condition, replace any with all

Currently filters only by title, ignoring descriptions

Runs Chrome headless by default (can be changed in code)

🚧 Future Enhancements

💡 Planned improvements:

Multi-page support (pagination)

Filters by price, city, or date posted

Keyword highlighting in the results table

LLM-based smart matching for related terms (e.g., “automobile cover” → “car cover”)

❤️ Author

👨‍💻 Chandra Sekhar Arasavalli
B.Tech CSE (2022–2026) | AI, ML, IoT & Full Stack Developer

📧 Email

🌐 GitHub – Prograto

💼 LinkedIn – Chandra Sekhar Arasavalli

⭐ If you like this project

Give it a star on GitHub 🌟 — it helps others find it!
