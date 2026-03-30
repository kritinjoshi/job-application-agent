# 🛡️ Executive Job Pipeline Agent (L6-L8 TPM)

An autonomous, multi-agent pipeline designed to discover, rank, and tailor applications for elite Technical Program Management roles (Staff, Principal, Director). This system bypasses standard feed noise using targeted "Sniper" searches and ensures 100% uptime through resilient LLM fallback logic.

---

## 🚀 Core Features

### 🎯 1. Sniper Search Discovery
Bypasses LinkedIn's default 7-day recency bias. The "Sniper" engine performs targeted, company-specific deep-dives (e.g., Roblox, OpenAI, NVIDIA) with a flexible 30-day lookback window, ensuring high-intent roles are never missed.

### 🧠 2. Statistical Semantic Ranker (v1.5)
A local scoring engine that evaluates roles based on:
- **Top Tier Boost**: +15 point priority for elite firms.
- **Seniority Rubric**: Regex-based salary and title extraction (L6+ focus).
- **Freshness Factor**: Dynamic decay (-0.2 pts/day) to balance intent vs. recency.

### 🛡️ 3. "Zero-Failure" LLM Fallback
To solve API quota constraints (429 errors), the system features a redundant model hierarchy:
- **Primary**: Gemini 2.5 Flash (Experimental/Elite).
- **Secondary**: Gemini 1.5 Flash - Latest (High Capacity).
- **Tertiary**: Gemini 2.0 Flash.

### ✍️ 4. Executive Asset Generation
Generates bespoke, impact-first application materials:
- **Resume Tailoring**: Strictly enforces a **2-line maximum** per bullet, focused on strategic alignment (Action -> Context -> Impact).
- **Honest Cover Letters**: Banned from using "AI-speak" (e.g., "profound interest"). Optimized for direct, executive-to-executive communication.

---

## 🛠️ Tech Stack

- **Orchestration**: Python 3.9+
- **AI Engine**: Google Gemini (Pro/Flash/2.5)
- **Data Layers**: Google Sheets API (Master Tracker)
- **Scraper**: LinkedIn Job Discovery Engine
- **Notifications**: macOS iMessage Integration

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kritinjoshi/job-application-agent.git
   cd job-application-agent
   ```

2. **Configure Environment Variables**:
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_key_here
   SPREADSHEET_ID=your_id_here
   IMESSAGE_RECIPIENT=+1xxxxxxxxxx
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🗓️ Usage

The system is designed for automated daily execution (7:00 AM PST).

**Run the Full Pipeline**:
```bash
PYTHONPATH=. python3 src/main.py
```

**Run Sniper Diagnostic**:
```bash
python3 tests/verify_sniper.py
```

---

## 📊 Telemetry & Monitoring
The system includes a local **Telemetry Manager** that tracks:
- Requests Per Day (RPD)
- Token Consumption
- Model Fallback history

*Logs are stored locally in `data/usage_history.json` and excluded from source control for privacy.*

---

## 📜 License
Private/Proprietary for executive career optimization.
