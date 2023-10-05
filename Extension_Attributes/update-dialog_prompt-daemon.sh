#!/bin/zsh

#### INSERT ORG NAME HERE ####
org=""

## Get the StartInterval for the swiftDialog app update framework LaunchDaemon (prompt run)
## Additionally, make sure it's actually loaded
daemonFile="/Library/LaunchDaemons/com.$org.appUpdates.promptRun.plist"

if [[ -f "$daemonFile" ]]; then
	interval=$(defaults read "$daemonFile" StartInterval)
	launchctl load -w "$daemonFile"
else
	interval=0
fi

echo "<result>$interval</result>"