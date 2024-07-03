FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
USER 1000
CMD [ "python", "main.py" ]
