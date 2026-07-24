import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))

import grpc
import random
from concurrent import futures
import order_pb2, order_pb2_grpc


#these are acting like local databases for me, ideally mysql should be used as 
#order DB, but that wasn't the bonus challenge I chose
orders = {}

class OrderServiceServer(order_pb2_grpc.OrderServiceServicer):

    #genreate random order number, keep looping if order already exists, store order in DB
    def MakeOrder(self, request, context):
        order_id = "ORD" + str(random.randint(1000, 9999))
        while order_id in orders:
            order_id = "ORD" + str(random.randint(1000, 9999))
        orders[order_id] = {"buyer_id": request.buyer_id, "vendor_id": request.vendor_id, "status": "Pending"}
        print(f"Order received from {request.buyer_id} for restaurant {request.vendor_id} -> Order ID: {order_id}")

        return order_pb2.MakeOrderResponse(generated_order_id=order_id, order_confirmation_status="Confirmed")

    #look up order in db and  get its status
    def GetOrderStatus(self, request, context):
        status = orders.get(request.tracking_order_id, {}).get("status", "Unknown")
        print(f"Retrieving Order Status for {request.tracking_order_id} -> {status}")
        
        return order_pb2.GetOrderStatusResponse(tracking_order_id=request.tracking_order_id, order_progress_status=status)

    #check if order exists in local db and update status
    def UpdatedOrderStatus(self, request, context):
        if request.tracking_order_id in orders:
            orders[request.tracking_order_id]["status"] = request.current_status
            print(f"Updated Order Status: {request.tracking_order_id} -> {request.current_status}")
            return order_pb2.UpdatedOrderResponse(tracking_order_id=request.tracking_order_id, latest_status=request.current_status)
        
        return order_pb2.UpdatedOrderResponse(tracking_order_id=request.tracking_order_id, latest_status="Unknown Order")

    # chek if order exists
    def CheckOrderIsPresent(self, request, context):
        exists = request.order_id in orders
        print(f"Checking if order {request.order_id} exists: {exists}")
        return order_pb2.CheckOrderIsPresentResponse(order_isPresent=exists)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServer(), server)
    server.add_insecure_port("[::]:50051")
    print("Order Server is running on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
