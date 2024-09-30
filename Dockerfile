# FROM python:3.10.11-alpine3.18
FROM --platform=linux/amd64 python:3.10-slim AS build_amd64

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y build-essential python3-dev libffi-dev
# RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt --break-system-packages
RUN pip install --upgrade pip
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]