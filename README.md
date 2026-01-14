# 🛍️ Team Malaai – AI-Powered Retail Intelligence Platform

Team Malaai is an **AI-driven retail intelligence platform** designed to enhance customer experience, automate insights from reviews, and enable smarter retail operations using **Machine Learning, Computer Vision, and NLP**.

The system integrates multiple AI components such as **recommendation systems, sentiment analysis, object detection, and vector search** into a single scalable web application.

---

## 🎯 Problem Statement

Modern retail systems struggle with:
- Understanding customer sentiment from large-scale reviews
- Personalizing product recommendations
- Managing visual data (products, shelves, customers)
- Extracting actionable insights from unstructured data

**Team Malaai** solves this by combining AI models with a robust backend architecture.

---

## 🚀 Key Features

- 🧠 **AI-based Recommendation Engine**
- ⭐ **Customer Review & Sentiment Analysis**
- 🖼️ **YOLO-based Object Detection**
- 🔍 **FAISS-powered Vector Search**
- 👤 **User Registration & Authentication**
- 📊 **Retail Insights Dashboard**
- ⚙️ **Modular & Scalable Architecture**

---

## 🛠️ Tech Stack

### Backend
- Python
- Django

### AI / ML
- Deep Neural Networks (DNN)
- FAISS (Vector Search)
- YOLO (Object Detection)
- NLP for review analysis

### Frontend
- HTML
- CSS
- JavaScript (Templates-based rendering)
###SCREENSHOTS
<img width="1600" height="800" alt="image" src="https://github.com/user-attachments/assets/c4374957-dcfb-41a3-b9e4-6e47feeac002" />
<img width="1600" height="786" alt="image" src="https://github.com/user-attachments/assets/3baa4ff5-bb83-4da8-a312-2d3398b1fe33" />
<img width="1600" height="802" alt="image" src="https://github.com/user-attachments/assets/4e874e47-56ae-4d35-bdcd-c2af887cfe99" />
###DEMO LINK
https://drive.google.com/file/d/1ZB9BKydZvmDW3962V26fxfhq3IBixPcX/view?usp=drive_link

### Database
- SQLite (can be extended to PostgreSQL)

---

## 🧱 Project Architecture / Folder Structure

```text
malaai/
│
├── dnn_model/          # Deep learning recommendation models
├── faiss_index/        # Vector embeddings & FAISS indexes
├── yolo/               # YOLO-based object detection logic
├── yt_models/          # Pretrained AI/ML models
│
├── retailai/            # Core Django application
├── regloguser/          # User registration & login module
├── reviews/             # Review handling & sentiment analysis
│
├── templates/           # HTML templates
├── static/              # CSS, JS, and static assets
├── utils/               # Helper functions & utilities
│
├── manage.py            # Django entry point
├── requirements.txt     # Python dependencies
├── db.sqlite3           # Database
├── create_dummy_data.py # Script to generate test data
├── README.md            # Project documentation
└── .gitignore           # Ignored files (env, venv, cache)
