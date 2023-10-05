#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

#### INSERT ORG NAME HERE ####
org = ""

## Check the last run result to determine when the script last attempted to prompt the user
lastRunFile = Path(f"/Library/Application Support/{org}/appUpdates/lastRun.json")

## Get the epoch date for the last prompt run
if lastRunFile.exists():
	try:
		runData = json.loads(lastRunFile.read_text())
		lastPromptTimeEpoch = runData.get('prompt').get('runTime')
	except:
		lastPromptTimeEpoch = 0
else:
	lastPromptTimeEpoch = 0

## Convert to jamf extension attribute date format
lastPromptTime = datetime.utcfromtimestamp(lastPromptTimeEpoch)

## Print result
print(f'<result>{lastPromptTime}</result>')