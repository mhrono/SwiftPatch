#!/bin/zsh

## Get the installed version of the swiftDialog based app update framework

#### Insert the path to the update script on-device
scriptPath=""

## Set to the path of your python3 executable
pythonPath="/usr/bin/env python3"

if [[ $pythonPath ]] && [[ $scriptPath ]]; then
	version="$($pythonPath $scriptPath --version)"
else
	version="Not Installed"
fi

echo "<result>$version</result>"