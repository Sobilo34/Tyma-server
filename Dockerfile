FROM python:3.12-slim
RUN apt-get update && apt-get install -y build-essential
RUN apt-get update && apt-get install -y libpq-dev
RUN pip install google-api-python-client google-cloud-storage

RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-deps


COPY . .
COPY /build.sh .
ENTRYPOINT [ "sh", "build.sh" ]
