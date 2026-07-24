import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))
import grpc
from concurrent import futures
import payment_pb2, payment_pb2_grpc



#these are acting like local databases for me, ideally mysql should be used as 
#payment DB, but that wasn't the bonus challenge I chose
payments = {}

class PaymentServiceServer(payment_pb2_grpc.PaymentServiceServicer):

    #generate payment id and store payemnet info in DB
    def ProcessPayment(self, request, context):
        transaction_id = "TXN" + str(len(payments) + 1)  # Generate a simple transaction ID
        payments[transaction_id] = {
            "order_id": request.associated_order_id,
            "amount": request.transaction_amount,
            "status": "COMPLETED"
        }
        print(f"Processed Payment: Order {request.associated_order_id}, Amount: {request.transaction_amount}, Transaction ID: {transaction_id}")
        return payment_pb2.ProcessPaymentResponse(payment_successful=True, generated_transaction_id=transaction_id)

    #get payment info based off order id
    def GetPaymentStatus(self, request, context):
        for transaction_id, details in payments.items():
            if details["order_id"] == request.order_id:
                print(f"Retrieving Payment Status: Order {request.order_id}, Status: {details['status']}")
                return payment_pb2.GetPaymentStatusResponse(payment_status=details["status"], transaction_id=transaction_id)
        print(f"Payment not found for Order {request.order_id}")
        return payment_pb2.GetPaymentStatusResponse(payment_status="NOT_FOUND", transaction_id="")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    payment_pb2_grpc.add_PaymentServiceServicer_to_server(PaymentServiceServer(), server)
    server.add_insecure_port("[::]:50056")
    print("Payment Server is running on port 50056")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
