# 🚦 V-Watch Traffic Violation Detection System (YOLO)

An AI-powered traffic monitoring system that detects violations (e.g., red light crossing) and extracts vehicle number plates using Computer Vision.

---

## 🚀 Features

* 🎥 Upload and process traffic videos
* 🚗 Vehicle detection using YOLO
* 🚦 Violation detection (line crossing logic)
* 🔍 Automatic Number Plate Recognition (ANPR)
* 📊 Live violation display using Streamlit
* 🧠 Hashing for evidence integrity

---

## 🛠️ Tech Stack

* Python 3.9+
* OpenCV
* YOLO (Ultralytics / custom model)
* Streamlit
* Torch

---

## 📁 Project Structure

```
VWatch/
├── app/
│   ├── ai/                # Detection, tracking, ANPR logic
│   ├── core/              # Utilities (hashing, video reader, state)
│   ├── db/                # Database (optional)
│   ├── config.py
│   ├── main.py
│   └── ui.py              # Streamlit UI
├── database/
│   └── violations.db
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/MuneebProblemSolver/VWatch-Traffic-Analysis-System-YOLO.git
cd VWatch-Traffic-Analysis-System-YOLO
```

---

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux

# OR (Windows)
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run the Application

```bash
streamlit run app/ui.py
```

---

### 5️⃣ Open in Browser

```
http://localhost:8501
```

---

## 📦 Model Files (IMPORTANT)

If YOLO model weights (`.pt`) are not included:

👉 Download from: **[Add your Google Drive / link here]**

Place it inside:

```
app/ai/
```

---

## ⚠️ Notes

* Do NOT upload `venv/` to GitHub
* Make sure video format is `.mp4`
* Works best with clear traffic footage

---

## 👨‍💻 Author

**Malik Muneeb**
AI Engineer | Software Developer

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
