FROM python:3.8-slim

WORKDIR /usr/src/app

# Copy the script and dependencies
COPY amqp_setup.py .
COPY http.reqs.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r http.reqs.txt

# Run the setup script
CMD ["python", "amqp_setup.py"]