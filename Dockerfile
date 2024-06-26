FROM python:latest
LABEL authors="Harry James Hall"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY *.py .
COPY templates/ templates/

RUN groupadd -g 1000 appuser
RUN useradd -r -u 1000 -g appuser appuser
USER appuser

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0", "wsgi:app"]