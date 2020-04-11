'''
This function handles a Slack slash command and echoes the details back to the user.

Follow these steps to configure the slash command in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Slash Commands".

  3. Enter a name for your command and click "Add Slash Command Integration".

  4. Copy the token string from the integration settings and use it in the next section.

  5. After you complete this blueprint, enter the provided API endpoint URL in the URL field.


Follow these steps to complete the configuration of your command API endpoint

  1. When completing the blueprint configuration select "Open" for security
     on the "Configure triggers" page.

  2. Enter a name for your execution role in the "Role name" field.

  3. Update the URL for your Slack slash command with the invocation URL for the
     created API resource in the prod stage.
'''
import json
import logging
import os
import urllib.request
import locale
import boto3

from base64 import b64decode
from urllib.parse import parse_qs

logger = logging.getLogger()
logger.setLevel(logging.INFO)
locale.setlocale( locale.LC_ALL, '' )

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def is_request_valid(params):
    is_token_valid = params['token'][0] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = params['team_id'][0] == os.environ['SLACK_TEAM_ID']
    return is_token_valid and is_team_id_valid

def createResponse():
    response = {}
    response["response_type"] = "in_channel"
    response["blocks"] = []
    return response

def addLine(response, message):
    block = { "type": "section", "text": {"type": "mrkdwn", "text": message} }
    response["blocks"].append(block)

def handleTifo():
    response = createResponse()
    addLine(response, "*Scheduled tifo dates include*")
    return respond(None, response)

def handlePrideraiser():    
    campaignURL = "https://www.prideraiser.org/api/campaigns/{0}/".format(os.environ['PRIDERAISER_CAMPAIGN_ID'])
    contents = urllib.request.urlopen(campaignURL).read()
    data = json.loads(contents)

    response = createResponse()
    addLine(response, "*Live Prideraiser data for NGS:*")
    addLine(response, "*Number of pledges:* {0}".format(data["pledge_count"]))
    per_goal = locale.currency(data["pledged_total"], grouping=True)
    addLine(response, "*Pledged per goal:* {0}".format(per_goal))
    addLine(response, "*Goals scored:* {0}".format(data["goals_made"]))
    total_amount = locale.currency(data["aggregate_pledged"], grouping=True)
    addLine(response, "*Total amount:* {0}".format(total_amount))
    additional_contributions = locale.currency(data["additional_contributions"], grouping=True)
    addLine(response, "*Additional partner contributions:* {0}".format(additional_contributions))
    aggregate_amount_raised = locale.currency(data["aggregate_amount_raised"], grouping=True)
    addLine(response, "*Grand total:* {0}".format(aggregate_amount_raised))
    
    return respond(None, response)

def handlePrideraiser2(response_url):
    #send an SNS message with the response_url to trigger the second handler
    client = boto3.client('sns')
    result = client.publish(TopicArn = os.environ['PRIDERAISER_SNS_TOPIC'], Message=response_url)


    response = createResponse()
    return respond(None, response)

def lambda_handler(event, context):    
    params = parse_qs(event['body'])

    if not is_request_valid(params):
        return respond({'message': 'Invalid token or team ID, please try again'})

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    if 'text' in params:
        command_text = params['text'][0]
    else:
        command_text = ''

    if command == "/ngstifo":
        return handleTifo()
    elif command == "/ngsprideraiser":
        return handlePrideraiser()
    elif command == "/ngsprideraiser2":
        response_url = params['response_url'][0]
        return handlePrideraiser2(response_url)
    return respond(None, {})