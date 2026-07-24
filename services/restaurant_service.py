import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pb2'))

import grpc
from concurrent import futures
import restaurant_pb2, restaurant_pb2_grpc

#these are acting like local databases for me, ideally mysql should be used as 
#restaurant DB, but that wasn't the bonus challenge I chose
restaurants_menus = {
    "Restaurant1": [
        {"dish_name": "Burger", "dish_description": "Cheese burger with bacon", "dish_price": 15},
        {"dish_name": "Pizza", "dish_description": "Pepperoni pizza with extra cheese", "dish_price": 12},
        {"dish_name": "Fries", "dish_description": "Crispy seasoned fries", "dish_price": 5},
        {"dish_name": "Coke", "dish_description": "Chilled Coca-Cola", "dish_price": 3},
        {"dish_name": "Milkshake", "dish_description": "Vanilla milkshake with whipped cream", "dish_price": 6}
    ],
    "Restaurant2": [
        {"dish_name": "Pasta", "dish_description": "Creamy alfredo pasta", "dish_price": 10},
        {"dish_name": "Salad", "dish_description": "Fresh garden salad", "dish_price": 8},
        {"dish_name": "Garlic Bread", "dish_description": "Toasted garlic bread with herbs", "dish_price": 4},
        {"dish_name": "Lemonade", "dish_description": "Homemade refreshing lemonade", "dish_price": 3},
        {"dish_name": "Iced Tea", "dish_description": "Chilled sweet iced tea", "dish_price": 4}
    ],
    "Restaurant3": [
        {"dish_name": "Steak", "dish_description": "Grilled sirloin steak with garlic butter", "dish_price": 20},
        {"dish_name": "Sushi", "dish_description": "Fresh salmon and tuna sushi platter", "dish_price": 18},
        {"dish_name": "Miso Soup", "dish_description": "Traditional Japanese miso soup", "dish_price": 5},
        {"dish_name": "Green Tea", "dish_description": "Hot Japanese green tea", "dish_price": 2},
        {"dish_name": "Sake", "dish_description": "Authentic Japanese rice wine", "dish_price": 10}
    ]
}

class RestaurantServiceServer(restaurant_pb2_grpc.RestaurantServiceServicer):

    #gets menu of choesen restaurant, 1, 2, 3 loops through menu items and adds them to the response
    def GetRestaurantsMenu(self, request, context):
        print(f"Fetching menu of restaurant: {request.restaurant_unique_id}")
        menu_items = restaurants_menus.get(request.restaurant_unique_id, [])
        
        response = restaurant_pb2.RestaurantMenuResponse(restaurant_unique_id=request.restaurant_unique_id)
        
        for item in menu_items:
            menu_entry = response.available_menu_items.add()  
            menu_entry.dish_name = item["dish_name"]
            menu_entry.dish_description = item["dish_description"]
            menu_entry.dish_price = item["dish_price"]
        
        return response


    #recieve new menu and overwrite the old one, return confirmation mesage
    def UpdateRestaurantsMenu(self, request, context):
        print(f"Updating menu for restaurant: {request.restaurant_unique_id}")
        updated_menu_items = []
        for item in request.updated_menu_items:
            updated_menu_items.append({
                "dish_name": item.dish_name,
                "dish_description": item.dish_description,
                "dish_price": item.dish_price
            })
        
        restaurants_menus[request.restaurant_unique_id] = updated_menu_items
        
        return restaurant_pb2.UpdateRestaurantMenuResponse(update_successful=True)

    #recieve order decision, accepted or rejected and print it with order id
    def OrderAcceptanceStatus(self, request, context):
        print(f"Restaurant Order Status: {request.order_tracking_id}: {'Accepted' if request.is_accepted else 'Rejected'}")
        
        return restaurant_pb2.OrderDecisionStatusResponse(decision_confirmed=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServiceServicer_to_server(RestaurantServiceServer(), server)
    server.add_insecure_port("[::]:50055")
    print("Restaurant Server is running on port 50055")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
