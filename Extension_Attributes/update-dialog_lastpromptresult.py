#!/opt/chime/bin/python3

import json
from datetime import datetime
from pathlib import Path

#### INSERT ORG NAME HERE ####
org = ""

## Check the last run result to report what apps were prompted and if they were updated or deferred
lastRunFile = Path(f"/Library/Application Support/{org}/appUpdates/lastRun.json")
lastPromptResult = ''

## Get the app and result list for the last prompt run
if lastRunFile.exists():
	try:
		runData = json.loads(lastRunFile.read_text())
		lastPromptResultDict = runData.get('prompt').get('runResult')
		lastPromptRunResultList = [(x, lastPromptResultDict.get(x).get('result')) for x in lastPromptResultDict.keys()]

		for app, result in lastPromptRunResultList:
			lastPromptResult += f'{app}: {result}\n'

	except:
		lastPromptResult = ''
else:
	lastPromptResult = ''

## Print result
print(f'<result>{lastPromptResult.strip()}</result>')