FROM python:3.8-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./notification.py ./amqp_connection.py ./email_functions.py ./
CMD [ "python", "./notification.py" ]