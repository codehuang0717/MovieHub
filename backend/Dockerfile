FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc zlib1g-dev libjpeg-dev && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project code
COPY . .

# Create media and static directories
RUN mkdir -p /app/media /app/staticfiles

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Launch command
CMD ["gunicorn", "movie_recommendation.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
