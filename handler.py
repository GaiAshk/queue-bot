import base64
import boto3
import json
import os

from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

kms = boto3.client('kms', region_name="us-east-1")


def decrypt(v):
    if os.getenv("STAGE") != "dev":
        return v

    encrypted_value = base64.b64decode(v)
    result = kms.decrypt(CiphertextBlob=encrypted_value)
    return result['Plaintext'].decode()


SLACK_APP_TOKEN = decrypt(os.environ["SLACK_APP_TOKEN"])
SLACK_BOT_TOKEN = decrypt(os.environ["SLACK_BOT_TOKEN"])
client = WebClient(token=SLACK_BOT_TOKEN)
os.environ["MYSQL_PASSWORD"] = decrypt(os.environ["MYSQL_PASSWORD"])

from mention_manager import on_mention

signature_verifier = SignatureVerifier(decrypt(os.environ["SLACK_SIGNING_SECRET"]))


def lambda_handler(event, context):
    # Verify the request is from Slack
    try:
        if not signature_verifier.is_valid_request(event.get("body"), event.get("headers")):
            raise "Invalid request error"
    except Exception as e:
        print(str(e))
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    # Parse the event data
    event_data = json.loads(event.get("body"))
    if event_data.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "body": json.dumps({"challenge": event_data.get("challenge")})
        }
    elif event_data.get("type") == "event_callback":
        event_type = event_data.get("event").get("type")
        event_text = event_data.get("event").get("text")
        event_user = event_data.get("event").get("user")
        event_channel = event_data.get("event").get("channel")
        if event_type == "app_mention":
            on_mention(event_user, event_text, event_channel, client)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event processed successfully"})
    }
