FROM python:3.9.6-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app

RUN python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]