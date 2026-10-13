
# 🎙️ VoiceNote AI
### Multilingual Audio Transcription & AI Summarization

VoiceNote AI is an AI-powered web application that converts audio recordings into text and generates concise summaries using Sarvam AI. Built with Python and Streamlit, it provides a simple interface for transcribing recordings, reviewing transcripts, and downloading results.

## ✨ Features

- **Audio Transcription:** Convert audio recordings into text using Sarvam AI's Saaras v4 speech-to-text model.
- **Multilingual Support:** Supports English, Hindi, Kannada, and Tamil, with an auto-detect option.
- **Batch Processing:** Uses Sarvam AI's batch transcription workflow for processing uploaded recordings.
- **Timestamps:** Optionally retrieve and display phrase or sentence timestamps when provided by the transcription API.
- **AI Summarization:** Generate concise summaries of transcripts using Sarvam's LLM API.
- **Download Results:** Export transcripts and generated summaries as text files.
- **Interactive Interface:** Upload recordings and view results through a Streamlit web application.

## 🛠️ Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **Speech-to-Text:** Sarvam AI Saaras v4
- **LLM:** Sarvam AI Chat Completions API
- **Libraries:** `sarvamai`, `python-dotenv`, `streamlit`
- **Data Handling:** JSON and Python file handling

## 🏗️ Application Workflow

1. Upload an audio recording.
2. Choose a language or select auto-detection.
3. Optionally enable timestamps.
4. Submit the recording for speech-to-text transcription.
5. Review the generated transcript.
6. Generate an AI-powered summary.
7. Download the transcript and summary.

## 📂 Project Structure

```text
VoiceNote-AI/
├── app.py
├── requirements.txt
├── .gitignore
├── .env                 # Local API credentials; not committed
└── .venv/               # Local virtual environment; not committed
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/02-Yuvraj/VoiceNote-AI.git
cd VoiceNote-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root and add your own Sarvam AI API key:

```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

Replace the placeholder with your actual API key. Never commit your `.env` file or expose your API key publicly.

### 5. Launch the application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL that you can open in your browser.

## ☁️ Deployment

VoiceNote AI can be deployed using Streamlit Community Cloud.

1. Connect your GitHub repository.
2. Select `app.py` as the main file.
3. Configure `SARVAM_API_KEY` in the application's Streamlit Secrets settings.
4. Deploy and test the application.

Do not upload your local `.env` file to GitHub.

## 🔐 API Usage and Security

- A valid Sarvam AI API key is required.
- API usage is subject to the provider's applicable quotas, rate limits, and pricing.
- Keep API credentials private.
- A publicly accessible deployment may allow other users to trigger API requests using the configured account. Add suitable access controls and usage limits before sharing it widely.

## 🎯 Project Objective

The goal of VoiceNote AI is to simplify audio-based information processing by combining speech recognition and large language model summarization in a single web application.

## 👨‍💻 Author

**Yuvraj Singh**

GitHub: [02-Yuvraj](https://github.com/02-Yuvraj)

---

*Built with Python, Streamlit, and Sarvam AI.*
