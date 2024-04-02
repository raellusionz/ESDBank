FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./group_details.py ./.env.development.local ./
CMD [ "python", "./group_details.py" ]