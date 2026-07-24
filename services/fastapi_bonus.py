import grpc
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))

import uvicorn
from fastapi import FastAPI
import order_pb2
import order_pb2_grpc
import delivery_pb2
import delivery_pb2_grpc
import payment_pb2
import payment_pb2_grpc
import restaurant_pb2
import restaurant_pb2_grpc
import time
import socket

app = FastAPI()


RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

if RUNNING_IN_DOCKER:
    ORDER_SERVICE_HOST = "order-service" 
    DELIVERY_SERVICE_HOST = "delivery-service"
    PAYMENT_SERVICE_HOST = "payment-service"
    RESTAURANT_SERVICE_HOST = "restaurant-service"
else:
    ORDER_SERVICE_HOST = "localhost"
    DELIVERY_SERVICE_HOST = "localhost"
    PAYMENT_SERVICE_HOST = "localhost"
    RESTAURANT_SERVICE_HOST = "localhost"

order_channel = grpc.insecure_channel(f"{ORDER_SERVICE_HOST}:50051")
delivery_channel = grpc.insecure_channel(f"{DELIVERY_SERVICE_HOST}:50053")
payment_channel = grpc.insecure_channel(f"{PAYMENT_SERVICE_HOST}:50056")
restaurant_channel = grpc.insecure_channel(f"{RESTAURANT_SERVICE_HOST}:50055")

order_stub = order_pb2_grpc.OrderServiceStub(order_channel)
delivery_stub = delivery_pb2_grpc.DeliveryServiceStub(delivery_channel)
payment_stub = payment_pb2_grpc.PaymentServiceStub(payment_channel)
restaurant_stub = restaurant_pb2_grpc.RestaurantServiceStub(restaurant_channel)

def send_graphite_metric(metric_name, value):
    try:
        sock = socket.socket()
        sock.connect(("localhost", 2003))
        timestamp = int(time.time())
        message = f"{metric_name} {value} {timestamp}\n"
        sock.send(message.encode())
        sock.close()
    except:
        pass

#Get Restaurant Menu
@app.get("/menu/{restaurant_id}")
async def get_menu(restaurant_id: str):
    start_time = time.time()
    request = restaurant_pb2.RestaurantMenuRequest(restaurant_unique_id=restaurant_id)
    response = restaurant_stub.GetRestaurantsMenu(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.menu.response_time", response_time * 1000)
    return {"restaurant_id": restaurant_id, "menu": [{"name": item.dish_name, "price": item.dish_price} for item in response.available_menu_items]}

#Place order
@app.post("/order")
async def place_order(buyer_id: str, vendor_id: str):
    start_time = time.time()
    request = order_pb2.MakeOrderRequest(buyer_id=buyer_id, vendor_id=vendor_id)
    response = order_stub.MakeOrder(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.order.response_time", response_time * 1000)
    return {"order_id": response.generated_order_id, "status": response.order_confirmation_status}

#Track order status
@app.get("/order/{order_id}/status")
async def get_order_status(order_id: str):
    start_time = time.time()
    request = order_pb2.GetOrderStatusRequest(tracking_order_id=order_id)
    response = order_stub.GetOrderStatus(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.order_status.response_time", response_time * 1000)
    return {"order_id": order_id, "status": response.order_progress_status}

# Assign driver
@app.post("/delivery/assign")
async def assign_driver(order_id: str):
    start_time = time.time()
    request = delivery_pb2.DriverAssignmentRequest(assigned_order_id=order_id)
    response = delivery_stub.AssignDriver(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.delivery_assign.response_time", response_time * 1000)
    return {"driver_id": response.assigned_driver_id, "vehicle": response.assigned_vehicle}

#Update delivery status
@app.put("/delivery/{order_id}/status")
async def update_delivery_status(order_id: str, status: str):
    start_time = time.time()
    request = delivery_pb2.DeliveryStatusUpdateRequest(assigned_order_id=order_id, delivery_status=status)
    response = delivery_stub.UpdateStatus(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.delivery_update.response_time", response_time * 1000)
    return {"order_id": order_id, "update_successful": response.update_successful}

#Process payment
@app.post("/payment")
async def process_payment(payer_id: str, order_id: str, amount: float, method: str):
    start_time = time.time()
    request = payment_pb2.ProcessPaymentRequest(
        payer_id=payer_id, associated_order_id=order_id, transaction_amount=amount, selected_payment_method=method
    )
    response = payment_stub.ProcessPayment(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.payment.response_time", response_time * 1000)
    return {"transaction_id": response.generated_transaction_id, "payment_successful": response.payment_successful}

#Get payment status
@app.get("/payment/{order_id}/status")
async def get_payment_status(order_id: str):
    start_time = time.time()
    request = payment_pb2.GetPaymentStatusRequest(order_id=order_id)
    response = payment_stub.GetPaymentStatus(request)
    response_time = time.time() - start_time
    send_graphite_metric("food_delivery.payment_status.response_time", response_time * 1000)
    return {"order_id": order_id, "payment_status": response.payment_status, "transaction_id": response.transaction_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)