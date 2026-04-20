# Leads Extraction Engine

A high-velocity, heuristic-filtered B2B scaling tool. This project uses real-time search engine scraping combined with an AI filter (OpenAI) to extract high-quality, verified B2B leads from the web and auto-exports them directly to a Google Sheet.

![Dashboard Preview](frontend/src/assets/hero.png)

## 🚀 Features

- **Real-Time Web Scraping**: Dynamically queries the web based on your target keyword and precise location.
- **AI-Powered Validation**: Feeds search results through an OpenAI LLM to verify search intent. It aggressively filters out junk results like directories, blogs, news articles, and marketplaces.
- **Automatic Email Extraction**: Automatically visits verified target websites and aggressively regex-parses the source code to sniff out contact emails.
- **Google Sheets Integration**: Automatically appends the extracted leads (Title, URL, Email, Description) cleanly to your integrated Google Sheet.
- **FastAPI SSE Stream**: The scraping engine reports back to the frontend Live Console instantly using Server-Sent Events (SSE).

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, OpenAI API, DuckDuckGo-Search, GSpread, BeautifulSoup4 / URLLib
- **Frontend**: React, Vite, CSS (Dark-Mode Glassmorphism UI)

## ⚙️ Installation & Setup

### 1. Backend Setup (Python)

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

**Environment Variables & Keys:**
- Create a `.env` file in the `backend` folder and add your OpenAI key:
  `OPENAI_API_KEY=your_key_here`
- Place your Google Service Account key inside the `backend` folder and name it `credentials.json`. 
- Ensure your target Google Sheet is shared with the client email found inside your `credentials.json` file!

**Run the Backend Server:**
```bash
uvicorn app:app --reload --port 8000
```

### 2. Frontend Setup (React)

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

## 🧠 How it Works under the Hood
1. **Query Engine**: The React frontend passes a `Query` (e.g. "Car Wash") and `Location` (e.g. "UK") via URL parameters to the FastAPI backend.
2. **DuckDuckGo Stream**: The Python backend generates real-time search strings dynamically (e.g. `Car Wash "UK" -"directory" -"blog"`) and fetches raw Google-like search results.
3. **LLM Verification**: Every search result is pinged to GPT-4o-mini acting as a ruthless B2B validator. The AI decides if the lead precisely matches the intent.
4. **Email Sniffing**: Verified targets have their homepages scanned for contact information.
5. **Auto-Export**: The final packaged lead is streamed back to the frontend table and pushed natively to the specific Google Sheet.
