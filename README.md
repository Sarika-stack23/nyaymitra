# ⚖️ NyayMitra — Your Free AI Legal Assistant

> *Speak your problem. Know your rights. Get your document. — Free.*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.3-green.svg)](https://groq.com)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🇮🇳 What is NyayMitra?

NyayMitra (Justice Friend) is a free AI-powered legal assistant built for every Indian citizen.

Millions of Indians face wage theft, landlord disputes, consumer fraud, domestic violence, and more — but cannot afford lawyers or navigate complex legal systems. NyayMitra solves this by:

- 🗣️ **Listening** to your problem in your own language (voice or text)
- ⚖️ **Explaining** your legal rights in simple words
- 📄 **Generating** ready-to-use legal documents instantly
- 🗺️ **Guiding** you to the exact office to go to
- 📧 **Emailing** your documents directly to you

---

## 🎯 Legal Domains Covered

| Domain | Law | Documents Generated |
|--------|-----|-------------------|
| 👷 Labor & Wages | Payment of Wages Act, 1936 | Legal Notice + Labour Complaint |
| 🏠 Tenant Rights | Karnataka Rent Control Act | Legal Notice to Landlord |
| 🛒 Consumer Rights | Consumer Protection Act, 2019 | Consumer Complaint + Demand Notice |
| 👨‍👩‍👧 Family & DV | Hindu Marriage Act + DV Act, 2005 | Domestic Violence Complaint |
| 📋 RTI | Right to Information Act, 2005 | RTI Application Letter |
| 🚔 FIR | CrPC, 1973 | Police Complaint Letter |

---

## 🌐 Languages Supported

- English
- Hindi (हिंदी)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Telugu (తెలుగు)

---

## ✨ Features

- 💬 **AI Chatbot** — Conversational legal guidance powered by Groq LLaMA 3.3
- 🎤 **Voice Input** — Speak your problem using Whisper speech-to-text
- 🔊 **Voice Output** — AI replies read aloud using gTTS
- 📄 **Document Generator** — Auto-fills 8 types of legal documents
- ⬇️ **PDF Download** — Download your document instantly
- 📧 **Email Delivery** — Send document directly to your email
- 🗺️ **Office Locator** — Google Maps link to nearest relevant office
- 📊 **Progress Tracker** — See exactly where you are in the process
- 🔄 **Multi-Case** — Reset and start a new case anytime

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/nyaymitra.git
cd nyaymitra
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install ffmpeg (for voice)
```bash
# Ubuntu/Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 4. Add your API keys
Open `main.py` and update:
```python
GROQ_API_KEY  = "your_groq_api_key_here"   # https://console.groq.com
EMAIL_SENDER  = "your_gmail@gmail.com"      # Optional — for email feature
EMAIL_PASSWORD = "your_app_password"        # Google App Password
```

### 5. Run
```bash
python main.py
```

### 6. Open in browser
```
http://localhost:7860
```

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| AI / LLM | Groq — LLaMA 3.3 70B Versatile |
| Speech to Text | OpenAI Whisper |
| Text to Speech | gTTS (Google TTS) |
| PDF Generation | FPDF2 |
| Translation | Deep Translator |
| Language Detection | LangDetect |
| UI | Gradio |
| Email | Python SMTP (Gmail) |
| Maps | Google Maps URL API |

---

## 📁 Project Structure

```
nyaymitra/
│
├── main.py              ← Complete single-file application (1620 lines)
├── requirements.txt     ← All Python dependencies
├── README.md            ← This file
├── .gitignore           ← Git ignore rules
└── HOW_TO_RUN.txt       ← Step by step setup guide
```

---

## 🧠 How It Works

```
User Opens App
      ↓
Selects Language (English / Hindi / Kannada / Tamil / Telugu)
      ↓
Speaks or Types Problem
      ↓
AI Classifies Legal Domain (labor / tenant / consumer / family / rti / fir)
      ↓
AI Explains Rights in User's Language
      ↓
AI Asks Follow-Up Questions One by One
      ↓
User Answers All Questions
      ↓
AI Generates Legal Document(s)
      ↓
PDF Generated → Download / Email
      ↓
AI Gives Step-by-Step Action Guide
      ↓
Google Maps Link to Nearest Office
```

---

## 👤 Real Use Case

> Ramesh Kumar, a construction worker from Kanakapura, worked for 8 months without full payment.
> His contractor owed him ₹38,000 but refused to pay.
> Ramesh didn't know his rights. He couldn't afford a lawyer. He didn't speak English.
>
> **With NyayMitra:**
> - He spoke his problem in Kannada
> - Learned his rights under the Payment of Wages Act
> - Got a Legal Notice + Labour Complaint generated in 2 minutes
> - Downloaded the PDF and sent it to the contractor
> - Got directions to the Labour Commissioner office
>
> **Justice — in his language. For free.**

---

## 🏆 Built For

**HackBLR 2026** — #BuildTheFuture
National-level AI Hackathon by HiDevs
Theme: Legal — Access to Justice & Documentation

---

## 📋 Requirements

```
groq
gradio
openai-whisper
gTTS
fpdf2
langdetect
deep-translator
ffmpeg-python
requests
```

---

## ⚙️ Getting Groq API Key (Free)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Click **API Keys** → **Create API Key**
4. Copy and paste into `main.py`

---

## 📧 Setting Up Email (Optional)

1. Go to your Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords → Create new app password
4. Copy the 16-character password into `main.py`

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — Ultra-fast LLM inference
- [OpenAI Whisper](https://github.com/openai/whisper) — Speech recognition
- [Gradio](https://gradio.app) — ML UI framework
- [HiDevs](https://hidevs.com) — HackBLR 2026

---

*⚠️ NyayMitra provides legal information to help users understand their rights.
For complex legal matters, please also consult a qualified lawyer.
This tool does not store any personal information.*