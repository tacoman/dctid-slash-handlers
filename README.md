# dctid-slash-handlers

I decided to mess around with AWS Lambda, and we wanted to get some slash commands in the DCTID Slack.

To run this, you need to create a Lambda function and put it behind an API Gateway, which the Slack slash command should be pointed to.
Check the source code of skellybot.py for info on using KMS to verify that requests are coming from Slack.