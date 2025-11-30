Smart Task Analyzer

Overview

Smart Task Analyzer is a full-stack task prioritization system designed to help users identify the most important tasks based on objective, multi-factor scoring. The system analyzes tasks using a weighted algorithm that accounts for urgency, importance, effort, and dependencies. It includes a RESTful backend built with Django REST Framework and a minimal, responsive frontend built with HTML, CSS, and JavaScript.

The project demonstrates API design, algorithm implementation, validation handling, scoring logic, and a functional user interface for interactive analysis.

Features

Core Functionalities

1.Multi-factor scoring for each task based on:

    Importance

    Urgency (due date proximity)

    Effort (estimated hours)

    Dependency impact

2.Four analysis strategies:

    Smart Balance (default)

    Fastest Wins

    High Impact

    Deadline Driven

3.Circular dependency detection and reporting

4.Bulk JSON task input support

5.Instant browser-based task analysis with explanations

6.Clean, responsive frontend (no frameworks)


API Endpoints

POST /api/tasks/analyze/
Analyzes and scores all tasks, returning them in sorted order.

POST /api/tasks/suggest/
Returns the top three recommended tasks.

GET /api/health/
Health check endpoint verifying backend availability.

Technology Stack
Backend

Python 3.8+

Django 4.x

Django REST Framework

Frontend

HTML5

CSS3

JavaScript

Database

SQLite (default Django configuration)

Installation and Setup
1. Clone the repository
git clone <repository-url>
cd task-analyzer

2. Backend Setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Backend will be available at:
http://localhost:8000

3. Frontend Setup

Option A: Open frontend/index.html directly in any browser.
Option B (recommended for local testing):

cd frontend
python -m http.server 8080


Frontend will be available at:
http://localhost:8080

4. Verify Installation

Run:

curl http://localhost:8000/api/health/


Expected response:

{"status": "ok", "message": "Task Analyzer API is running"}

Scoring Algorithm

The Smart Task Analyzer uses a weighted scoring model based on the following components:

1. Importance (0–100)

User-provided rating (1–10), scaled by a factor of 10.

2. Urgency (0–100)

Based on proximity to the due date:

Overdue: 100

Due today: 90

Due tomorrow: 80

Due in 2–3 days: 60

Due in 4–7 days: 40

Due in 8–14 days: 20

Due in 15+ days: 10

No due date: 0

3. Effort (0–40 bonus)

Lower effort results in a higher score:

≤1 hour: 40

≤2 hours: 30

≤4 hours: 20

≤8 hours: 10

8 hours: 5

4. Dependency Impact (0–50 bonus)

Rewards tasks that unblock other tasks:

Blocks 1 task: 25

Blocks 2 tasks: 35

Blocks 3+ tasks: 50

Strategy Weights

Each strategy applies a weight multiplier to the four scoring components:

Smart Balance

Fastest Wins

High Impact

Deadline Driven

All final task scores include a detailed human-readable explanation.

Testing
Running Backend Tests
cd backend
python manage.py test tasks

Test Coverage Includes

Overdue task scoring

Quick-win detection

Dependency impact scoring

Circular dependency detection

Strategy weight variation

Design Considerations

Stateless API
Tasks are processed per request without persistence. This keeps the system simple and testable.

Weighted Strategy Model
All strategies use the same base algorithm but apply different weight multipliers for flexibility and consistency.

Transparent Scoring
Every scored task includes a breakdown and explanation to ensure clarity for users.

Frontend-Backend Separation
The REST API is fully decoupled from the frontend for easier testing and integration.

Input Validation
Django REST Framework serializers ensure reliable validation of user input.

Circular Dependency Recognition
The system detects but does not block cycles, allowing valid analysis but providing warnings.



Conclusion

Smart Task Analyzer provides a structured, reliable, and flexible task prioritization system suitable for personal productivity, team planning, and academic demonstration. The modular architecture, clear scoring model, and API-driven approach make the project easy to extend and integrate into larger systems.