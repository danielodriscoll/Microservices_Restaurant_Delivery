FROM python:3.9-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50051

CMD ["python", "services/order_service.py"]
