FROM python:latest
LABEL authors="harry"

#RUN apt update -y
#RUN apt install python3 python3-pip -y

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

RUN python3 create_database.py

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0", "wsgi:app"]