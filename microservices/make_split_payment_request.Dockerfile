FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./make_split_payment_request.py .
CMD [ "python", "./make_split_payment_request" ]