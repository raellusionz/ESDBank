FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./error.py ./amqp_connection.py ./
CMD [ "python", "./error.py" ]