FROM python:3.9-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50055

CMD ["python", "services/restaurant_service.py"]
