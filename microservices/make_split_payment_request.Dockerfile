FROM python:3.8-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./make_split_payment_request.py ./invokes.py ./amqp_connection.py ./.env.development.local ./
CMD [ "python", "./make_split_payment_request.py" ]