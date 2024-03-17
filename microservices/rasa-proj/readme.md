readme for rasa-proj

to get started, change directory into rasa-proj, use command line:
$ cd rasa-proj

If you are on any python version above 3.10, please activate a virtual env for 3.10 and below (to 3.6).
// for mac users,
To create virtual env, use command line:
$ python3.10 -m venv venv

activate the vitual env, use command line:
source venv/bin/activate

-- after being in the correct correct env --
To run rasa, use command line:
$ rasa shell. 

If rasa says to train the model before running, use command line:
$ rasa train

After running rasa, run app.py under microservices folder and go to "http://127.0.0.1:5000/roboadvisor" to try out the chatbot

the chatbot is currently just a hi-bye service, currently working on userGoals microservice to create advice

To stop rasa:
use '/stop' to exit

To deactivate virtual env:
type 'deactivate' into command line