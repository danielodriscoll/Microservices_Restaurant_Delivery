setup:
cd A1
source venv/bin/activate

RUN MICROSERVICES MANUALLY:
- open new terminal window for each command
python services/order_service.py
python services/restaurant_service.py
python services/payment_service.py
python services/delivery_service.py
python services/fastapi_bonus.py

RUN MICROSERVICES using docker-compose:
docker compose up --build -d

RUN UNIT TESTS (works on either of the above just enure compose is down for manual method):
python clients/test_client.py 


INTERACT WITH API GATEWAY (BONUS CAHLLENGE):
- Can view menus from Restaurant1, 2 or 3
curl -X GET "http://localhost:8000/menu/Restaurant1"

- Place order with your name and chosen restaurant1, 2 or 3
curl -X POST "http://localhost:8000/order?buyer_id=Daniel&vendor_id=Restaurant1"

- Check order status, (use correct order number from response of previous command)
curl -X GET "http://localhost:8000/order/ORD1234/status"

-Assign a driver to the Order ( use correct number):
curl -X POST "http://localhost:8000/delivery/assign?order_id=ORD1234"

-Update delivery status (user order number):
curl -X PUT "http://localhost:8000/delivery/ORD1234/status?status=DELIVERED"

-Process payment use name and order number:
curl -X POST "http://localhost:8000/payment?payer_id=Daniel&order_id=ORD1234&amount=25.0&method=credit_card"

-CHeck payment status:
curl -X GET "http://localhost:8000/payment/ORD1234/status"

##### A2 ######
Part1

# Build and push Docker images to Docker Hub
docker build -t dodriscoll4/order-service:latest -f docker/order.Dockerfile .
docker push dodriscoll4/order-service:latest

docker build -t dodriscoll4/restaurant-service:latest -f docker/restaurant.Dockerfile .
docker push dodriscoll4/restaurant-service:latest

docker build -t dodriscoll4/payment-service:latest -f docker/payment.Dockerfile .
docker push dodriscoll4/payment-service:latest

docker build -t dodriscoll4/delivery-service:latest -f docker/delivery.Dockerfile .
docker push dodriscoll4/delivery-service:latest

docker build -t dodriscoll4/fastapi-bonus:latest -f docker/fastapi.Dockerfile .
docker push dodriscoll4/fastapi-bonus:latest

# Deploy all services to Kubernetes
sudo k3s kubectl apply -f kubernetes/order-deploy.yaml
sudo k3s kubectl apply -f kubernetes/order-svc.yaml

sudo k3s kubectl apply -f kubernetes/restaurant-deploy.yaml
sudo k3s kubectl apply -f kubernetes/restaurant-svc.yaml

sudo k3s kubectl apply -f kubernetes/payment-deploy.yaml
sudo k3s kubectl apply -f kubernetes/payment-svc.yaml

sudo k3s kubectl apply -f kubernetes/delivery-deploy.yaml
sudo k3s kubectl apply -f kubernetes/delivery-svc.yaml

sudo k3s kubectl apply -f kubernetes/fastapi-deploy.yaml
sudo k3s kubectl apply -f kubernetes/fastapi-svc.yaml

# Check pod status
sudo k3s kubectl get pods
sudo k3s kubectl get services


Part2 - functional

Functional Testing with Postman
Test endpoints through Postman GUI or Newman
Test collection includes menu retrieval, order placement, and status tracking
See  video

part 2 - non functional

# Download and install Gatling
cd ~/
wget https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.9.5/gatling-charts-highcharts-bundle-3.9.5-bundle.zip
unzip gatling-charts-highcharts-bundle-3.9.5-bundle.zip
mv gatling-charts-highcharts-bundle-3.9.5 gatling

# Create test script
cd ~/gatling/user-files/simulations/
nano FoodDeliveryTest.scala
See food service scal file in gatling dircetory

# Run Gatling test
cd ~/gatling
./bin/gatling.sh
# Select FoodDeliveryTest from menu

part2 - kubernetes investigation

# Create ConfigMap
sudo k3s kubectl apply -f kubernetes/configmap.yaml

# View ConfigMap details
sudo k3s kubectl get configmap fastapi-settings -o yaml

# Test ConfigMap with demo deployment
sudo k3s kubectl apply -f kubernetes/test-config-deploy.yaml

# Verify environment variables
sudo k3s kubectl exec -it $(sudo k3s kubectl get pod -l app=test-config -o jsonpath='{.items[0].metadata.name}') -- printenv | grep -E "DEBUG_MODE|LOG_LEVEL"

# Cleanup
sudo k3s kubectl delete -f kubernetes/test-config-deploy.yaml
sudo k3s kubectl delete configmap fastapi-settings


part 3:

FUNCTION check_restaurant_offerings(event_payload):
   BEGIN
       // Input: Restaurant offering details
       offering_details = parse_json(event_payload)
       establishment_id = offering_details["establishment_id"]
       dish_listings = offering_details["dish_listings"]
       
       // Processing: Verify dish listings
       verification_outcomes = []
       
       FOR EACH dish IN dish_listings:
           outcome = {
               "dish_title": dish["title"],
               "is_valid": true,
               "issues": []
           }
           
           // Verify required attributes
           IF dish["title"] is_blank:
               outcome["is_valid"] = false
               outcome["issues"].add("Title is compulsory")
           
           IF dish["cost"] <= 0:
               outcome["is_valid"] = false
               outcome["issues"].add("Cost must be greater than zero")
           
           // Verify for repeated dishes
           IF dish["title"] appears_elsewhere:
               outcome["is_valid"] = false
               outcome["issues"].add("Repeated dish title")
           
           verification_outcomes.add(outcome)
       
       // Produce summary
       approved_dishes_count = tally_approved_dishes(verification_outcomes)
       overall_dishes = length(dish_listings)
       
       // Output: Verification summary
       RETURN {
           "establishment_id": establishment_id,
           "overall_dishes": overall_dishes,
           "approved_dishes": approved_dishes_count,
           "verification_outcomes": verification_outcomes,
           "fully_approved": (approved_dishes_count == overall_dishes),
           "verification_timestamp": current_timestamp()
       }
   END








