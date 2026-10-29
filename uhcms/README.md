# UHCMS – University Helpdesk & Complaint Management System
Students report campus problems (projector, Wi-Fi, hostel…), staff update the status, students track progress.
Tech: Python 3, Flask, SQLite, HTML/CSS. No Docker, all free.

## Run on your computer
1. Install Python 3.10+ from python.org (tick "Add to PATH").
2. In a terminal inside this folder:
```
python -m venv .venv
.venv\Scripts\activate        (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python app.py
```
3. Open http://127.0.0.1:5000
Demo staff login: staff@uni.edu / staff123. Students register themselves.

## Run the tests
`python -m pytest -q`

## 2-minute demo
Register → log in → New complaint (Projector not working / Classroom Equipment) → see CMP-001 → log out → log in as staff → set In Progress → log in as student → updated status shows.

## Folders
app.py (all logic) · schema.sql (database) · templates/ (pages) · static/style.css · tests/ · docs/DESIGN.md (diagrams, SRS, traceability) · .github/workflows/ci.yml (auto tests)

## GitHub
```
git init
git add .
git commit -m "feat: initial UHCMS MVP"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```
The CI workflow runs your tests on every push.

## Deploy (free)
Netlify and Vercel host static sites, so they do not suit a Flask app with a database. Use Render.com (free): New > Web Service > connect your GitHub repo > Build command `pip install -r requirements.txt gunicorn` > Start command `gunicorn "app:create_app()"` > add env var SECRET_KEY (long random text). On the free tier SQLite data resets on redeploy, fine for a demo.

## Project team
Muhammad Zubair (71773, IT Department, 2nd Semester), Zaheer Ahmed (71168), Naik Bakht (70863), Jasim Ali (69724), Abdul Ghafoor (70963).

Pages: Home `/`, About `/about`, Login, Sign up, Dashboard, New complaint, Complaint details.
