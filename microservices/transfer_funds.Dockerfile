FROM python:3.8-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./transfer_funds.py ./invokes.py ./amqp_connection.py ./.env.development.local ./
CMD [ "python", "./transfer_funds.py" ]