import os

from slack_sdk import WebClient

from mysql_config import create_session
from queuer import q, nq, dq, resetq, credits, blame

commands = {
    "q?": q,
    "nq": nq,
    "dq": dq,
    "blame": blame,
    "resetq": resetq,
    "faq": credits,
    "help": credits,
    "credits": credits,
}


def on_mention(event_user, event_text, event_channel, client):
    with create_session() as session:
        slack_user = f"<@{event_user}>"
        _, command, *message = event_text.split(" ")
        message = " ".join(message)
        print(f"Running command {command}")
        if command not in commands:
            txt = f"I dont know what should I do when you are saying `{command}` :confused:"
        else:
            txt = commands[command](session, slack_user, message, event_channel)
        print(txt)
        session.commit()
    if os.getenv("STAGE") == "dev":
        response = client.chat_postMessage(
            channel=event_channel,
            text=txt
        )
    else:
        print(f"Sending {txt} to {event_channel}")
