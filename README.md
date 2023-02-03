# queue-bot
A simple queue bot for developer deployments. Using AWS Function URL

## general
This project was created to make a simple queue Slack app or bot, the queue will keep trace of who is next in line 
to deploy his/her code.

## background
When working with a team that has 10+ developers, we ran into a problem of keeping track who will deploy next.
We started by synchronizing by Slack messages, but this was too cumbersome. To automate this simple task I decided to 
create a Slack app that will integrate in our Slack channels and keep trace of who is next in line for us.

The queue support the following features
1. enqueue - enter queue
2. dequeue - leave queue 
3. blame - who is being blocking the queue for longest
4. informing the next in line it is his turn to deploy 
5. help - supported operations


## installation
Python 3.9

`
python -m venv venv
source venv/bin/activate
python -m pip install -r requierments.txt
`

## resources 
1. AWS lambda function (lambda function url)
2. AWS RDS
