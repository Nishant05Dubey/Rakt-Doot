# Rakt Doot (रक्त दूत) 🩸

**An Autonomous, AI-Powered Blood Donor Coordination Platform**

Rakt Doot is a full-stack, serverless application built for the **Blend Hackathon (Blood Warriors problem statement)**. It completely digitizes and automates the process of finding, contacting, and confirming blood donors for Thalassemia patients.

By leveraging an event-driven AWS architecture, **OpenAI GPT** for intelligent WhatsApp conversations, and **Vapi AI** for automated voice calling, Rakt Doot eliminates the need for NGO volunteers to make exhausting manual phone calls to coordinate the 500-700 lifetime transfusions required by Thalassemia patients.

---

## 🚀 Key Features

### 🎛️ NGO Command Center
- A beautiful React dashboard providing a bird's-eye view of all active patients, urgent requests, and system health metrics.
- One-click **"Activate Rakt Doot"** button to trigger the entire automated donor coordination pipeline.

### 🗺️ Geographic Donor Pods
- Aggregates and displays the real-time availability of 5,000+ donors clustered by region (e.g., Delhi NCR, Pune Metro).

### 🧠 Smart Matching Engine
- An AWS Lambda algorithm that filters donors by blood type compatibility, proximity, and reliability score.
- Automatically enforces a **90-day medical cooldown period** to ensure donor safety.
- Tracks contacted donors to prevent duplicate outreach.

### 💬 WhatsApp AI Chatbot (Amazon Bedrock + Twilio)
- Sends automated WhatsApp messages to matched donors via **Twilio Sandbox API**.
- Uses **Amazon Bedrock (Claude 3 Haiku)** to hold intelligent, lightning-fast, empathetic conversations in **Hinglish** (Hindi + English) natively within AWS.
- Follows a structured flow: asks availability → confirms donation → provides hospital details → or gracefully handles decline.
- **NLP fallback engine** ensures robust offline responses.

### 📞 Automated Voice Calling (Vapi AI)
- For **Urgent** requests (≤3 days left for blood), the system automatically places an **AI-powered phone call** to the top donor match.
- Powered by **Vapi AI** — a voice AI platform that handles natural, conversational phone calls.
- The AI agent introduces itself as Rakt Doot, explains the urgency, and collects scheduling information from the donor.
- Supports multilingual detection (English, Hindi, Telugu).

### 🔄 Auto-Escalation & Real-Time Sync
- **Vapi WhatsApp Loop**: Vapi voice AI intelligently directs donors to confirm via WhatsApp ("Reply YES to the text we just sent"), routing all confirmations through the ultra-reliable Twilio webhook.
- If a donor **declines** (via WhatsApp or voice), the system automatically contacts the **next best match** — no human intervention needed.
- **Auto-Refreshing React UI**: The dashboard polls the live DynamoDB database to instantly flip UI states to "Confirmed" without page reloads.

### 📊 Real-time AI Activity Feed
- An audit log displaying every action the AI takes in the background (scanning pods, sending alerts, generating tokens).

### 🏥 Urgency-Based Triage System
| Urgency Level | Blood Needed In | Action |
|---|---|---|
| **Urgent** 🔴 | 3 days | WhatsApp + AI Voice Call |
| **Critical** 🟠 | 6 days | WhatsApp message only |
| **Needy** 🟡 | 10 days | WhatsApp message only |

---

## 🛠️ Architecture & Tech Stack

Rakt Doot is built on a **100% Serverless Microservices Architecture**, ensuring infinite scalability and zero idle server costs for the NGO.

### Frontend (User Interaction Layer)
- **React.js (Vite)** — Fast, modern SPA
- **Vanilla CSS** — Custom medical-grade dark mode UI with glassmorphism

### Backend (Intelligence & Orchestration)
- **Amazon API Gateway** — Secure routing for all frontend and webhook requests
- **AWS Lambda (Python 3.12)** — 6 independent serverless microservices:
  - `create_request` — Creates new blood requests and triggers the matching pipeline
  - `match_donors` — AI matching algorithm + Twilio WhatsApp + Vapi voice calling
  - `donor_response` — Processes incoming WhatsApp replies with OpenAI chatbot
  - `voice_bot_escalation` — Handles Vapi voice call webhooks
  - `chat_bot` — General chat interface
  - `admin_dashboard` — Real-time dashboard stats and patient queue
