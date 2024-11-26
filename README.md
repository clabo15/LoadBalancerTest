# Load Balancing with NGINX and FastAPI

## Introduction

A **load balancer** is a critical component in distributed systems, designed to evenly distribute incoming network traffic across multiple servers. By doing so, it ensures:

1. **High availability**: If one server goes down, the load balancer reroutes traffic to other healthy servers.
2. **Scalability**: Handles increased traffic by distributing it across multiple instances.
3. **Performance**: Balances load, preventing individual servers from being overwhelmed.
4. **Fault tolerance**: Improves system reliability by isolating and handling failing components.

This project demonstrates a simple implementation of a load balancer using **NGINX** to route requests to two instances of a **FastAPI** application.

---

## Project Structure

```
LoadBalancerTest/
|__app/
     |__Dockerfile
     |__main.py
|__nginx/
     |__default.conf
|__docker-compose.yml
```

Each file in the project serves a specific purpose:

- **Dockerfile**: Defines how to containerize the FastAPI app.
- **main.py**: Implements the FastAPI application.
- **default.conf**: Configures NGINX as a load balancer.
- **docker-compose.yml**: Orchestrates the multi-container environment.

---

## File Explanations

### **Dockerfile**

The `Dockerfile` is used to create a containerized environment for the FastAPI app.

```dockerfile
# Use Python 3.12-slim as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local app code into the container
COPY . .

# Install required Python packages (FastAPI and Uvicorn)
RUN pip install fastapi uvicorn

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **main.py**

The `main.py` file defines the FastAPI application.

```python
from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI", "hostname": socket.gethostname()}
```

- **Purpose**: 
  - The app responds to HTTP GET requests at the root (`/`) endpoint.
  - Returns the container's **hostname**, allowing us to verify which instance handled the request.
  
### **default.conf**

The `default.conf` file contains the NGINX configuration to act as a load balancer.

```nginx
upstream fastapi_app {
    server app1:8000;
    server app2:8000;
}

server {
    listen 80;

    location / {
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Key Sections:

1. **Upstream Block**:
   - Defines the `fastapi_app` backend consisting of two servers (`app1` and `app2`), both running on port `8000`.
   - NGINX will load balance traffic between these servers.

2. **Server Block**:
   - **listen 80**: Configures the server to listen on port `80`.
   - **location /**: Matches all requests to the root path.
     - **proxy_pass http://fastapi_app**: Forwards requests to the upstream block (`fastapi_app`).
     - **proxy_set_header directives**:
       - Forward additional client information (e.g., IP address, protocol) to the backend servers.

---

### **docker-compose.yml**

This file orchestrates the deployment of all components using Docker Compose.

```yaml
services:
  app1:
    build: ./app
    container_name: app1
    expose:
      - "8000"
    networks:
      - app_network

  app2:
    build: ./app
    container_name: app2
    expose:
      - "8000"
    networks:
      - app_network

  nginx:
    image: nginx:latest
    container_name: nginx_lb
    ports:
      - "8080:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app1
      - app2
    networks:
      - app_network

networks:
  app_network:
    driver: bridge
```

#### Key Sections:

1. **Services**:
   - **app1** and **app2**:
     - Build the FastAPI application from the `app` folder using the `Dockerfile`.
     - Expose port `8000` for communication within the internal network (`app_network`).
   - **nginx**:
     - Uses the official `nginx:latest` image to create the load balancer.
     - Maps host port `8080` to container port `80` for external access.
     - Mounts the local `default.conf` file as the NGINX configuration.

2. **Networks**:
   - Defines a `bridge` network named `app_network` for communication between containers.

3. **depends_on**:
   - Ensures the NGINX service starts only after `app1` and `app2` are running.

---

## Running the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/clabo15/LoadBalancerTest.git
   cd LoadBalancerTest
   ```

2. **Start the containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Open a browser or use a tool like `curl` to navigate to `http://localhost:8080`.
   - Each request will be handled by either `app1` or `app2`, as identified by the `hostname` in the response.

4. **Test Load Balancing**:
   - Refresh the page multiple times to observe different responses as NGINX distributes the requests between `app1` and `app2`.

---

## Key Takeaways

1. **NGINX as a Load Balancer**:
   - Simple to configure using an `upstream` block.
   - Easily integrates with Dockerized applications.

2. **Docker Compose**:
   - Simplifies multi-container setups by orchestrating networking, dependencies, and configuration.

3. **Scalability**:
   - Adding more instances is as simple as defining additional services (e.g., `app3`) in the `docker-compose.yml` and adding them to the `upstream` block.
