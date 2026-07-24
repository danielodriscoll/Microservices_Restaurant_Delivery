
import grpc
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))


import order_pb2
import order_pb2_grpc
import delivery_pb2
import delivery_pb2_grpc
import restaurant_pb2
import restaurant_pb2_grpc
import payment_pb2
import payment_pb2_grpc

#THis allows me to run test_client on local host servers and also docker containers using docker-compose enironment variable
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

#Set grpc services to docker or localhost 
ORDER_SERVICE_HOST = "order_service" if RUNNING_IN_DOCKER else "localhost"
DELIVERY_SERVICE_HOST = "delivery_service" if RUNNING_IN_DOCKER else "localhost"
PAYMENT_SERVICE_HOST = "payment_service" if RUNNING_IN_DOCKER else "localhost"
RESTAURANT_SERVICE_HOST = "restaurant_service" if RUNNING_IN_DOCKER else "localhost"

# setup grpc  clients
order_channel = grpc.insecure_channel(f"{ORDER_SERVICE_HOST}:50051")
order_stub = order_pb2_grpc.OrderServiceStub(order_channel)

delivery_channel = grpc.insecure_channel(f"{DELIVERY_SERVICE_HOST}:50053")
delivery_stub = delivery_pb2_grpc.DeliveryServiceStub(delivery_channel)

payment_channel = grpc.insecure_channel(f"{PAYMENT_SERVICE_HOST}:50056")
payment_stub = payment_pb2_grpc.PaymentServiceStub(payment_channel)

restaurant_channel = grpc.insecure_channel(f"{RESTAURANT_SERVICE_HOST}:50055")
restaurant_stub = restaurant_pb2_grpc.RestaurantServiceStub(restaurant_channel)

# ensure servers are up and running
time.sleep(5)

# Test viewing  Menus
print(".....................................")
print(".....................................")

print("Test (Customer/CLient) viewing Menus")
restaurant_request = restaurant_pb2.RestaurantMenuRequest(restaurant_unique_id="Restaurant1")
restaurant_response = restaurant_stub.GetRestaurantsMenu(restaurant_request)
print("Test successful: Customer/CLient viewed: ")

for item in restaurant_response.available_menu_items:
    print(f"   - {item.dish_name}: ${item.dish_price}")

print(".....................................")
print(".....................................")

# test Customer/Client making an order
print("Testing Customer/Client making order")
order_request = order_pb2.MakeOrderRequest(buyer_id="Daniel", vendor_id="Restaurant1")
order_response = order_stub.MakeOrder(order_request)
print(f"Order Created: {order_response.generated_order_id}, Status: {order_response.order_confirmation_status}")

print(".....................................")
print(".....................................")

#Test customer/client making payment
print("Testing Customer/Client making payment")
payment_request = payment_pb2.ProcessPaymentRequest(payer_id = "Daniel", associated_order_id = order_response.generated_order_id, transaction_amount = 15.0, selected_payment_method = "card")
payment_response = payment_stub.ProcessPayment(payment_request)
print(f"Payment made: Payment ID: {payment_response.generated_transaction_id}")

print(".....................................")
print(".....................................")

#Test Tracking Payment 
print("Testing restaurant tracking payment")
payment_status_request = payment_pb2.GetPaymentStatusRequest(order_id=order_response.generated_order_id)
payment_status_response = payment_stub.GetPaymentStatus(payment_status_request)
print(f"Payment Status for order {order_response.generated_order_id}: {payment_status_response.payment_status}")

print(".....................................")
print(".....................................")

# Test Assigning a Driver to a order
print("Testing Assigning a new driver to order")
driver_assign_request = delivery_pb2.DriverAssignmentRequest(assigned_order_id=order_response.generated_order_id)
driver_assign_response = delivery_stub.AssignDriver(driver_assign_request)

if driver_assign_response.assigned_driver_id:
    print(f"Driver {driver_assign_response.assigned_driver_id} assigned to order: {order_response.generated_order_id}")
else:
    print(f"Failed to assign driver to order: {order_response.generated_order_id}")

print(".....................................")
print(".....................................")

#Test customer/client tracking dleivery status
print("Testing Customer/client tracking delivery status")
delivery_status_request = delivery_pb2.DeliveryStatusRequest(assigned_order_id=order_response.generated_order_id)
delivery_status_response = delivery_stub.GetStatus(delivery_status_request)
print(f"Order Delivery Status: {delivery_status_response.delivery_status}")

print(".....................................")
print(".....................................")

#Testing restaurant updating their menu
print("Testing restaurant updating menu")
update_menu_request = restaurant_pb2.UpdateRestaurantMenuRequest(restaurant_unique_id="Restaurant1", updated_menu_items = [restaurant_pb2.MenuListing(dish_name = "Updated CheeseBurger", dish_description = "Cheeseburger", dish_price = 14)])
update_menu_response = restaurant_stub.UpdateRestaurantsMenu(update_menu_request)
print(f"Restaurant menu updated: {update_menu_response.update_successful}")

print(".....................................")
print(".....................................")

#Test restaurant accept/reject order
print("Testing restaurant accepting order")
order_decision_request = restaurant_pb2.OrderDecisionStatusRequest(order_tracking_id = order_response.generated_order_id, is_accepted = True)
order_decision_response = restaurant_stub.OrderAcceptanceStatus(order_decision_request) 
print(f"Restaurant order confirmed order: {order_decision_response.decision_confirmed}")

print(".....................................")
print(".....................................")

#Test delivery driver viewing assigned orders
print("Testing delivery driver viewing their orders")
driver_deliveries_request = delivery_pb2.DriverRequest(driver_id=driver_assign_response.assigned_driver_id)
driver_deliveries_response = delivery_stub.GetAssignedDeliveries(driver_deliveries_request)
print(f"Driver {driver_assign_response.assigned_driver_id} Assigned Deliveries:")
for delivery in driver_deliveries_response.deliveries:
    print(f"   - Order ID: {delivery.order_id}, Status: {delivery.order_status}")

print(".....................................")
print(".....................................")

#Test delivery driver updating delivery status of order
print("Testing delivery driver updating delivery status")
delivery_update_request = delivery_pb2.DeliveryStatusUpdateRequest(assigned_order_id = order_response.generated_order_id, delivery_status = "Order Delivered")
delivery_update_response = delivery_stub.UpdateStatus(delivery_update_request)
print(f"Delivery status updated: {delivery_update_response.update_successful}")

print(".....................................")
print(".....................................")