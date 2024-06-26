# ESDBank
An web application that aims to mimic a bank online service. It caters to three scenarios:
1. Payment transfers between different users of the app
2. Splitting share bills between users 
3. An AI powered chatbot to provide advice on users' spending

## Setup

1. Clone the repository to your local machine.

2. Install the required Python modules by running:

   ```bash
   pip install -r requirements.txt

To run each microservice locally:

Open a terminal window and navigate to the directory "cd microservices"

Run the command "docker run -d --hostname esd-rabbit --name rabbitmq-mgmt -p 5672:5672 -p 15672:15672 rabbitmq:3-management"

Run the amqp_setup.py

Run the Python script for each microservice.

Once all microservices are running, you can access the application at http://localhost:4999/login.

Then login to jakoblwr@gmail.com , and wait for it to initalize.

# Links
Git Repo: https://github.com/raellusionz/ESDBank <br>
Youtube Demostration of user scernario: https://www.youtube.com/watch?v=p2Aaqf0ydKA

# Tech Stacks
Front end:
- HTML
- CSS
- Javascript
- Frameworks
  - Bootstrap
  - Vue.js

Back end:


