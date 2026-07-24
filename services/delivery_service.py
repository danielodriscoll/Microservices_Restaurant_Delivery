import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))

import grpc
import random
from concurrent import futures
import delivery_pb2, delivery_pb2_grpc
import order_pb2, order_pb2_grpc


#these are acting like local databases for me, ideally mysql should be used as 
#delivery DB, but that wasn't the bonus challenge I chose
deliveries = {}
assigned_drivers = {}
driver_pool = ["Driver01", "Driver02", "Driver03"]

class DeliveryServiceServer(delivery_pb2_grpc.DeliveryServiceServicer):

    #allow sme to call order service functionality through grpc
    def __init__(self):
        RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
        ORDER_SERVICE_HOST = "order_service" if RUNNING_IN_DOCKER else "localhost"
        self.order_channel = grpc.insecure_channel(f"{ORDER_SERVICE_HOST}:50051")
        self.order_stub = order_pb2_grpc.OrderServiceStub(self.order_channel)
    #check order exists, if it does assign random driver from db and set order status
    def AssignDriver(self, request, context):
        check_request = order_pb2.CheckOrderIsPresentRequest(order_id=request.assigned_order_id)
        check_response = self.order_stub.CheckOrderIsPresent(check_request)

        if not check_response.order_isPresent:
            print(f"Error: Order {request.assigned_order_id} does not exist.")
            return delivery_pb2.DriverAssignmentResponse(assigned_driver_id="", assigned_vehicle="")
        
        assigned_driver = random.choice(driver_pool)
        assigned_drivers[request.assigned_order_id] = assigned_driver
        deliveries[request.assigned_order_id] = {"status": "PENDING_PICKUP", "driver_id": assigned_driver}
        print(f"Assigned Driver: {assigned_driver} for Order: {request.assigned_order_id}")
        
        return delivery_pb2.DriverAssignmentResponse(assigned_driver_id=assigned_driver, assigned_vehicle="Van")

    #update teh delivery status of an order
    def UpdateStatus(self, request, context):
        if request.assigned_order_id in deliveries:
            deliveries[request.assigned_order_id]["status"] = request.delivery_status
            print(f"Updated Status for Order: {request.assigned_order_id} -> {request.delivery_status}")
            return delivery_pb2.DeliveryStatusUpdateResponse(update_successful=True)
        
        print(f"Error: Order {request.assigned_order_id} not found in deliveries.")
        return delivery_pb2.DeliveryStatusUpdateResponse(update_successful=False)

    # get current status of an order
    def GetStatus(self, request, context):
        status = deliveries.get(request.assigned_order_id, {}).get("status", "UNKNOWN")
        print(f"Retrieving Status for Order: {request.assigned_order_id} -> {status}")
        
        return delivery_pb2.DeliveryStatusResponse(assigned_order_id=request.assigned_order_id, delivery_status=status)

    #get all deliveries a driver has
    def GetAssignedDeliveries(self, request, context):
        driver_deliveries = []
        for order_id, data in deliveries.items():
            if data["driver_id"] == request.driver_id:
                driver_deliveries.append(delivery_pb2.DeliveryInfo(order_id=order_id, order_status=data["status"]))
        print(f"Deliveries assigned to Driver {request.driver_id}: {driver_deliveries}")
        
        return delivery_pb2.DriverDeliveriesResponse(deliveries=driver_deliveries)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    delivery_pb2_grpc.add_DeliveryServiceServicer_to_server(DeliveryServiceServer(), server)
    server.add_insecure_port("[::]:50053")
    print("Delivery Server is running on port 50053")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
