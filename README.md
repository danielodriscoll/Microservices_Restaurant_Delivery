<<<<<<< HEAD
setup:
cd A1
source venv/bin/activate

RUN MICROSERVICES MANUALLY:
- open new terminal window for each command
=======
# Restaurant Microservices Platform

A food-ordering backend built as a set of independent Python microservices — **Order**, **Restaurant**, **Payment**, and **Delivery** — that talk to each other over **gRPC**, fronted by a **FastAPI** gateway that exposes a single REST API to clients. Built to practice service decomposition, protobuf contract design, and containerised deployment (Docker Compose locally, Kubernetes manifests for a cluster).

## Architecture

```mermaid
graph LR
    Client -->|HTTP/REST| Gateway["FastAPI Gateway :8000"]
    Gateway -->|gRPC| Order["Order Service :50051"]
    Gateway -->|gRPC| Restaurant["Restaurant Service :50055"]
    Gateway -->|gRPC| Payment["Payment Service :50056"]
    Gateway -->|gRPC| Delivery["Delivery Service :50053"]
    Delivery -->|gRPC: verify order exists| Order
```

- **API Gateway** (`services/fastapi_bonus.py`) — the only HTTP entry point. Translates REST calls into gRPC requests against the four backend services and returns JSON.
- **Order Service** — creates orders, tracks status, and answers "does this order exist?" checks from the Delivery service.
- **Restaurant Service** — serves and updates restaurant menus, records order accept/reject decisions.
- **Payment Service** — processes payments and reports payment status per order.
- **Delivery Service** — assigns a driver from a fixed pool, tracks delivery status, and calls back into the Order service via gRPC to confirm an order is valid before assigning it.

Each service is a standalone gRPC server with its own `.proto` contract (in `protos/`) and generated stubs (in `pb2/`), so any service can be developed, tested, or redeployed independently of the others.

## Tech Stack

- **Python** (3.9 in containers, 3.12 for local venv)
- **gRPC + Protocol Buffers** for inter-service contracts and communication
- **FastAPI** + **Uvicorn** for the REST gateway
- **Docker** / **Docker Compose** for local multi-container orchestration
- **Kubernetes** manifests for cluster deployment

## Project Layout

```
services/       gRPC servers + the FastAPI gateway
protos/         .proto contracts for each service
pb2/            generated gRPC/protobuf stubs
docker/         one Dockerfile per service
kubernetes/     Deployment + Service manifests per service
clients/        end-to-end test client
docker-compose.yml
```

## Getting Started

### Prerequisites
- Python 3.9+ and `pip`
- Docker & Docker Compose (for the containerised option)

### Option A — run locally in a virtualenv
```bash
git clone <this-repo-url>
cd restaurant-microservices-platform

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Then open five terminals (one per service) and run:
```bash
>>>>>>> dab0dcb5afe6ffac89f9d81d12ff85773d9422b4
python services/order_service.py
python services/restaurant_service.py
python services/payment_service.py
python services/delivery_service.py
python services/fastapi_bonus.py
<<<<<<< HEAD

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








=======
```

### Option B — run with Docker Compose (recommended)
```bash
docker compose up --build -d
```
This builds and starts all five services, with `wait-for-it.sh` making sure each service doesn't start until the Order service (which the others depend on) is reachable.

## Using the API

Once the gateway is up on `http://localhost:8000`, a typical order flow looks like:

**1. View a restaurant's menu**
```bash
curl -X GET "http://localhost:8000/menu/Restaurant1"
```

**2. Place an order**
```bash
curl -X POST "http://localhost:8000/order?buyer_id=Daniel&vendor_id=Restaurant1"
```

**3. Check order status** (use the `order_id` returned above)
```bash
curl -X GET "http://localhost:8000/order/ORD1234/status"
```

**4. Assign a driver**
```bash
curl -X POST "http://localhost:8000/delivery/assign?order_id=ORD1234"
```

**5. Update delivery status**
```bash
curl -X PUT "http://localhost:8000/delivery/ORD1234/status?status=DELIVERED"
```

**6. Pay for the order**
```bash
curl -X POST "http://localhost:8000/payment?payer_id=Daniel&order_id=ORD1234&amount=25.0&method=credit_card"
```

**7. Check payment status**
```bash
curl -X GET "http://localhost:8000/payment/ORD1234/status"
```

## Running the Test Client

`clients/test_client.py` drives the full order → payment → delivery lifecycle straight over gRPC (bypassing the REST gateway) and prints the result of each step — useful as a quick smoke test that every service is wired up correctly.

```bash
python clients/test_client.py
```
Works against either the manually-started services or the Docker Compose stack — it reads a `RUNNING_IN_DOCKER` environment variable to decide which hostnames to use.

## Kubernetes Deployment (optional)

Deployment + Service manifests for all five services are in `kubernetes/manifests/`. They currently reference pre-built images on Docker Hub, so to deploy to your own cluster, build and push your own images first and update the `image:` field in each `*-deploy.yml` accordingly:

```bash
docker build -t <your-registry>/order-service:latest -f docker/order.Dockerfile .
docker push <your-registry>/order-service:latest
# ...repeat for restaurant, payment, delivery, fastapi-bonus

kubectl apply -f kubernetes/manifests/
```

## Metrics (optional)

The gateway pushes basic response-time metrics for each endpoint to a Graphite listener on `localhost:2003` (Carbon plaintext protocol). This is best-effort: if nothing is listening on that port, the send silently no-ops and the request still completes normally.

## Design Notes & Limitations

This project prioritises demonstrating clean service boundaries and gRPC contracts over production-readiness. Worth knowing going in:

- **In-memory storage** — each service keeps its state in a plain Python dict, so data is lost on restart. A production version would give each service its own database, in keeping with the microservices principle of independent data ownership.
- **No auth or TLS** — gRPC channels are insecure and the REST gateway has no auth layer; fine for local development, not something to expose publicly as-is.
- **Random driver assignment** — the Delivery service picks a driver at random from a fixed pool of three, as a stand-in for real dispatch logic.

## Possible Next Steps

- Persistent storage per service (e.g. Postgres per service, or SQLite for a lighter first step)
- AuthN/AuthZ on the gateway
- Event-driven communication (e.g. RabbitMQ/Kafka) between services instead of synchronous gRPC calls where it makes sense (e.g. order-status change notifications)
- CI pipeline to build, test, and push images automatically on merge
>>>>>>> dab0dcb5afe6ffac89f9d81d12ff85773d9422b4
