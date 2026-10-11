# 1. Use an official lightweight Python image
FROM python:3.12-slim-bookworm

# 2. Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr (essential for logging)
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app



# 4. Install system dependencies (Uncomment if using PostgreSQL/mysqlclient)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy and install dependencies first (leverages Docker cache caching)
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . /app/

# 7. Expose the port Django runs on
EXPOSE 8000

# 8. Run Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
