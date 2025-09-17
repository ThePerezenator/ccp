FROM python:3-alpine3.21
WORKDIR /ccp
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python ./webserver.py