- **Amazon DynamoDB** — Blazing fast NoSQL database storing 5,000+ donor records and real-time patient queues
- **Amazon EventBridge** — Event-driven coordinator that triggers automated workflows

### AI & Communication
- **Amazon Bedrock (Claude 3 Haiku)** — Natively powers the WhatsApp conversational chatbot with context-aware, empathetic Hinglish responses securely via IAM.
- **Vapi AI** — Voice AI platform for automated outbound phone calls to donors.
- **Twilio** — WhatsApp Sandbox API for sending/receiving donor messages.

---

## 📂 Project Structure

```text
Rakt-Doot/
├── frontend/                 # React.js application
│   ├── src/
│   │   ├── components/       # Reusable UI components (Sidebar, Header, LiveCoordinationPanel)
│   │   ├── pages/            # Dashboard views (Overview, Patients, DonorPods, LiveFeed, Settings)
│   │   └── App.jsx           # Main routing layer
├── backend/                  # Serverless Architecture
│   ├── functions/            # AWS Lambda Microservices
│   │   ├── admin_dashboard/  # Dashboard stats & patient queue API
│   │   ├── chat_bot/         # General chat interface
│   │   ├── create_request/   # Blood request creation + EventBridge trigger
│   │   ├── donor_response/   # WhatsApp webhook + OpenAI chatbot
│   │   ├── match_donors/     # Smart matching + Twilio WA + Vapi voice calls
│   │   └── voice_bot_escalation/  # Vapi voice call webhook handler
│   └── scripts/              # Infrastructure-as-Code & DB Seeding
│       ├── setup_dynamodb.py
│       ├── seed_dynamodb.py
│       ├── deploy_lambdas.py
│       └── setup_api_gateway.py
└── dataset.json              # Cleaned and processed donor dataset (5,000+ records)
```

---

## 💻 Running the Project Locally

### 1. Prerequisites
- Node.js (v18+) installed
- Python 3.12+ installed
- AWS CLI installed and configured with `aws configure`
- Twilio account (free sandbox works)
- Vapi AI account with a phone number
- OpenAI API key

### 2. Environment Variables
Set these environment variables before deploying the backend:
```bash
export TWILIO_ACCOUNT_SID=your_twilio_sid
export TWILIO_AUTH_TOKEN=your_twilio_auth_token
export VAPI_API_KEY=your_vapi_api_key
export VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
# Note: Amazon Bedrock authenticates automatically via the IAM Lambda Execution Role! No API keys needed for the WhatsApp bot.
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The application will launch at `http://localhost:5173`.

### 4. Backend Deployment
The backend uses Python `boto3` scripts to automatically provision all infrastructure in your AWS account.
```bash
cd backend/scripts

# 1. Create DynamoDB Tables
python setup_dynamodb.py

# 2. Seed the 5,000+ donor dataset into DynamoDB
python seed_dynamodb.py

# 3. Zip and deploy all 6 AWS Lambda functions
python deploy_lambdas.py

# 4. Provision and link API Gateway (Copy the resulting URL into your frontend .env file)
python setup_api_gateway.py
```

### 5. Twilio WhatsApp Setup
1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Join the sandbox from your phone
3. Set the **"When a message comes in"** webhook URL to: `https://YOUR_API_GATEWAY_URL/donor/respond`

---

## 🔮 How It Works (End-to-End Flow)

```
1. NGO adds a patient request (blood type, hospital, urgency)
         ↓
2. Smart Matching Engine finds top 5 compatible donors
         ↓
3. System sends WhatsApp message to the best match
         ↓
4. [If Urgent] Vapi AI simultaneously places a voice call
         ↓
5. Donor replies on WhatsApp → OpenAI chatbot handles conversation
         ↓
6. Donor says YES → Status = Confirmed ✅
   Donor says NO  → Auto-escalate to next donor 🔄
         ↓
7. Dashboard updates in real-time
```

---

## 👥 Team

Built with ❤️ for the **Blend Hackathon — Blood Warriors Problem Statement**

---

## 📜 License

This project is built for social good. Feel free to fork, contribute, and deploy it for any blood donation coordination use case.
