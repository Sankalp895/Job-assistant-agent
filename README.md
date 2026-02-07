# 🚀 AI Job Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**AI Job Assistant** is a powerful tool designed to streamline your job application process. Using advanced LLMs and automated tools, it helps you analyze job descriptions, tailor your resume, and even generate answers for application questions—all in one place.

---

## ✨ Key Features

-   **🔍 Intelligent Job Matching**: Scrape job details from any URL or enter them manually to get an AI-powered match score against your resume.
-   **📄 PDF Resume Support**: Effortlessly upload and parse your PDF resumes for analysis.
-   **🤖 Automated Q&A**: Generate tailored answers for those tricky job application questions based on your profile and the job requirements.
-   **⚡ Smart Job Search**: Find your next opportunity quickly with built-in job search powered by `python-jobspy`.
-   **📊 Personalized Dashboard**: Track all your applications, matching scores, and status in a sleek, modern interface.
-   **🎯 User Profiles & Preferences**: Save your preferences and career goals to get more relevant AI insights.

---

## 🛠️ Tech Stack

-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
-   **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) with SQLite
-   **AI Engine**: [OpenRouter](https://openrouter.ai/) (supporting various models)
-   **Frontend**: Vanilla HTML5, CSS3, and JavaScript (Modern & Responsive)
-   **Job Scraping**: Custom scraper with `python-jobspy`, `httpx`, and `beautifulsoup4`
-   **PDF Processing**: `PyPDF2`

---

## 🚀 Getting Started

### 📋 Prerequisites

-   Python 3.8+
-   An [OpenRouter API Key](https://openrouter.ai/keys)

### 📥 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ParthSharma272/Startup_health_engine.git
    cd Startup_health_engine
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY=your_actual_api_key_here
    ```

---

## 🖥️ Usage

### Running the Backend

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. You can explore the interactive API docs at `http://localhost:8000/docs`.

### Using the Frontend

Simply open `forntend/home.html` in your favorite web browser to start using the application.

---

## 📁 Project Structure

```text
JOB_assistant/
├── app/                  # Backend application logic
│   ├── agents/           # AI Agents (Scoring, Answer, etc.)
│   ├── tools/            # Utility tools (Job Scraper)
│   ├── main.py           # FastAPI entry point
│   ├── models.py         # Pydantic models
│   └── database.py       # SQLAlchemy setup & DB logic
├── forntend/             # Frontend HTML/CSS/JS files
├── tests/                # Unit and integration tests
├── .data/                # SQLite database storage (auto-created)
├── .env                  # Environment variables (private)
└── requirements.txt      # Project dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you have ideas for improvements or new features.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (if applicable).

---

> [!NOTE]
> Made with ❤️ by the AI Job Assistant team. Enjoy your job hunt!
