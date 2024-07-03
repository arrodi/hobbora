FROM python:3.9-slim
WORKDIR /usr/src
COPY src/requirements.txt ./
RUN pip install -r requirements.txt
USER 1000
CMD [ "python", "main.py" ]
