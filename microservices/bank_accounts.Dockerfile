FROM python:3.8-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./bank_accounts.py ./invokes.py ./.env.development.local ./
CMD [ "python", "./bank_accounts.py" ]