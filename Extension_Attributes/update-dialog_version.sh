#!/bin/zsh

#### INSERT ORG NAME HERE ####
org=""

## Get the installed version of the swiftDialog based app update framework
scriptPath="/opt/$org/tools/appUpdates.py"
pythonPath="/opt/$org/bin/python3"

if [[ $pythonPath ]] && [[ $scriptPath ]]; then
	version="$($pythonPath $scriptPath --version)"
else
	version="Not Installed"
fi

echo "<result>$version</result>"