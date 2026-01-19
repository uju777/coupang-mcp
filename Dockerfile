FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY http_server.py .
COPY static/ ./static/

EXPOSE 7860

CMD ["python", "http_server.py"]
