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

### 2.1 Install ChromeDriver (for crawling rendered HTML)
The crawler uses Selenium with Google Chrome. Install ChromeDriver and make sure it is in your `PATH`.

- macOS (Homebrew):
```commandline
brew install chromedriver
```

- macOS (manual):
  1) Download from https://googlechromelabs.github.io/chrome-for-testing/
  2) Unzip and move `chromedriver` to `/usr/local/bin`
  3) Ensure it is executable: `chmod +x /usr/local/bin/chromedriver`

- Windows:
  1) Download from https://googlechromelabs.github.io/chrome-for-testing/
  2) Unzip and add the folder to the System `PATH`

- Linux (Debian/Ubuntu):
```commandline
sudo apt-get update
sudo apt-get install -y chromium-chromedriver
```

Verify installation:
```commandline
chromedriver --version
```

If you prefer not to add ChromeDriver to `PATH`, place it in the project folder and pass the path:
```commandline
python crawl_students.py --url http://127.0.0.1:8000 --driver-path ./chromedriver-mac-arm64/chromedriver --output students_clean.csv
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
