# PPR501_SP26_MSA36 Final Project

Run the below command to download the dependencies.
```commandline
pip install -r requirements.txt
```

To start the service let run the below command
```commandline
fastapi dev main.py
```
or

```commandline
uvicorn main:app
```


docker build -t student-api .
docker run -p 8000:8000 student-api
