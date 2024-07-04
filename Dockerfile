FROM python:3.9-slim
WORKDIR /app/src
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD [ "python", "main.py" ]
