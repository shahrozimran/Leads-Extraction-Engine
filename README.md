# 🚀 Leads Extraction Engine

A high-velocity, heuristic-filtered B2B scaling tool. This project uses real-time search engine scraping combined with an AI filter (OpenAI) to extract high-quality, verified B2B leads from the web and auto-exports them directly to a Google Sheet.

<p align="center">
  <img src="frontend/src/assets/hero.png" alt="Leads Extraction Engine Interface" width="85%">
</p>

## ✨ Features

- **Real-Time Web Scraping**: Dynamically queries the web based on your target keyword and precise location (e.g., "Car Wash" in "United Kingdom").
- **AI-Powered Validation**: Feeds search results through an OpenAI LLM (GPT-4) to verify search intent. It aggressively filters out junk results like directories, blogs, news articles, and marketplaces, ensuring you only get direct B2B contacts.
- **Automatic Email Extraction**: Automatically visits verified target websites and leverages Regex to aggressively parse the source code to sniff out contact emails, skipping "no-reply" traps.
- **Google Sheets Integration**: Automatically appends the extracted leads (Title, URL, Email, Description) cleanly into your specified Google Sheet in real-time.
- **FastAPI SSE Stream**: The scraping engine reports back to the frontend Live Console instantly using Server-Sent Events (SSE).

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, OpenAI API, DuckDuckGo-Search, GSpread, BeautifulSoup4 / URLLib
- **Frontend**: React, Vite, Vanilla CSS (Dark-Mode Glassmorphism UI)

---

## ⚙️ Step-by-Step Installation & Setup

This guide assumes you have Python (3.9+) and Node.js installed on your machine.

### 🔑 Step 1: Prepare Your Credentials

Before running the application, you need to set up two critical credentials inside the `backend/` folder:

#### 1. OpenAI API Key
1. Go to your [OpenAI Developer Platform](https://platform.openai.com/api-keys).
2. Generate a new secret key.
3. In your project, go into the `backend/` folder and create a new file named exactly `.env`.
4. Open the `.env` file and paste your key strictly in this format:
   ```env
   OPENAI_API_KEY=sk-your-very-long-secret-key-here
   ```

#### 2. Google Sheets Service Account (`credentials.json`)
This allows the app to automatically write data into your Google Sheets without needing manual login.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project and enable the **Google Sheets API** and **Google Drive API**.
3. Go to **Credentials** -> **Create Credentials** -> **Service Account**.
4. Once created, go to the "Keys" tab for that service account, and click **Add Key** -> **Create New Key** -> **JSON**.
5. A `.json` file will automatically download to your computer.
6. Rename this file to exactly `credentials.json` and move it into the `backend/` folder of this project.
7. **CRITICAL STEP**: Open `credentials.json` and look for the field `client_email` (it will look something like `your-bot@your-project.iam.gserviceaccount.com`). You **must** copy this email, open your destination Google Sheet in your web browser, and share the Sheet with this email as an **Editor**.

### 💻 Step 2: Run the Backend

Open a new terminal window at the root of the project to start the Python API.

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
*The backend should now be listening quietly on `http://localhost:8000`.*

### 🎨 Step 3: Run the Frontend

Leave the backend terminal running. Open a **second, new terminal window** at the root of the project to start the React interface.

```bash
cd frontend
npm install
npm run dev
```
*The terminal will provide a local link (usually `http://localhost:5173`). Ctrl+Click it to open the app in your browser!*

---

## 🧠 How the Pipeline Works

1. **Query Input**: You enter a keyword (e.g., "Plumbers") and location (e.g., "Texas, US") in the React interface.
2. **Search & Crawl**: The Python backend generates a targeted search query and dynamically crawls DuckDuckGo for live results.
3. **LLM Verification**: Every single website title and snippet found is silently passed to OpenAI. The AI judges whether the website is actually a B2B business matching your intent.
4. **Email Sniffing**: If the AI approves the lead, the scraper instantly visits the actual website and crawls its underlying code for hidden emails.
5. **Live Export**: The complete data package (Name, URL, Email, Summary) is streamed directly to your screen and instantly synced to your Google Sheet!
