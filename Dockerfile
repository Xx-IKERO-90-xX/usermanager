FROM python:3

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5002

CMD ["python3", "app.py"]