# Smart Retail Shelf System - Migration to Local/Free Stack

This project has been migrated to a fully local, free-to-use stack, removing all dependency on Google paid APIs (Gemini, YouTube Data API).

## 🚀 Setup Instructions

### 1. Prerequisites
- **Python 3.10+** (Ensure Python is added to PATH)
- **Ollama**: Download and install from [ollama.com](https://ollama.com).

### 2. Environment Setup
1. Open the project folder in a terminal.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Run Local AI (Ollama)
You must have Ollama running with the `llama3` model.
Open a **separate terminal** and run:
```bash
ollama run llama3
```
*Wait until you see the chat prompt `>>>`, then you can minimize this window.*

### 4. Run the Web Application
In your main terminal:
```bash
python manage.py runserver
```

Access the app at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🛠 Technical Changes

- **AI Backend**: `utils.llm_helper` connects to `localhost:11434`.
- **Embeddings**: `GoogleGenerativeAIEmbeddings` replaced with `OllamaEmbeddings`.
- **YouTube**: `utils.youtube_helper` uses `yt-dlp` to fetch comments without API keys.
- **Sentiment**: Replaced heavy Tensorflow/Keras model with lightweight `TextBlob` library (fixes installation issues and removes need for trained .h5 files).
- **Project Structure**: Created `retailai` django project configuration to fix missing settings.

## ⚠️ Notes
- The first time you run `ollama run llama3`, it will download the model (few GBs).
- Text generation speed depends on your local hardware (GPU recommended).
- YouTube fetching might be slower than API but is rate-limit free and free of cost.
