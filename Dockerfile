FROM python:3.11.4
COPY requirements.txt app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install requests

COPY . /app
EXPOSE 8080

CMD ["python", "main.py"]