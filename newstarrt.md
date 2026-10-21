# 🚀 Quick Start & Viva Guide

### Step 1: Start the Backend (Terminal 1)
Open PowerShell or Command Prompt, navigate to the `backend` folder, and run:
```powershell
cd backend
python app.py
```
**Expected Output:**
```text
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
*(Keep this terminal window open!)*

---

### Step 2: Open the Frontend (Browser)
Double-click `frontend/index.html` in File Explorer or run:
```powershell
Start-Process "frontend\index.html"
```

---

## 🎬 The 3-Minute Live Viva Demo Script
When the examiner says: *"Show me the project and what each of you did,"* follow this exact flow:

### Part 1: Project Overview & Core Demo (Presented by Yash)
Point to the open Web UI in the browser. In the chat box, type these test questions:
- **Question 1:** `"Who is the Lead Architect?"`  
  ➔ **Bot Output:** *"According to the verified document, the Lead Architect is Dr. Aris Thorne."*
- **Question 2:** `"What is the override code for Level 3?"`  
  ➔ **Bot Output:** *"The override code for the Level 3 diagnostic terminal is 'NEXUS-99-OMEGA'."*
- **Question 3:** `"What is the maximum operating temperature?"`  
  ➔ **Bot Output:** *"The system operates at a maximum temperature threshold of 4.2 Kelvin. If breached, the Aegis Protocol shuts down the mainframe."*
- **Show Vector Stats:** Open `http://127.0.0.1:5000/api/stats` in a browser tab to show the total indexed chunks in ChromaDB.

### Part 2: Session Management & Ingestion (Presented by Shreyas)
- In the Web UI, click the grey **Clear Chat** button to demonstrate memory reset via `/api/clear-history`.
- Ingest a `.txt` or `.md` file to prove multi-format support.
- Show the Health Check: Open `http://127.0.0.1:5000/api/health` in a browser tab to prove service uptime.

### Part 3: Web Client Architecture (Presented by Harsh)
Explain the frontend structure:
- *"The frontend is a lightweight, responsive single-page web client built in `frontend/index.html`."*
- *"It handles asynchronous communication with the Flask REST endpoints using modern JavaScript `fetch()` APIs and safe DOM message rendering."*

### Part 4: Automated Testing & QA (Presented by Mahavir)
Run the test suite in terminal:
```powershell
cd backend
python -m pytest test_health.py
```
Show the examiner the green output: **`1 passed in 0.97s`**.

### Part 5: Open Source Collaboration Evidence (All Members)
Open your GitHub repository in the browser:
- **Closed Pull Requests Tab:**  
  👉 [https://github.com/yash1616-accept/nexus_rag_chatbot/pulls?q=is%3Apr+is%3Aclosed](https://github.com/yash1616-accept/nexus_rag_chatbot/pulls?q=is%3Apr+is%3Aclosed)  
  Show the merged Pull Requests with purple badges:
  - PR #6 (Shreyas): `@Shreyas26X`
  - PR #5 & #2 (Harsh): `@Harsh31749`
  - PR #3 (Mahavir): `@mahavirgujarani04`
  - PR #4 (Yash): `@yash1616-accept`
- **Terminal Tree:** Run:
  ```bash
  git log --graph --pretty=format:"%h - %an: %s" -n 8
  ```
