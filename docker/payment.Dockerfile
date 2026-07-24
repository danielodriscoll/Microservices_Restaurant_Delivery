FROM python:3.9-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50056

CMD ["python", "services/payment_service.py"]
