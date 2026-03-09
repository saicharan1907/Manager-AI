# Manager AI - Intelligent MSME Analyst Platform

Manager AI is an advanced, AI-powered inventory and sales management platform built exclusively for MSME (Micro, Small, and Medium Enterprises) business owners. It completely replaces complex spreadsheets by offering an intelligent, natural-language AI conversational agent (powered by Google Gemini), dynamic financial dashboards, PDF reporting, and predictive stock analytics.

##  Key Features
- **Intelligent Dashboards:** Real-time visualization of your total revenue, dead stock, active inventory efficiently, and top-performing sellers.
- **AI Data Analyst:** Communicate naturally with "Manager AI" to instantly generate insights like "What were my top 3 items last month?" or "Do I need to restock anything?".
- **PDF Diagnostic Generation:** Automatically compile your performance into a downloaded PDF invoice/report for immediate distribution.
- **Bulk CSV Uploads:** Migrate thousands of products in one click using simple CSV/Excel file drops.
- **Admin HQ Portal:** A dedicated overview dashboard for tracking superuser logistics and registered system users.

---

##  Local Installation & Setup

Want to run Manager AI on your own computer? Follow these precise steps:

### 1. Clone the Repository
```bash
git clone https://github.com/saicharan1907/Manager-AI.git
cd Manager-AI
```

### 2. Set Up a Virtual Environment (Recommended)
Isolate your Python dependencies so they don't break your computer's native environment:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
You must create a `.env` file in the root folder of the project to securely house your passwords.
Copy the provided `.env.example` structure, or manually create a `.env` file containing:
```ini
# This secures your user login cookies
SECRET_KEY=add_a_random_secure_password_here

# Required for the AI Chatbot to function (Get this from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Connects to your Cloud Database (Neon/Supabase) or defaults to local SQLite if omitted
DATABASE_URL=postgresql://your_db_username:your_db_password@hostname/dbname?sslmode=require
```

### 5. Start the Server
Run the Uvicorn web server natively:
```bash
python -m uvicorn backend.main:app --reload
```
Open **http://127.0.0.1:8000** in your web browser!

---

##  User Workflow (How to use the App)

When a brand-new user registers on your application, they should follow this exact pipeline to unlock the platform's power:

1. **Sign in / Create Account:** Use the dummy Google Login button or standard email protocol. (Note: Using `admin@manager.ai` grants you Admin HQ portal access).
2. **Seed Your Inventory:** Go to the **Inventory** tab. You can either manually create products one-by-one by clicking "Add Product", or seamlessly upload a CSV file containing your current warehouse stock using the file-drop zone.
3. **Log Sales:** Go to the **Sales** tab to register units sold. You can bulk-upload daily sales spreadsheets directly into the dashboard.
4. **Interact with the AI:** Now that the database is populated, click on the **Chat Interface**! Ask the AI natural queries about your business performance, restock recommendations, or revenue milestones. 
5. **Print Reports:** Head over to **Reports** and generate an automatic 1-click PDF Diagnostic Report downloading your current statistics.

---

##  System Limitations & Known Constraints

Please be aware of the following technical limitations when actively using or testing the platform:

* **Upload Limits (Vercel Deployments only):** If you are hosting this application on Vercel's Serverless architecture, Vercel enforces a strict global **4.5 MB hard limit** on file uploads. Attempting to upload a CSV file larger than 4.5 MB will trigger a `413: PAYLOAD_TOO_LARGE` server crash.
  * *Solution:* Split massive spreadsheets into smaller CSV batches, or host the app on a persistent server platform like **Render** or **Railway** instead of Vercel!
* **Cold Starts:** On free-tier cloud databases (like Neon.tech), your database goes to "sleep" after 5 minutes of inactivity. Logging in for the first time after a long break may take ~5 seconds to load as the database wakes up.
* **AI API Rate Limits:** The Google Gemini API (`gemini-2.5-flash`) operates on a standard RPM (Requests Per Minute) free tier. If multiple users execute AI analysis commands simultaneously during a massive traffic spike, the system will temporarily pause or gracefully bounce requests natively.

---

## 🏗️ Tech Stack
* **Backend:** FastAPI (Python), SQLAlchemy, JWT Authentication, Uvicorn
* **Frontend:** HTML5, Tailwind CSS, Vanilla JS
* **Database Engine:** PostgreSQL (Supported) / SQLite (Fallback)
* **AI Engine:** Google Generative AI (`gemini-2.5-flash`)
