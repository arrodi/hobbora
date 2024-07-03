FROM python:3.9-slim
WORKDIR /app
COPY src/requirements.txt ./
RUN pip install -r requirements.txt
COPY src
EXPOSE 8080
CMD [ "python", "main.py" ]