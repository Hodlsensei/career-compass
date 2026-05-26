# 1. Use an official Python runtime as a parent image
# We use 'slim' to keep the image size small (SRE Best Practice)
FROM python:3.9-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the current directory contents into the container at /app
# This automatically copies 'app.py', 'requirements.txt', and the 'templates' folder
COPY . /app

# 4. Install dependencies
# It reads the requirements.txt file to install Flask, Flask-CORS, and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# 5. Make port 5000 available to the world outside this container
EXPOSE 5000

# 6. Define environment variable
ENV FLASK_APP=app.py

# 7. PRODUCTION COMMAND:
# We use 'gunicorn' (Green Unicorn) instead of the default 'python app.py'.
# -b 0.0.0.0:5000 -> Binds the server to all network interfaces so the browser can reach it.
# app:app -> Tells Gunicorn to look in 'app.py' for the 'app' object.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]