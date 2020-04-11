import json
import logging
import os
import urllib.request
import locale

from base64 import b64decode
from urllib.parse import parse_qs
from urllib.request import Request, urlopen

logger = logging.getLogger()
logger.setLevel(logging.INFO)
locale.setlocale( locale.LC_ALL, '' )

def createResponse():
    response = {}
    response["response_type"] = "in_channel"
    response["blocks"] = []
    return response

def addLine(response, message):
    block = { "type": "section", "text": {"type": "mrkdwn", "text": message} }
    response["blocks"].append(block)

def lambda_handler(event, context):    
    params = parse_qs(event['body'])
    response_url = params['response_url'][0]

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

