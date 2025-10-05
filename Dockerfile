FROM python:3-alpine3.21
WORKDIR /ccp
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5001
CMD python ./webserver.py
