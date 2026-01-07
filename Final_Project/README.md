# PPR501_SP26_MSA36 Final Project

## Run in local

### 1. Create virtual environment

```commandline
source env/bin/activate
```

### 2. Install dependencies
Run the below command to download the dependencies.
```commandline
pip install -r requirements.txt
```

### 3. Run the application
To start the service let run the below command
```commandline
fastapi dev main.py
```
or

```commandline
uvicorn main:app
```

Server started at http://127.0.0.1:8000

Swagger UI at http://127.0.0.1:8000/docs

## Container

### 1. Build the image
To run the service as container

First, build the docker image
```commandline
docker build -t student-api .
```

### 2. Run the container
Second, run the image
```commandline
docker run -p 8000:8000 student-api
```

Note: This project is for educational purposes.