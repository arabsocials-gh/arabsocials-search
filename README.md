# ArabSocials Member Search

A full-stack member search app — **FastAPI backend on Render** + **static frontend on GitHub Pages**.

---

## Project Structure

```
arabsocials-search/
├── backend/
│   ├── main.py          ← FastAPI app
│   ├── requirements.txt
│   └── users.xlsx       ← Your data file (add this manually)
├── frontend/
│   └── index.html       ← Single-page search UI
├── .github/
│   └── workflows/
│       └── deploy.yml   ← Auto-deploys frontend to GitHub Pages
├── render.yaml          ← Render deployment config
└── README.md
```

---

## Step 1 — Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `arabsocials-search` (or anything you like)
3. Set it to **Public** (required for free GitHub Pages)
4. Click **Create repository**

---

## Step 2 — Push the code

```bash
cd arabsocials-search
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/arabsocials-search.git
git push -u origin main
```

> ⚠️ **Important:** The `backend/users.xlsx` file contains real user data.
> Make sure you are comfortable committing it to a public repo, or set the repo to **Private** and use a [Render environment variable](#option-loading-data-from-env) instead.

---

## Step 3 — Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. Save. The workflow will auto-run on every push to `main`.
4. Your site will be live at: `https://YOUR_USERNAME.github.io/arabsocials-search/`

---

## Step 4 — Deploy backend to Render

### 4a. Create a free Render account
Go to [render.com](https://render.com) and sign up (free tier is enough).

### 4b. Connect your GitHub repo
1. Click **New → Web Service**
2. Connect your GitHub account and select `arabsocials-search`
3. Render will auto-detect `render.yaml` — click **Apply**

### 4c. Manual setup (if render.yaml is not picked up)
| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

4. Click **Deploy**. Wait ~2 minutes for the first deploy.
5. Copy your service URL — it looks like: `https://arabsocials-search-api.onrender.com`

---

## Step 5 — Connect frontend to backend

1. Open your live site: `https://YOUR_USERNAME.github.io/arabsocials-search/`
2. Click **Change** next to the API URL in the filter panel
3. Paste your Render URL (e.g. `https://arabsocials-search-api.onrender.com`)
4. The filters will load automatically

Alternatively, hardcode it by editing `frontend/index.html`:
```js
const DEFAULT_API = 'https://arabsocials-search-api.onrender.com';
```

---

## API Endpoints

### `GET /options`
Returns all filter options (countries, languages, etc.)

### `GET /search`
Returns paginated search results.

| Parameter | Type | Description |
|---|---|---|
| `country` | string | Exact match |
| `state` | string | Exact match |
| `city` | string | Exact match |
| `nationality` | string | Exact match |
| `gender` | string | Exact match |
| `marital_status` | string | Exact match |
| `education` | string | Exact match |
| `religion` | string | Exact match |
| `profession` | string | Exact match |
| `language` | string | Comma-separated, match ANY |
| `interest` | string | Comma-separated, match ANY |
| `age_min` | int | Minimum age |
| `age_max` | int | Maximum age |
| `about_keyword` | string | Free-text search in About Me |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 20, max: 100) |

---

## Updating the data

To use a new Excel file:
1. Replace `backend/users.xlsx` with the new file
2. Commit and push — Render will automatically redeploy

---

## Render free tier notes

- **Spins down after 15 min of inactivity** — first request after sleep takes ~30 seconds
- Upgrade to a paid plan ($7/mo) to keep it always-on
- Alternatively use [UptimeRobot](https://uptimerobot.com) to ping the API every 5 minutes for free
