🧭 Career Compass (National Edition)

A premium, AI-driven course recommendation engine optimized for the Nigerian education landscape.

🌟 What's New in National Edition?

Glassmorphism UI: A modern, frosted-glass aesthetic for a premium user experience.

Dark Mode: Fully responsive theme switching for night-time usage.

Career Path Visualization: Shows students not just the course, but the job titles they can attain (e.g., "Junior Dev" → "CTO").

National Database: Expanded logic covering Federal, State, and Private universities across all geopolitical zones (North, East, West, South).

🎯 The Problem

High school graduates often struggle to choose university courses that align with both their academic reality and personal interests. Generic tools do not account for:

Catchment Areas: The specific advantage students get when applying to schools in their home state.

Strict Subject Combinations: The fact that you cannot study Medicine without a Credit in Biology, regardless of your JAMB score.

Varied Cut-off Marks: The drastic difference in requirements between schools like UNILAG and private universities.

🛠️ The Solution

Career Compass is a Containerized Web Application that uses a weighted scoring algorithm to predict admission chances with high accuracy.

Key Logic Features

Strict Validation: Automatically disqualifies candidates who fail compulsory subjects (e.g., Medicine requires Credit in Biology).

Catchment Area Bonus: Applies a logic layer that lowers cut-off marks (usually by ~20 points) if the student's "State of Origin" matches the University's catchment zone.

Interest Mapping: Matches psychometric interests (e.g., "Building things", "Helping people") to academic paths.

🚀 SRE Deployment Guide (How to Run)

Prerequisites

Docker Desktop installed and running.

1. Build the Image

Open your terminal in the project folder and run:

docker build -t career-compass-national .


2. Run the Container

Start the production server (Gunicorn) inside the container:

docker run -p 5000:5000 career-compass-national


3. Access the App

Open your browser and visit: http://localhost:5000

📂 Project Structure

career-compass/
├── templates/
│   └── index.html      # The Frontend (Glassmorphism UI)
├── app.py              # The Backend (Flask + Logic Engine)
├── Dockerfile          # Blueprint for the container
├── requirements.txt    # Python dependencies
└── README.md           # This documentation


🏗️ Technical Stack

Frontend: HTML5, TailwindCSS (Dark Mode/Animation), Vanilla JS.

Backend: Python (Flask) with custom logic engine.

Server: Gunicorn (Production WSGI).

Container: Docker (Python 3.9-slim).