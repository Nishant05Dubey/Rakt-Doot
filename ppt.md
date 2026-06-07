---
marp: true
theme: default
paginate: true
header: 'Rakt Doot: Autonomous Blood Donor Coordination'
footer: 'Team Name | Blend Hackathon - Blood Warriors'
---

# Rakt Doot (रक्त दूत) 🩸
### Autonomous, AI-Powered Blood Donor Coordination Platform
**Team Name:** [Insert Your Team Name Here]  
**Problem Statement:** Blood Warriors - Automating the donor coordination process for Thalassemia patients.

---

# ⚠️ The Problem: A Lifelong Crisis

### The Hidden Toll of Thalassemia
- **Lifelong Transfusions:** A Thalassemia Major patient requires blood transfusions every 2 to 3 weeks. Over a lifetime, that amounts to **500 - 700 transfusions**.
- **The Coordination Nightmare:** NGO volunteers and family members spend countless exhausting hours cold-calling donors to find a compatible match who is available and hasn't donated recently.
- **Critical Delays:** Finding a donor in emergency or critical situations often takes days, putting the patient's life at severe risk.
- **Burnout:** The manual effort required to track donor cooldowns (90 days) and availability is highly prone to human error and leads to immense volunteer burnout.

---

# 💡 Our Solution: Rakt Doot

**Rakt Doot** completely eliminates the manual coordination bottleneck by introducing a **100% Serverless, Autonomous AI Agent** that handles donor outreach from start to finish.

### Core Philosophy
- **Zero Human Intervention:** From the moment a blood request is generated, the AI handles the database filtering, messaging, calling, and confirmation.
- **Empathetic AI:** Leveraging state-of-the-art NLP to speak with donors naturally in Hinglish, ensuring respect and understanding.
- **Data-Driven Matchmaking:** Geospatial and temporal matching ensures we only contact eligible donors who are close by.

---

# ⚙️ Working Model & Features (1/2)

### 🗺️ Geographic Donor Pods & Smart Match Engine
- Aggregates over 5,000+ donors, tracking live availability, blood type, and exact coordinates.
- **Algorithmic Filtering:** Automatically strictly filters out donors who have donated within the last 90 days.
- **Proximity Sorting:** Ranks donors based on actual geospatial distance and a dynamic reliability score.

### 💬 Conversational WhatsApp Agent
- Auto-triggers WhatsApp outreach to the top-matched donor.
- Uses **Amazon Bedrock (Claude 3 Haiku)** to engage donors in a fluid, context-aware **Hinglish** conversation.
- Asks for availability, answers basic queries, and secures confirmation seamlessly.

---

# ⚙️ Working Model & Features (2/2)

### 📞 Autonomous Voice Calling (Vapi AI)
- For **Urgent** & **Critical** requests, Rakt Doot immediately initiates an AI voice call to the donor.
- The Voice Bot introduces itself, explains the emergency, and instructs the donor to confirm their slot via WhatsApp, creating a perfectly closed-loop system.

### 🔄 Intelligent Auto-Escalation
- If a donor declines (via text or voice), the AI thanks them and **instantly auto-escalates** to the next best match in the queue without needing human approval.
- Real-time sync updates the central NGO Dashboard instantly when a donor says "YES".

---

# 📸 System Interface & Screenshots

*(Insert Screenshots of your application here)*

- **Screenshot 1:** The NGO Command Center Dashboard (showing Live Donor Pods and Urgent Requests).
- **Screenshot 2:** Live Coordination Panel showing the Radar UI scanning for matches.
- **Screenshot 3:** WhatsApp Chat Screenshot showing the Amazon Bedrock AI conversing in Hinglish and confirming the donation.

> **Speaker Notes:** Highlight the real-time nature of the UI—mention how the "Searching" badge automatically flips to "Confirmed" when the webhook fires.

---

# 🛠️ Tech Stack & Architecture

Rakt Doot is built on a highly scalable, event-driven Serverless architecture.

**Frontend Layer:**
- **React.js & Vite:** Blazing fast SPA with custom glassmorphism UI.

**Serverless Infrastructure (AWS):**
- **Amazon API Gateway & AWS Lambda:** 6 independent microservices orchestrating the workflow.
- **Amazon DynamoDB:** NoSQL database handling the 5000+ donor dataset with lightning-fast querying.

**AI & Communication Layer:**
- **Amazon Bedrock (Claude 3 Haiku):** Powers the core conversational intelligence.
- **Vapi AI:** Voice AI platform for lifelike outbound phone calls.
- **Twilio:** Handles the WhatsApp Sandbox API integrations.

---

# 🚀 Future Enhancements

We envision Rakt Doot evolving from a reactive coordination tool into a proactive healthcare platform:

1. **Predictive AI Models:**
   - Implement Machine Learning to predict regional blood shortages during specific seasons (e.g., Dengue outbreaks) and pre-emptively engage donors.
   
2. **Wearable & Health App Integration:**
   - Sync with Apple Health / Google Fit to ensure donors are physically well enough to donate before the AI even contacts them.

3. **Logistics Integration:**
   - Auto-book Uber/Ola rides for confirmed donors directly to the hospital to reduce drop-off rates.

4. **Gamification & Rewards:**
   - Introduce an automated token-based reward system for consistent "Bridge Donors."
