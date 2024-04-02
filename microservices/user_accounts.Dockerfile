FROM python:3.8-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./user_accounts.py ./.env.development.local ./
CMD [ "python", "./user_accounts.py" ]