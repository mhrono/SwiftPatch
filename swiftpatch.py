#!/usr/bin/env python3

"""
SwiftPatch

Author: Matt Hrono @ Chime | MacAdmins: @matt_h | mattonmacs.dev

----
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
----

Some elements and inspiration derived from
    - Tom Larkin's Auto-Update: https://github.com/t-lark/Auto-Update/ | Copyright 2019 Snowflake Inc.    | Apache 2.0 License
    - My fork of Auto-Update:   https://github.com/mhrono/Auto-Update/ | Copyright 2022 Buoy Health, Inc. | Apache 2.0 License
"""

"""
REQUIREMENTS:

    - swiftDialog: https://github.com/bartreardon/swiftDialog
		- Version 2.3.0 or higher
    - PyObjC -- I suggest the "recommended" flavor of MacAdmins Python: https://github.com/macadmins/python
		- This recommended Python package also includes any other modules this script requires
        - Be sure to update the shebang to point to your managed installation

NOTICE:
    - This script is intended to be used alongside AutoPkg, Jamf-Upload, and my non-standard jamf recipes available at https://github.com/mhrono/autopkg-recipes
    - While it may work with other workflows, platforms, or environments, it is not supported and I make no guarantees of functionality
    - You are, however, free to modify this script to suit your needs under the terms of the Apache 2.0 License detailed above
    
    - At a BARE MINIMUM, this script as written will expect configuration profiles in place containing all fields referenced within
    
ACKNOWLEDGEMENTS:
	I would be in remiss if I did not acknowledge a number of folks from MacAdmins Slack who have provided inspiration, pointers, and assistance while creating this workflow. In no particular order:
		- @tlark
		- @grahamrpugh
		- @nick.mcspadden
		- @bartreardon
		- @BigMacAdmin
		- @drtaru
		- @adamcodega
		- @dan-snelson
		- All the other fine folks in #autopkg, #python, #jamf-upload, and #swiftdialog
	Finally, thanks to the authors and commenters on an untold number of StackOverflow theads.
"""

"""
Use SwiftDialog to prompt users to update their apps

Version rollback functionality is not yet implemented. Some of the bits are already written, but no testing has been done and rollbacks are not expected to work.
"""

scriptVersion = "1.1.1"
requiredDialogVersionString = "2.3.0"
requiredDialogPattern = (
    "^(\d{2,}.*|[3-9].*|2\.\d{2,}.*|2\.[4-9].*|2\.3\.\d{2,}.*|2\.3\.[1-9].*|2\.3\.0.*)$"
)
requiredPythonVersionString = "3.10"
requiredPythonPattern = (
    "^(\d{2,}.*|[4-9].*|3\.\d{3,}.*|3\.[2-9]\d{1,}.*|3\.1[1-9].*|3\.10.*)$"
)
"""
CHANGELOG:

---- 1.0 RC1 | 2023-09-22 ----
First functional release

---- 1.0 RC2 | 2023-09-26 ----
Remove display of deferral data unless <= 3 remaining
Adjust dialog json options to make windows slightly more compact
Change macOS installed version logic to account for new major releases

---- 1.0 RC3 | 2023-10-04 ----
Add import for urllib.parse
Adjust pkgName variable assignment in monitorPolicyRun to account for HTML-encoded spaces in filenames

---- 1.0 | 2023-10-05 ----
First public release!

---- 1.0.1 | 2023-10-13 ----
Move run receipt update above inventory update in cleanup

---- 1.0.2 | 2023-10-18 ----
Remove unneeded warning logging for silent status update attempts
Fix path presence checking in getBinaryVersion
Added some error handling to getBinaryVersion
Fixed force tagging logic for silent updates

---- 1.0.3 | 2023-10-23 ----
Added step to unload existing LaunchDaemons before loading new ones
Changed run time in receipt to use UTC instead of device local time
Added RunAtLoad to setup LaunchDaemons

---- 1.0.4 | 2023-10-24 ----
Fixed issue with last run receipt checking

---- 1.1.0 | 2023-11-06 ----
POTENTIALLY BREAKING CHANGES
----------------------------
Setting preferences via configuration profile is now possible using the com.github.swiftpatch domain
Any NEW preference keys will be available via configuration profile, URL, or json file ONLY, with the exception of the new --selfservice option
NO additional command-line arguments will be added to support additional keys
All options are supported, and command-line arguments will continue to take precedence over other methods
For a list of available command-line arguments, run this script with --help
----------------------------
Now, on to the changes:
Updated description for --saveprefs argument to remind that configuration profiles take precedence
Added --selfservice argument to enable an ultralight single-app update interface
Added endRun function to consolidate script exit points and ensure consistency
Added support for preferences set by configuration profile
Added 'simple' option to remove the info box, icon, and instructions, creating a smaller and cleaner prompt interface
Added 'speedtest' option to enable or disable the download speed test (defaults to True, unless 'simple' is True)
Added 'position' option to configure where on the user's screen the prompt is generated
Added 'speechBalloon' emoji
Added check for existing dialog processes before continuing a run to avoid a potential race condition
Updated 'updateStatus' function to handle updates to 'selfservice' runs
Updated retrieval method for 'systemUptimeDays' in 'getDeviceHealth' to include time spent sleeping
Fixed copy in infobox uptime field to remove use the singular 'day' if 'systemUptimeDays == 1'
Fixed an issue in 'setDeferral' by adding an item to 'deferralIndexMap' to better handle randomized deferrals
Updated method for gathering installed update metadata profiles to enable case-insensitivity (and avoid potential issues when using '--selfservice')
Fixed version metadata being unintentionally included in 'dialogPromptList'
Added status overlay icons to dialog updates for a slightly richer UX
Updated time between download progress checks from 0.5 > 0.1 seconds, also for a slightly richer UX
Updated some copy and buttom labeling for both the prompt and status dialogs when using the default interface
Added copy and dialog parameters to prompt and status dialogs to support new simple interface
Fixed typo in 'parseUserSelections' function name
Added logic in 'run' to process 'selfservice' executions
Fixed lazy deferral checking in 'parseUserSelections' to only check app keys in 'promptOutput'
Other minor fixes throughout

---- 1.1.1 | 2023-11-13 ----
Fixed and reformatted arguments and prefsData processing (thanks @erchn!)
Fixed processing of --selfservice argument in multiple places
Removed a placeholder comment
Updated formatting with Black for improved readability (also thanks to @erchn)
Removed backticks from 1.1.0 release notes--look great on GitHub, behave rudely when writing this script to disk from a shell script
"""

##########################
##### Import Modules #####
##########################

import argparse
import json
import logging
import platform
import plistlib
import random
import re
import requests
import subprocess
import sys
import time
import urllib.parse

from AppKit import NSWorkspace
from Cocoa import NSRunningApplication
from datetime import datetime
from pathlib import Path
from shutil import disk_usage
from tempfile import NamedTemporaryFile

##########################

###################################################################################
###################### ---- DO NOT EDIT BELOW THIS LINE ---- ######################
###################################################################################

#### Parse Command Line Arguments and Set Default Values ####
parser = argparse.ArgumentParser(
    description="Control the behavior of this script",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    argument_default=argparse.SUPPRESS,
)
parser.add_argument(
    "--silent",
    action=argparse.BooleanOptionalAction,
    help="Determines whether or not the script runs silently or generates a prompt",
)
parser.add_argument(
    "--defer",
    action=argparse.BooleanOptionalAction,
    help="Identifies this run as triggered by a deferral. Useful for testing only, as the run timing will always evaluate as valid.",
)
parser.add_argument(
    "--selfservice",
    default="",
    const="",
    nargs="?",
    help="Enables an ultralight interface for updating a single app, generally from a Self Service item. Accepts a single argument for the display name of the app to be updated. This name must match the app's associated metadata configuration profile.",
)
parser.add_argument(
    "--org",
    nargs="?",
    help="Name of your org, used to create deferral and data directories",
)
parser.add_argument(
    "-d",
    "--dialog",
    nargs="?",
    type=Path,
    help="Full path to the dialog binary, if somewhere other than /usr/local/bin/dialog",
)
parser.add_argument(
    "-i",
    "--icon",
    nargs="?",
    type=Path,
    help="Full path to an icon for your org/team/etc. Placed at the top of the prompt infobox.",
)
parser.add_argument(
    "--processes",
    nargs="+",
    help='Space-separated list of process names to check if running. Determines the status of "Security Systems" in the prompt sidebar.',
)
parser.add_argument(
    "-v", "--verbose", action="count", default=0, help="Enable debug logging"
)
parser.add_argument(
    "--prefsfile",
    default=None,
    help="Full path or URL to a json file to set any/all options. Keys are identical to command-line long-form option flags (example: 'path' for a custom dialog binary path). Preferences set on the command line will take precedence over any found in a json file.",
)
parser.add_argument(
    "--saveprefs",
    action=argparse.BooleanOptionalAction,
    default=False,
    help='Overwrite an existing (or create new) preferences file at "/Library/Application Support/org/appUpdates/preferences.json". By default, prefs will be created if not present but NOT overwritten. Preferences set via configuration profile take precedence over local or URL-sourced preferences.',
)
parser.add_argument(
    "--setsilent",
    type=int,
    nargs="?",
    const=3600,
    default=None,
    help="Create and load a LaunchDaemon to run this script silently every x seconds. Default: every hour (3600) NOTE: Be sure to set org, icon, etc. or specify a preferences file with this data.",
)
parser.add_argument(
    "--setprompt",
    type=int,
    nargs="?",
    const=604800,
    default=None,
    help="Create and load a LaunchDaemon to run this script in prompt mode every x seconds. Default: every 7 days (604800) NOTE: Be sure to set org, icon, etc. or specify a preferences file with this data.",
)
parser.add_argument(
    "--setwatchpath",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Create and load a LaunchDaemon to trigger a silent run whenever a configuration profile is added, removed, or modified on the device. WARNING: This can potentially trigger a lot of silent runs depending on how much configuration profile traffic you have. This should be relatively inconsequential, but use with caution.",
)
parser.add_argument("--version", action="version", version=f"{scriptVersion}")
args = parser.parse_args()

## Get current interpreter and script paths for use in LaunchDaemons
pythonPath = sys.executable
scriptPath = sys.argv[0]


def endRun(exitCode=None, logLevel="info", message=None):
    if str(exitCode).isdigit():
        exitCode = int(exitCode)

    logCmd = getattr(logging, logLevel, "info")

    logCmd(message)
    sys.exit(exitCode)


## Check for a preferences configuration profile, URL, or local json file and attempt to parse if found
prefsData = None

profilePath = Path("/Library/Managed Preferences/com.github.swiftpatch.plist")

if profilePath.exists():
    logging.info("Found configuration profile for preferences, processing...")
    prefsSource = "profile"

    try:
        prefsData = plistlib.loads(profilePath.read_bytes())
        logging.debug("Successfully loaded preferences from configuration profile")
    except:
        endRun(2, "critical", "Failed to fetch preferences from configuration profile")

if prefs := args.prefsfile:
    logging.info("Loading preferences from file...")

    ## Try to get prefs from URL
    if prefs.startswith("http://") or prefs.startswith("https://"):
        logging.debug(f"Found URL for preferences: {prefs}")
        try:
            prefsData = json.loads(requests.get(prefs).content)
            prefsSource = "url"
        except:
            endRun(2, "critical", "Failed to fetch prefs from URL")

    ## Try to get prefs from file
    elif Path(prefs).exists:
        logging.debug(f"Attempting to read preferences from {prefs}...")
        try:
            prefsData = json.loads(Path(prefs).read_text())
            prefsSource = "file"
        except:
            endRun(2, "critical", "Failed to fetch prefs from file")

    else:
        endRun(2, "critical", "Prefs file was specified but unable to be loaded")
    logging.debug(f"Successfully retrieved preferences from {prefsSource}")


silentRun = args.silent if "silent" in args else None
deferredRun = args.defer if "defer" in args else None
selfService = args.selfservice if "selfservice" in args else None
orgName = args.org if "org" in args else None
dialogPath = Path(args.dialog) if "dialog" in args else None
iconPath = Path(args.icon) if "icon" in args else None
requiredProcessList = args.processes if "process" in args else None
verbose = args.verbose if "verbose" in args else None

## If preferences data was gathered from a file or URL, set those values
## Values from a preferences file are only set if the same option was not specified as a command-line argument
## For example, if a preferences file sets silent = False but the --silent option is specified on the command-line, the script will proceed as a silent run
if prefsData:
    silentRun = silentRun or prefsData.get("silent", "false").lower() == "true"
    deferredRun = deferredRun or prefsData.get("defer", "false").lower() == "true"
    orgName = orgName or prefsData.get("org", "org")
    dialogPath = dialogPath or Path(prefsData.get("dialog", "/usr/local/bin/dialog"))
    iconPath = iconPath or Path(
        prefsData.get("icon"), "/System/Library/CoreServices/Installer.app"
    )
    requiredProcessList = requiredProcessList or prefsData.get("processes", [])
    verbose = verbose or prefsData.get("verbose", 0)
    ## If an update is being run from Self Service, an ultralight interface will be used
    selfService = selfService or prefsData.get("selfservice", "").lower()

    ## Set additional preferences gathered from a file, if provided
    ## Simple mode defaults to False, using the full dialog with sidebar and instructions
    ## Speedtest (for estimating download time) defaults to True unless simple mode is enabled, in which case the data is not needed and the time can be saved
    simpleMode = str(prefsData.get("simple", "false")).lower() == "true"
    speedtest = all(
        [not simpleMode, str(prefsData.get("speedtest", "false")).lower() == "true"]
    )

    ## The dialog can be placed in any of validPositions on the user's screen
    ## Defaults to center if not set or set value is invalid
    validPositions = [
        "topleft",
        "left",
        "bottomleft",
        "top",
        "center",
        "bottom",
        "topright",
        "right",
        "bottomright",
    ]
    position = (
        prefsData.get("position").lower()
        if "position" in prefsData.keys()
        and prefsData.get("position").lower() in validPositions
        else "center"
    )

else:
    prefsSource = "cli"

    silentRun = args.silent
    deferredRun = args.defer
    selfService = args.selfservice
    orgName = args.org
    dialogPath = Path(args.dialog)
    iconPath = Path(args.icon)
    requiredProcessList = args.processes
    verbose = args.verbose

###############################
#### Logging configuration ####
###############################

## Current date
dateToday = datetime.date(datetime.now())

## Local log file
logDir = Path(f"/Library/Application Support/{orgName}/Logs/{dateToday}")
logDir.mkdir(parents=True, exist_ok=True)
logFile = logDir.joinpath(
    f"appUpdate-log_{time.asctime()}_silent-{silentRun}_defer-{deferredRun}.log"
)

## Configure root logger
logger = logging.getLogger()
logger.handlers = []

## Create handlers
logToFile = logging.FileHandler(str(logFile))
logToConsole = logging.StreamHandler(sys.stdout)

## Configure logging level and format
if verbose:
    logLevel = logging.DEBUG
    logFormat = logging.Formatter(
        "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
    )
else:
    logLevel = logging.INFO
    logFormat = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

## Set root and handler logging levels
logger.setLevel(logLevel)
logToFile.setLevel(logLevel)
logToConsole.setLevel(logLevel)

## Set log format
logToFile.setFormatter(logFormat)
logToConsole.setFormatter(logFormat)

## Add handlers to root logger
logger.addHandler(logToFile)
logger.addHandler(logToConsole)

###############################

## Generate a randomized temporary file to use for dialog commands
dialogCommandFile = Path(
    NamedTemporaryFile(prefix="dialogCommand-", suffix=".log").name
)
logging.debug(f"Using dialog command file at {str(dialogCommandFile)}")

## Log current date
logging.debug(f"Today is {dateToday}")

## Current user username and UID
userName = subprocess.run(
    ["/usr/bin/stat", "-f", "%Su", "/dev/console"], capture_output=True, text=True
).stdout.strip()
userUID = subprocess.run(
    ["/usr/bin/stat", "-f", "%u", "/dev/console"], capture_output=True, text=True
).stdout.strip()
logging.debug(f"Current user is {userName} with UID {userUID}")

## Define an empty reason for forcing an update by default
forceReason = None

## Path for storing deferral data
deferPath = Path(f"/Library/Application Support/{orgName}/appUpdates")
deferPath.mkdir(parents=True, exist_ok=True)
deferFile = deferPath.joinpath("deferralData.json")
logging.debug(f"Deferral data will be stored at {str(deferFile)}")

## Receipt file for last run
runReceipt = Path(f"/Library/Application Support/{orgName}/appUpdates/lastRun.json")
logging.debug(f"Last run data will be stored at {str(runReceipt)}")

## Preferences file to save settings between runs
prefsPath = Path(f"/Library/Application Support/{orgName}/appUpdates/preferences.json")

## Byte codes for emoji to be used in prompts
## Great place to find these: https://apps.timwhitlock.info/emoji/tables/unicode
emojiDict = {
    "greenHeart": b"\xf0\x9f\x92\x9a",
    "infoBox": b"\xE2\x84\xB9",
    "lightbulb": b"\xF0\x9F\x92\xA1",
    "magnifyingGlass": b"\xF0\x9F\x94\x8D",
    "warningSymbol": b"\xE2\x9A\xA0",
    "hourglass": b"\xE2\x8F\xB3",
    "greenCheck": b"\xE2\x9C\x85",
    "redX": b"\xE2\x9D\x8C",
    "greenX": b"\xE2\x9D\x8E",
    "thanksHands": b"\xF0\x9F\x99\x8F",
    "eyes": b"\xF0\x9F\x91\x80",
    "restartIcon": b"\xF0\x9F\x94\x81",
    "rightArrow": b"\xE2\x9E\xA1",
    "speechBalloon": b"\xF0\x9F\x92\xAC",
}

## Initialize some dicts and vars for dialog lists and behaviors
appListEntries = {}

dialogProgressList = {"listItem": []}

dialogPromptList = {"checkbox": []}

forcePrompt = False

##########################################################

###############################
##### Verify Requirements #####
###############################


def requirementsCheck():
    requirementsMet = True

    ## Dialog present and meets minimum version
    if Path.is_file(dialogPath):
        dialogVersion = subprocess.run(
            [dialogPath, "-v"], capture_output=True, text=True
        ).stdout.strip()
        logging.debug(f"Using dialog version {dialogVersion} at {dialogPath}")

        if not re.match(requiredDialogPattern, dialogVersion):
            logging.critical(
                f"Dialog version {dialogVersion} does not meet minimum {requiredDialogVersionString}!"
            )
            requirementsMet = False
    else:
        logging.critical(
            "Dialog binary was not found. Check your installation and/or specified path!"
        )
        requirementsMet = False

    ## Jamf binary present and server available
    if Path("/usr/local/bin/jamf").exists():
        logging.debug("jamf binary found")
        cmd = ["/usr/local/bin/jamf", "checkJSSConnection", "-retry", "5"]
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            jamfPrefs = loadPlist(
                Path("/Library/Preferences/com.jamfsoftware.jamf.plist")
            )
            logging.debug(f'jamf server at {jamfPrefs.get("jss_url")} is available')

        except subprocess.CalledProcessError:
            logging.critical("jamf server could not be reached!")
            requirementsMet = False
    else:
        logging.critical("jamf binary not found!")
        requirementsMet = False

    ## Python executable meets minimum version
    pythonVersionCmd = [pythonPath, "-V"]
    cmdResult = subprocess.run(pythonVersionCmd, text=True, capture_output=True)
    pythonVersion = cmdResult.stdout.split(" ")[-1].strip()

    if not re.match(requiredPythonPattern, pythonVersion):
        logging.critical(
            f"Python version {pythonVersion} does not meet minimum {requiredPythonVersionString}!"
        )
        requirementsMet = False
    else:
        logging.debug(f"Using Python version {pythonVersion} at {pythonPath}")

    if getProcessStatus("dialog"):
        logging.info("Another dialog is currently running!")
        requirementsMet = False
    else:
        logging.debug("No dialog processes found, continuing...")

    return requirementsMet


##########################
#### Define Functions ####
##########################


## Load and return data from a plist
def loadPlist(plistPath):
    logging.debug(f"Loading plist data from {str(plistPath)}")
    plistData = plistlib.loads(plistPath.read_bytes())
    return plistData


## Dump data into a plist
def dumpPlist(plistData, plistPath):
    logging.debug(f"Dumping plist data to {str(plistPath)}")
    logging.debug(f"Plist data sent: {plistData}")
    plistPath.write_bytes(plistlib.dumps(plistData))


## Load and return data from a json file
def loadJson(jsonPath):
    logging.debug(f"Loading json data from {str(jsonPath)}")
    jsonData = json.loads(jsonPath.read_text())
    return jsonData


## Dump data into a json file
def dumpJson(jsonData, jsonPath):
    logging.debug(f"Dumping json data to {str(jsonPath)}")
    logging.debug(f"json data sent: {jsonData}")
    jsonPath.write_text(json.dumps(jsonData))


## Attempt to load a LaunchDaemon
def loadLaunchDaemon(daemonPath):
    ## launchctl command to load the LaunchDaemon once created
    cmd = [
        "/bin/launchctl",
        "load",
        "-w",
        str(daemonPath),
    ]

    ## Try to unload the LaunchDaemon so new data can be picked up if this is an update, and fail silently otherwise
    try:
        subprocess.run(["/bin/launchctl", "unload", str(daemonPath)], text=True)
        logging.info("Unloaded existing LaunchDaemon")
    except:
        logging.debug(
            "Failed to unload existing LaunchDaemon. This message is not an error and can be ignored."
        )

    ## Load the LaunchDaemon
    try:
        subprocess.run(cmd, text=True, check=True)
        logging.info("Daemon created and loaded successfully")
        return 0

    except subprocess.CalledProcessError:
        logging.error(
            f"Something went wrong loading the LaunchDaemon: {subprocess.CalledProcessError.output}"
        )
        return subprocess.CalledProcessError.returncode


## Return a requested emoji
def getEmoji(emojiLabel):
    try:
        emoji = emojiDict[emojiLabel].decode("utf-8")
        logging.debug(f"Retrieved emoji: {emojiLabel} ({emoji})")

    except KeyError:
        emoji = None
        logging.warning(f"Failed to retrieve emoji: {emojiLabel}")

    return emoji


## Send an update to the dialog command log
def updateDialog(command):
    if not command:
        logging.warning("No command specified to updateDialog, returning...")
        return

    with open(dialogCommandFile, "a") as commandLog:
        logging.debug(f"Appending command '{command}' to {dialogCommandFile}")
        commandLog.write(f"{command}\n")


## Send a status update to the dialog command file
def updateStatus(status, statustext, listIndex):
    if type(listIndex) is not int or listIndex > len(appListEntries):
        logging.error(
            "Invalid data sent to updateStatus function. Dialog command file will not be updated."
        )
        return

    if silentRun and not forcePrompt:
        return

    if not selfService:
        itemStatus = f"status: {status}" if "progress" not in status else status
        dialogCommand = (
            f"listitem: index: {listIndex}, {itemStatus}, statustext: {statustext}"
        )
        progressUpdate = {"status": itemStatus, "statustext": statustext}
        dialogProgressList["listItem"][listIndex].update(progressUpdate)
        updateDialog(dialogCommand)
    else:
        if "progress" in status:
            updateDialog(status)
        elif status == "wait":
            updateDialog("progress: 0")
        updateDialog(f"progresstext: {statustext}")


## Check provided array of processes for security apps or other requirements
def getProcessStatus(processName):
    logging.debug(f"Checking for running process {processName}...")
    checkCmdStatus = not bool(
        subprocess.run(
            ["/usr/bin/pgrep", processName],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ).returncode
    )
    logging.info(f"Process status check for {processName}: {checkCmdStatus}")
    return checkCmdStatus


## Get the required version of macOS from a Nudge configuration profile (if present), or the latest version from the Apple catalog
## Then, compare it to the currently-installed version and return a boolean based on whether or not the versions match (i.e. the device is up to date)
def getOSVersionData():
    macOSInstalledVer = platform.platform().split("-")[1]
    logging.info(f"Installed macOS version is {macOSInstalledVer}")

    logging.debug("Getting latest macOS version")

    nudgeConfigFile = Path(
        "/Library/Managed Preferences/com.github.macadmins.Nudge.plist"
    )

    if nudgeConfigFile.exists():
        logging.debug("Found Nudge configuration profile")

        try:
            nudgeConfigData = loadPlist(
                Path("/Library/Managed Preferences/com.github.macadmins.Nudge.plist")
            )
            latestVersion = nudgeConfigData["osVersionRequirements"][0][
                "requiredMinimumOSVersion"
            ]
            logging.info(
                f"Required minimum macOS version from Nudge is {latestVersion}"
            )

        except:
            logging.error(
                "Unable to load required macOS version from Nudge configuration profile"
            )

    else:
        logging.debug("Fetching latest macOS version from Apple catalog")

        catalogURL = "https://gdmf.apple.com/v2/pmv"
        catalogData = requests.get(catalogURL, verify=False)

        try:
            catalog = json.loads(catalogData.text)
        except:
            logging.error("Something went wrong loading Apple catalog data")
            upToDate = False

        latestVersion = sorted(
            catalog.get("PublicAssetSets").get("macOS"),
            key=lambda x: x.get("ProductVersion"),
            reverse=True,
        )[0].get("ProductVersion")

        if not re.match("\d{2}\.\d\.\d", latestVersion):
            logging.warning(
                "Latest version from Apple catalog does not match expected semantic versioning pattern!"
            )
            upToDate = False

        logging.info(f"Latest macOS version from Apple is {latestVersion}")

    ## If version strings are equal OR the installed major version is greater than the latest required/available major version, consider macOS up to date
    if macOSInstalledVer == latestVersion or int(macOSInstalledVer.split(".")[0]) > int(
        latestVersion.split(".")[0]
    ):
        logging.info("macOS is up to date")
        upToDate = True
    else:
        logging.info("macOS is not up to date")
        upToDate = False

    return upToDate, macOSInstalledVer


## Get device health info for dialog display
def getDeviceHealth():
    logging.info("Collecting device health data...")

    macOSUpdated, macOSInstalledVer = getOSVersionData()

    deviceInfo = {
        "macOSVersion": macOSInstalledVer,
        "macOSIsCurrent": macOSUpdated,
        "serialNumber": platform.node().split("-")[1],
        "systemUptimeDays": round(time.clock_gettime(time.CLOCK_MONOTONIC_RAW) / 86400),
        "healthCheck": True
        if (
            len(requiredProcessList) > 0
            and all(getProcessStatus(x) for x in requiredProcessList)
        )
        or len(requiredProcessList) == 0
        else False,
        "diskUsage": int((disk_usage("/").used / disk_usage("/").total) * 100),
    }

    infoboxData = f"\
### Device Information\n\
**Serial Number**\n\n{deviceInfo['serialNumber']}\n\n\
**macOS Version**\n\n{getEmoji('greenCheck') if deviceInfo['macOSIsCurrent'] else getEmoji('redX')} {deviceInfo['macOSVersion']}{'<br>***Please update!***' if not deviceInfo['macOSIsCurrent'] else ''}\n\n\
**Last Restart**\n\n{getEmoji('greenCheck') if deviceInfo['systemUptimeDays'] < 14 else getEmoji('redX')} {deviceInfo['systemUptimeDays']} day{'s' if deviceInfo['systemUptimeDays'] != 1 else ''} ago{'<br>***Please restart soon!***' if deviceInfo['systemUptimeDays'] >= 14 else ''}\n\n\
**Disk Usage**\n\n{getEmoji('greenCheck') if deviceInfo['diskUsage'] < 75 else getEmoji('warningSymbol')} {deviceInfo['diskUsage']}%\n{'All good!' if deviceInfo['diskUsage'] < 75 else '<br>***Getting full!***'}\n\n\
**Security Systems**\n\n{getEmoji('greenCheck') + ' All good!' if deviceInfo['healthCheck'] else getEmoji('redX') + '<br>***Please contact support!***'}\n\n\
_A message from {orgName} IT_ {getEmoji('greenHeart')}"

    logging.debug(f"Collected device information for dialog sidebar: {deviceInfo}")
    return infoboxData


## Read the app's creation date and compare it to the current date
## If more than 60 days have passed since the last update, force the update now
def checkInstallDate(bid):
    appPath = getAppPath(bid)

    appLastInstalled = datetime.fromtimestamp(appPath.stat().st_birthtime).date()
    installDelta = dateToday - appLastInstalled

    logging.info(
        f"{str(appPath.stem)} was last updated on {appLastInstalled}, which was {installDelta.days} days ago."
    )
    if installDelta.days > 60:
        logging.warning(
            "More than 60 days have passed since the last update, forcing update now..."
        )
        global forceReason
        forceReason = "Last update >60 days ago"
        return False

    return True


## Make sure we're not running too frequently or too soon after the last run
def validateRunTiming():
    logging.info("Validating run timing...")

    ## If running from a deferral LaunchDaemon, the run is valid and no checks need to be done
    if deferredRun:
        logging.info("Run is valid: deferred execution")
        return True

    timeNow = int(time.time())
    logging.debug(f"Current epoch time is {timeNow}")

    if runReceipt.exists():
        receiptData = json.loads(runReceipt.read_text())

        lastRunTime = (
            receiptData.get("silent" if silentRun else "prompt").get("runTime") or 0
        )

        runDelta = timeNow - lastRunTime
        logging.debug(f"Update script was last run {runDelta} seconds ago")
    else:
        logging.info("Run is valid: no run receipt found")
        return True

    ## Make sure this is running at least once every other week minimum
    if runDelta >= 1209600:
        logging.warning(
            "More than two weeks have passed since the last run, forcing run now..."
        )
        return True

    ## If run less than 30 minutes ago, or prompted less than 8 hours ago and trying to prompt again (not counting user deferrals), stop
    if runDelta <= 1800 or (not silentRun and runDelta <= 28800):
        logging.warning("Run attempted too soon after last run, skipping...")
        return False
    else:
        logging.info("Run is valid: acceptable interval since last run")
        return True


## Write out a json file with details of the last run
def writeRunReceipt():
    logging.info("Writing run receipt...")

    runResult = {}

    for update in appListEntries:
        updateData = appListEntries[update]
        updateResult = {
            update: {
                "background": updateData["background"],
                "force": updateData["force"],
                "result": updateData["result"],
            }
        }

        runResult.update(updateResult)
        logging.debug(f"Updating run result: {updateResult}")

    runData = {
        "silent"
        if silentRun
        else "prompt": {
            "runTime": int(time.mktime(time.gmtime())),
            "runResult": runResult,
        }
    }

    if runReceipt.exists():
        receiptData = json.loads(runReceipt.read_text())
    else:
        receiptData = {}

    receiptData.update(runData)

    runReceipt.write_text(json.dumps(receiptData))
    logging.debug(f"Run receipt: {receiptData}")


## Use a native macOS API to determine whether or not the app is running using its bundle ID
## Return a boolean value based on the result
def checkIfRunning(bid):
    app = next(
        (a for a in NSRunningApplication.runningApplicationsWithBundleIdentifier_(bid)),
        None,
    )
    logging.info(f"{bid} running: {bool(app)}")
    return app


## Return the path of an application from its bundle ID
def getAppPath(bid, versionKey=None):
    if versionKey in ["CFBundleVersion", "CFBundleShortVersionString"]:
        path = Path(
            NSWorkspace.sharedWorkspace()
            .URLForApplicationWithBundleIdentifier_(bid)
            .path()
        )
        logging.debug(f"{bid} found at {path}")
    else:
        path = Path(versionKey)
        logging.debug(f"{bid} path set to {path} as a binary file")

    return path


## Try common arguments to get the version of a binary at a specified path
def getBinaryVersion(path):
    ## If there's no file there, log a warning
    if not path.exists():
        logging.warning(f"Unable to find {str(path.stem)} at {str(path)}")
    else:
        options = ["-v", "-V", "--version", "version"]

        ## Try arguments to find a version
        for option in options:
            try:
                cmd = [str(path), option]

                try:
                    versionCheck = subprocess.check_output(
                        cmd, stderr=subprocess.STDOUT, text=True
                    )

                except FileNotFoundError:
                    continue

                if version := re.search("\d*\.\d*\.\d*", versionCheck):
                    versionString = version[0]
                elif version := re.search("\d*\.\d*", versionCheck):
                    versionString = version[0]
                else:
                    continue

                logging.debug(
                    f"Got version {versionString} of {str(path)} using {option}"
                )
                return versionString

            ## Move on to the next argument in the list if the command fails
            except subprocess.CalledProcessError:
                continue

    ## If a version was found, this code will never be reached
    ## Otherwise, return a dummy version
    logging.error(f"Unable to determine current version of {str(path)}")
    return "0.0.0"


## Clean up LaunchDaemons from deferred update prompts
## If the current iteration is running from a LaunchDaemon, that daemon will still be present after the script exits
## It will need to be unloaded and deleted before the script exits
## Otherwise, it will be loaded again next time the device restarts and the user will get an erroneous update prompt
def removeDaemons():
    daemonFiles = sorted(
        Path("/Library/LaunchDaemons").glob(
            f"com.{orgName.lower()}.appUpdates.runDeferral.*.plist"
        )
    )[:-1]
    if daemonFiles:
        logging.debug(f"Removing old LaunchDaemons: {daemonFiles}")
    else:
        logging.debug("No old LaunchDaemons found to remove")

    for daemon in daemonFiles:
        try:
            logging.debug(f"Unloading and removing {str(daemon.stem)}...")
            cmd = ["/bin/launchctl", "remove", daemon.stem]
            subprocess.run(cmd, text=True)
            daemon.unlink(missing_ok=True)
        except Exception as e:
            logging.error(f"Error removing daemon ({daemon}): ", str(e))

    return


## Write out and load a LaunchDaemon to call the deferral policy after the user's selected time
## Need to make a fresh file for each deferral, because unloading the existing one kills the jamf process that's trying to make the new one
## Chicken and egg situation, but easily worked around by creating unique daemons using epoch time
def setDeferral(deferralIndex=None):
    ## Map list indices of user deferral options to seconds for use in the LaunchDaemon
    deferralIndexMap = {
        # Random
        -1: None,
        # 5 minutes
        0: 300,
        # 15 minutes
        1: 900,
        # 1 hour
        2: 3600,
        # 3 hours
        3: 10800,
        # 1 day
        4: 86400,
    }

    ## If the deferral index isn't specified (such as deferring because of user DND), set a random deferral time between 5 and 15 minutes
    deferralPeriod = (
        deferralIndexMap[deferralIndex]
        if deferralIndex is not None
        else random.randint(300, 900)
    )

    logging.info(f"Deferring run for {deferralPeriod} seconds")

    removeDaemons()

    daemonTime = int(time.time())
    daemonLabel = f"com.{orgName.lower()}.appUpdates.runDeferral.{daemonTime}"
    daemonFile = f"/Library/LaunchDaemons/{daemonLabel}.plist"
    logging.debug(f"Creating deferral daemon at {daemonFile}")

    if setPrefsFile():
        daemonData = {
            "Label": daemonLabel,
            "LaunchOnlyOnce": True,
            "ProgramArguments": (
                pythonPath,
                scriptPath,
                "--no-silent",
                "--defer",
                "--prefsfile",
                str(prefsPath),
            ),
            "StartInterval": deferralPeriod,
        }

    else:
        daemonData = {
            "Label": daemonLabel,
            "LaunchOnlyOnce": True,
            "ProgramArguments": (
                pythonPath,
                scriptPath,
                "--no-silent",
                "--defer",
                "--org",
                orgName,
                "--dialog",
                str(dialogPath),
                "--icon",
                str(iconPath),
            ),
            "StartInterval": deferralPeriod,
        }

    dumpPlist(daemonData, Path(daemonFile))

    loadLaunchDaemon(daemonFile)


## Given an app name and deferral limit, check the deferral metadata file (if it exists) for an existing deferral count
## If all deferrals have been used, the update will be forced
def checkDeferralCount(appName, appDeferLimit):
    logging.info(f"Deferral limit for {appName} is {appDeferLimit}")

    if not deferFile.exists():
        deferValue = {
            appName: 0,
        }

        deferFile.write_text(json.dumps(deferValue))

    deferData = json.loads(deferFile.read_text())

    if appName in deferData.keys():
        deferCount = deferData[appName]
    else:
        deferCount = 0

    if int(deferCount) >= int(appDeferLimit):
        logging.info(f"All deferrals used for {appName}")
        deferralsRemain = False
    else:
        logging.info(f"{deferCount} deferral(s) have been used for {appName}")
        deferralsRemain = True

    return deferralsRemain, deferCount


## Increment the deferral count
## If reset=True, the deferral count for the given app will be set to 0
def incrementDeferral(appName, reset=False):
    deferData = json.loads(deferFile.read_text())

    if appName in deferData.keys():
        deferCount = deferData[appName]
    else:
        deferCount = 0

    deferValue = {
        appName: deferCount + 1 if not reset else 0,
    }

    deferData.update(deferValue)

    logging.info(f"Setting deferral count for {appName} to {deferValue[appName]}...")

    deferFile.write_text(json.dumps(deferData))


## Quit the application to be updated if the update isn't being deferred or otherwise skipped
## If the app should be force-terminated (in the case of a forced update), kill it immediately
## Otherwise, attempt to quit it gracefully
## This function will loop once per second for 30 seconds monitoring whether or not the app is still running
## If still running after 10 quit attempts, it switches to forced termination
def quitApp(bid, force=False):
    logging.info("Terminating app {}".format(bid))

    for i in range(30):
        app = checkIfRunning(bid)

        if not app or app.isTerminated():
            logging.debug(f"{bid} is not running.")
            break

        if force:
            app.forceTerminate()
        else:
            app.terminate()

        if i >= 10 and not app.isTerminated():
            logging.warning(f"Terminating {bid} taking too long. Forcing terminate.")
            app.forceTerminate()

        logging.debug(f"Waiting on {bid} to terminate")
        time.sleep(1)


## Check to see if the user is on an active Zoom call by looking for the CptHost process
def checkForZoom():
    zoompid = subprocess.run(
        ["pgrep", "CptHost"], capture_output=True, text=True
    ).stdout.strip()

    logging.debug(f"Zoom running: {bool(zoompid)}")

    return True if zoompid else False


## If the user has Do Not Disturb or a Focus mode set, don't generate any prompts
def checkForDnd():
    userAssertionsFile = Path(
        "/Users/" + userName + "/Library/DoNotDisturb/DB/Assertions.json"
    )

    try:
        assertions = json.loads(userAssertionsFile.read_text())
        logging.debug(
            f'DND assertions found: {bool(assertions["storeAssertionRecords"])}'
        )
        return True if assertions["storeAssertionRecords"] else False
    except:
        return False


## Check if the user is using an app in presentation mode
def checkForPresentation():
    displaySleepAssertions = subprocess.run(
        '/usr/bin/pmset -g assertions | /usr/bin/awk \'/NoDisplaySleepAssertion | PreventUserIdleDisplaySleep/ && match($0,/\(.+\)/) && ! /coreaudiod/ && ! /Video\ Wake\ Lock/ {gsub(/^.*\(/,"",$0); gsub(/\).*$/,"",$0); print};\'',
        capture_output=True,
        text=True,
        shell=True,
    ).stdout.strip()
    logging.debug(f"Presentation mode active: {bool(displaySleepAssertions)}")
    return True if displaySleepAssertions else False


## Check for any of the above interruption conditions
## Loop every 30 seconds for up to 5 minutes
def checkInterruptions():
    for i in range(10):
        interruptCheck = any([checkForDnd(), checkForPresentation(), checkForZoom()])

        if i == 9 and interruptCheck:
            logging.warning("User still busy after 5 minutes, deferring prompt...")
            return True
        if not interruptCheck:
            logging.info("User is not busy, continuing...")
            return False
        else:
            logging.info("User is busy, waiting...")
            time.sleep(30)


## Verify the app to be updated is running a version other than the latest
## If there's a match, no action needs to be taken
def checkVersion(
    bid, targetVersion, appVersionKey, appVersionRegex=None, rollbackVersion=False
):
    appPath = getAppPath(bid, appVersionKey)

    ## If we're dealing with an actual app, appVersionKey will be one of the version keys from its Info.plist
    if appVersionKey in ["CFBundleVersion", "CFBundleShortVersionString"]:
        appInfoPlist = appPath.joinpath("Contents/Info.plist")
        plistData = loadPlist(appInfoPlist)
        installedVersion = plistData[appVersionKey]

    ## Otherwise, we need to try and get the version of a single binary
    else:
        installedVersion = getBinaryVersion(appPath)

    ## Fall back to version string comparison if no regex provided
    if not appVersionRegex:
        logging.warning("No version regex provided, using string comparison")

        if installedVersion == targetVersion:
            logging.debug("Version strings match--no update required")
            versionCheck = False

        else:
            logging.debug(
                f"Found {appVersionKey} {installedVersion}, needs {targetVersion}"
            )
            versionCheck = True

        return versionCheck, installedVersion

    ## Only proceed with patterns that aren't empty
    appVersionRegex = [x for x in appVersionRegex if x != "^$"]

    for pattern in appVersionRegex:
        ## If either the CFBundleVersion or CFBundleShortVersionString match the pattern, matchTest will evaluate True
        matchTest = re.match(pattern, installedVersion)
        logging.debug(f"Checking {pattern} against {installedVersion}")

        ## If we have a match and this is a rollback, break the loop with a successful version check (i.e. the update is required)
        if rollbackVersion and matchTest:
            logging.debug(f"Rolling back to {rollbackVersion}")
            versionCheck = True
            break

        ## If no match was found, the update is required
        elif not matchTest:
            logging.debug(
                f"Found {appVersionKey} {installedVersion}, needs {targetVersion}"
            )
            versionCheck = True
            break

        ## If a match was found, no action needs to be taken for this app
        else:
            logging.debug("No update requirement found with this version pattern")
            versionCheck = False

    logging.info(
        f'{f"Update required for {appPath.stem}" if versionCheck else f"No update needed for {appPath.stem}"}'
    )

    ## Send back a tuple with a boolean of whether or not the update is required, and the currently installed version of the app
    return versionCheck, installedVersion


## Gather up data from any update profiles on the device
def getUpdateRequirements():
    global dialogPromptList
    global dialogProgressList
    global forcePrompt

    logging.info("Gathering update requirements...")

    profilesDir = Path("/Library/Managed Preferences")
    updateProfiles = [
        x
        for x in profilesDir.iterdir()
        if re.match(
            f"com\.appUpdates\.managedApps\.{selfService}.*".lower(),
            str(x.stem).lower(),
        )
    ]
    logging.debug(f"Found update profiles: {updateProfiles}")

    if not updateProfiles:
        logging.info("No app update configuration profiles found")
        return None

    for profile in updateProfiles:
        profileData = loadPlist(profile)
        logging.debug(f"Loading update data from {profile}...")

        appBundleID = profileData.get("bundleID")
        appDisplayName = profileData.get("displayName")
        appTargetVersion = profileData.get("targetVersionString")
        appDeferLimit = profileData.get("deferLimit", 10)
        appForceUpdate = profileData.get("forceUpdate").lower() == "true"
        appRollbackVersion = profileData.get("rollbackVersion", "false")
        appIsRollback = appRollbackVersion.lower() != "false"
        appPackageSize = profileData.get("pkgSize", 0)
        appVersionKey = profileData.get("versionKey", "CFBundleShortVersionString")
        appVersionRegex = [
            profileData.get("targetVersionRegex", "^$"),
            profileData.get("targetVersionRegex2", "^$"),
            profileData.get("targetVersionRegex3", "^$"),
        ]

        logging.debug(f"Profile data loaded: {profileData}")

        requiredKeys = [appBundleID, appDisplayName, appTargetVersion]

        if not all(requiredKeys):
            logging.error(
                f'Missing required key(s) for update processing: {", ".join([x for x in requiredKeys if x is None])}'
            )
            continue

        logging.info(f"Processing update data for {appDisplayName}...")

        if appForceUpdate:
            logging.warning(f"{appDisplayName} will be force updated")
            forceReason = "Urgent security patch"
            forcePrompt = True
            deferralPermitted = False
        else:
            logging.debug(f"{appDisplayName} update is not a force update")
            forceReason = None
            deferralPermitted = True

        updateRequired, installedVersion = checkVersion(
            appBundleID,
            appTargetVersion,
            appVersionKey,
            appVersionRegex,
            appRollbackVersion if appIsRollback else None,
        )

        if updateRequired:
            logging.info(f"{appDisplayName} needs to be updated")

            if all([silentRun, checkIfRunning(appBundleID), not appForceUpdate, not selfService]):
                logging.warning(
                    f"Silent run is enabled and {appDisplayName} is running, skipping update"
                )
                continue

            appPath = getAppPath(appBundleID, appVersionKey)

            deferralsRemain, deferralsUsed = checkDeferralCount(
                appDisplayName, appDeferLimit
            )

            if not deferralsRemain:
                logging.info(f"All deferrals used for {appDisplayName}")
                forceReason = "No deferrals remaining"

            if appForceUpdate:
                switchDisabled = True
            elif (
                checkIfRunning(appBundleID)
                and all([deferralsRemain, deferralPermitted])
            ) or appIsRollback:
                switchDisabled = False
            else:
                switchDisabled = True

            logging.debug(
                f"Update switch disabled for {appDisplayName}: {switchDisabled}"
            )

            ## Used in the initial user prompt for selection of which apps to update or defer
            listLabel = f'{appDisplayName} | v{installedVersion} {getEmoji("rightArrow")} v{appTargetVersion}'
            listLabel += (
                f" | {(int(appDeferLimit) - deferralsUsed)} deferrals remaining"
                if (int(appDeferLimit) - deferralsUsed <= 3)
                else ""
            )
            listLabel += " | (ROLLBACK)" if appIsRollback else ""
            listLabel += f" | ({forceReason})" if forceReason is not None else ""
            logging.debug(f"List label: {listLabel}")

            icon = (
                str(appPath)
                if (
                    Path("/Applications") in appPath.parents[::]
                    and appPath.suffix == ".app"
                )
                else "/System/Applications/Utilities/Terminal.app"
            )

            appData = {
                "label": listLabel,
                "checked": True,
                "disabled": switchDisabled,
                "icon": icon,
            }

            dialogPromptList["checkbox"].append(appData)

            ## Used in the second prompt to show update progress
            listEntry = {
                "title": appDisplayName,
                "icon": icon,
                "status": "pending",
                "statustext": "Pending",
            }

            dialogProgressList["listItem"].append(listEntry)

            ## Sort lists together so index calculations below will be accurate
            dialogPromptList["checkbox"].sort(
                key=lambda x: x["label"].split("|")[0].strip()
            )

            dialogProgressList["listItem"].sort(key=lambda x: x["title"])

            ## Used internally to store data about updates being installed
            appListEntry = {
                appDisplayName: {
                    "bundleID": appBundleID,
                    "listIndex": next(
                        i
                        for (i, x) in enumerate(dialogProgressList["listItem"])
                        if x["title"].startswith(appDisplayName)
                    ),
                    "background": not checkIfRunning(appBundleID),
                    "force": False
                    if silentRun and not checkIfRunning(appBundleID)
                    else switchDisabled,
                    "result": None,
                    "pkgSize": appPackageSize,
                    "versionString": appTargetVersion,
                    "versionKey": appVersionKey,
                }
            }
            appListEntries.update(appListEntry)

        else:
            logging.info(f"No update required for {appDisplayName}")

    return dialogPromptList["checkbox"]


## Update inventory to jamf
def runRecon():
    logging.info("Running recon...")
    cmd = ["/usr/local/bin/jamf", "recon"]
    subprocess.run(cmd, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


## Receive stdout from a policy run and update the dialog command file as the policy executes
## Once the policy is finished, the success or failure result is added to appListEntries, which will be dumped into the run result file
def monitorPolicyRun(logStream, appName):
    appData = appListEntries.get(appName)

    bundleID = appData.get("bundleID")
    listIndex = appData.get("listIndex")
    downloadSize = appData.get("pkgSize")
    expectedVersionString = appData.get("versionString")
    versionKey = appData.get("versionKey", "CFBundleShortVersionString")

    logging.info(f"Monitoring jamf policy progress for {appName}...")

    while True:
        for logData in logStream.stdout:
            if re.match("^Checking for policies triggered by.*$", logData):
                logging.debug(logData)
                updateDialog("overlayicon: SF=icloud.and.arrow.down,palette=auto")
                updateStatus("pending", "Download pending...", listIndex)

            elif re.match("^Executing Policy Install Latest.*$", logData):
                logging.debug(logData)
                updateStatus("progress: 100", "Download pending...", listIndex)

            elif re.match("^Downloading.*$", logData) or re.match(
                "^Resuming download of.*$", logData
            ):
                logging.debug(logData)
                pkgName = urllib.parse.unquote(
                    logData.rsplit("/", 1)[-1].split("...", 1)[0].split(" ", 1)[-1]
                )
                pkgPath = Path(f"/Library/Application Support/JAMF/Downloads/{pkgName}")
                pkgVersion = ".".join(pkgName.split(".")[:-1]).split("-")[-1]
                logging.debug(f"Package destination is {pkgPath}")
                if expectedVersionString != pkgVersion:
                    logging.warning(
                        f"Expected version {expectedVersionString} does not match download version {pkgVersion}"
                    )
                bytesDownloaded = 0
                time.sleep(1)
                while bytesDownloaded <= downloadSize and pkgPath.exists:
                    bytesDownloaded = pkgPath.stat().st_size
                    percentDownloaded = round((bytesDownloaded / downloadSize) * 100)
                    updateStatus(
                        f"progress: {percentDownloaded}", "Downloading...", listIndex
                    )
                    if percentDownloaded == 100:
                        break
                    time.sleep(0.1)
                else:
                    updateStatus("wait", "Validating download...", listIndex)

            elif re.match("^Verifying package integrity.*$", logData):
                logging.debug(logData)
                updateStatus("wait", "Validating download...", listIndex)

            elif re.match("^Installing.*$", logData):
                logging.debug(logData)
                updateDialog("overlayicon: /System/Library/CoreServices/Installer.app")
                updateStatus("wait", "Installing...", listIndex)

            elif re.match("^Successfully installed.*$", logData):
                logging.debug(logData)
                versionStringMismatch, _ = checkVersion(
                    bundleID, expectedVersionString, versionKey
                )
                if not versionStringMismatch:
                    logging.debug(f"Verified new version instalation for {appName}")
                    updateDialog("overlayicon: SF=checkmark.circle.fill,color=green")
                    updateStatus("success", "Update complete!", listIndex)
                    appListEntries[appName].update({"result": "success"})
                    dialogProgressList["listItem"][listIndex].update(
                        {"status": "success"}
                    )
                    logging.info(
                        f"{appName} was successfully updated to version {expectedVersionString}"
                    )
                else:
                    logging.warning(f"Unable to verify updated version for {appName}")
                    updateDialog(
                        "overlayicon: SF=exclamationmark.triangle.fill,color=yellow"
                    )
                    updateStatus("error", "Unable to verify update", listIndex)
                    appListEntries[appName].update({"result": "unknown"})
                    dialogProgressList["listItem"][listIndex].update(
                        {"status": "error", "statustext": "Unable to verify update"}
                    )
                break
            else:
                logging.debug(logData)
                updateDialog("overlayicon: SF=x.square,color=red")
                updateStatus("fail", "Something went wrong", listIndex)
                appListEntries[appName].update({"result": "fail"})
                dialogProgressList["listItem"][listIndex].update(
                    {"status": "fail", "statustext": "Something went wrong"}
                )
                logging.error(f"Something went wrong attempting to update {appName}")
                break

        break


## Call the jamf policy to install the updated app package
## This function accepts an event as a trigger for a jamf policy to install an app package, such as 'autoupdate-Slack'
## The jamf binary is called to explicitly run the policy with the specified event trigger
## If the event trigger is empty, do nothing
## stdout is sent to monitorPolicyRun so the user-facing dialog can be updated in realtime
def runJamfPolicy(appName):
    if not appName:
        logging.warning("No app name sent to run policy function, returning...")
        return

    incrementDeferral(appName, reset=True)

    logging.debug(f"Calling jamf policy for {appName}...")
    cmd = [
        "/usr/local/bin/jamf",
        "policy",
        "-event",
        "autoupdate-" + appName,
        "-forceNoRecon",
    ]

    proc = subprocess.Popen(
        cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    monitorPolicyRun(proc, appName)


## Build prompt json and call dialog
def promptForUpdates():
    defaultMessage = f"\
{getEmoji('lightbulb')} Any running apps selected for update will be closed.  \n \
{getEmoji('hourglass')} Deferral options, if available, are at the bottom.  \n\
{getEmoji('eyes')} To **defer** an update, first **deselect** the apps you'd like to update, then choose a deferral time below the list.\n\n\
**Note: Any apps not currently running or with no remaining deferrals will be updated at this time.**\n\n\
Apps to be _deferred_ will look like this:          ![toggleOff](https://i.imgur.com/mOd52bV.png)\n\n\
Apps to be _updated now_ will look like this:   ![toggleOn](https://i.imgur.com/xBHRc0K.png)\n\n"

    dialogConfig = {
        "title": "Managed App Updates Available",
        "titlefont": "size=20",
        "messagefont": "size=14",
        "messageposition": "top",
        "position": position,
        "button1text": "Update Apps",
        "button1disabled": "True",
        "timer": "300",
        "infobutton": 0,
        "quitoninfo": 0,
        "ontop": 1,
        "moveable": 1,
        "quitkey": "i",
        "json": 1,
        "checkboxstyle": {"style": "switch", "size": "small"},
        "checkbox": dialogPromptList["checkbox"],
    }

    if simpleMode:
        modeConfig = {
            "message": "**App to be Quit and Updated                                                              Update Now?**",
            "messagealignment": "center",
            "hideicon": 1,
            "width": "550",
        }

    else:
        global infoboxData
        infoboxData = getDeviceHealth()

        modeConfig = {
            "message": defaultMessage,
            "icon": str(iconPath),
            "iconsize": "120",
            "infobox": infoboxData,
            "hideicon": 0,
            "height": "625",
        }

    dialogConfig.update(modeConfig)

    ## Add deferral options to the dialog config if any of the pending updates can be deferred
    ## Default selection of None will result in a randomized 5-15 minute deferral
    if bool([x for x in dialogPromptList["checkbox"] if x["disabled"] is False]):
        logging.debug("Adding deferral options to prompt configuration...")
        deferOptions = {
            "selectitems": [
                {
                    "title": "Defer Unselected Apps:",
                    "required": "False",
                    "values": ["5 minutes", "15 minutes", "1 hour", "3 hours", "1 day"],
                }
            ]
        }
        dialogConfig.update(deferOptions)

    promptJson = "/var/tmp/prompt.json"

    Path(promptJson).write_text(json.dumps(dialogConfig))

    promptCmd = ["/opt/chime/bin/dialog", "--jsonfile", promptJson]

    logging.debug("Generating prompt dialog...")
    logging.debug(f"Prompt dialog configuration: {loadJson(Path(promptJson))}")
    prompt = subprocess.run(promptCmd, text=True, capture_output=True)

    promptResponse = json.loads(prompt.stdout) if prompt.stdout else None
    promptReturnCode = prompt.returncode

    ## dialog will return the checkbox list state and deferral selection when finished
    ## Send that and the return code back to the caller for processing
    logging.debug(f"Prompt exited with code {promptReturnCode}")
    logging.debug(f"Prompt returned response: {promptResponse}")
    return promptResponse, promptReturnCode


## Build the progress reporting config
def parseUserSelections(promptOutput):
    totalDownloadSize = 0

    logging.info("Parsing prompt selections...")

    selectedApps = [
        x.split("|")[0].strip() for x in promptOutput.keys() if promptOutput[x] is True
    ]
    progressListApps = [x for x in dialogProgressList["listItem"]]

    for app in progressListApps:
        appFriendlyName = app["title"]

        if app["title"] not in selectedApps:
            logging.info(f"{appFriendlyName} was deferred")
            appListEntries[appFriendlyName].update({"result": "deferred"})
            dialogProgressList["listItem"].remove(app)
            incrementDeferral(appFriendlyName)
        else:
            logging.info(f"Update accepted for {appFriendlyName}")
            appDownloadSize = appListEntries.get(appFriendlyName).get("pkgSize") or 0
            appListEntries[appFriendlyName].update(
                {
                    "listIndex": next(
                        i
                        for (i, x) in enumerate(dialogProgressList["listItem"])
                        if x["title"].startswith(appFriendlyName)
                    )
                }
            )
            logging.debug(
                f'New list index for {appFriendlyName} is {appListEntries[appFriendlyName]["listIndex"]}'
            )
            totalDownloadSize += appDownloadSize
            continue

    ## To reliably determine if any apps were deferred, remove non-app keys from the promptOutput object
    promptMetaKeys = ["SelectedIndex", "SelectedOption", "Defer Unselected Apps:"]
    promptedApps = [x for x in promptOutput if x not in promptMetaKeys]

    if not all([x for x in promptedApps]):
        setDeferral(promptOutput["Defer Unselected Apps:"]["selectedIndex"])
    else:
        removeDaemons()

    if len(dialogProgressList["listItem"]) == 0:
        writeRunReceipt()
        runRecon()
        endRun(
            0,
            "info",
            "No apps to be updated on this run. Updating inventory and exiting...",
        )

    defaultMessage = f"\
{getEmoji('thanksHands')} Thanks!\n\n\
{getEmoji('eyes')} You can track the status of your updates below.\n\n\
{getEmoji('restartIcon')} Any apps we had to close will be re-opened when the update is completed.\n\n\
{getEmoji('greenX')} This message will be dismissed once all updates are done, or you can click \"OK\" to dismiss it now."

    if speedtest:
        totalDownloadSeconds = round(
            (totalDownloadSize / downloadSpeed)
            + (len(dialogProgressList["listItem"]) * 10)
        )
        totalDownloadTime = "{} minutes, {} seconds".format(
            *divmod(totalDownloadSeconds, 60)
        )
        defaultMessage += f"\n\n\n\n\
{getEmoji('hourglass')} The estimated total download time for these updates is {totalDownloadTime}"

    dialogConfig = {
        "title": "Managed App Updates Installing",
        "titlefont": "size=20",
        "messagefont": "size=12",
        "messageposition": "top",
        "position": position,
        "button1text": "OK",
        "infobutton": 0,
        "quitoninfo": 0,
        "moveable": 1,
        "quitkey": "i",
        "listitem": dialogProgressList["listItem"],
    }

    if simpleMode:
        modeConfig = {
            "message": "**App to be Quit and Updated                                                            Update Status**",
            "messagealignment": "center",
            "hideicon": 1,
            "width": "550",
        }

    else:
        global infoboxData
        infoboxData = getDeviceHealth()

        modeConfig = {
            "message": defaultMessage,
            "icon": str(iconPath),
            "iconsize": "120",
            "infobox": infoboxData,
            "hideicon": 0,
            "height": "650",
        }

    dialogConfig.update(modeConfig)

    statusJson = "/var/tmp/status.json"

    Path(statusJson).write_text(json.dumps(dialogConfig))

    statusCmd = [
        str(dialogPath),
        "--jsonfile",
        statusJson,
        "--commandfile",
        str(dialogCommandFile),
        "&",
    ]

    logging.debug("Generating status dialog...")
    logging.debug(f"Status dialog configuration: {loadJson(Path(statusJson))}")
    subprocess.Popen(statusCmd, text=True, start_new_session=True)


## Use the networkQuality utility to measure the user's download bandwidth
## This will be used to calculate progress percentage during download status, and
## to estimate how long the updates will take
def getDownloadSpeed():
    ## Initialize the global variable
    global downloadSpeed

    speedCmd = ["/usr/bin/networkQuality", "-c"]

    logging.info("Testing Internet bandwidth...")
    testResult = json.loads(
        subprocess.run(speedCmd, text=True, capture_output=True).stdout
    )

    ## Get the dl_throughput field from the test data
    downloadSpeedBits = testResult["dl_throughput"]

    ## Divide by 8 to convert bits/s > bytes/s and assign the result to downloadSpeed
    logging.debug(
        f"Current download bandwidth measured at {downloadSpeedBits} bits per second"
    )
    downloadSpeed = round(downloadSpeedBits / 8)


## Create a preferences file to reference during future scheduled/deferred runs using values from this run
def setPrefsFile():
    logging.debug("Checking for existing preferences file...")
    if args.saveprefs or not prefsPath.exists():
        logging.debug("Creating preferences file using current run settings:")
        logging.debug(
            f'Org Name: {orgName}, Dialog Path: {str(dialogPath)}, Icon Path: {str(iconPath)}, Process List: {", ".join(requiredProcessList)}'
        )

        ## Create json preferences from current settings
        runSettings = {
            "org": orgName,
            "dialog": str(dialogPath),
            "icon": str(iconPath),
            "processes": requiredProcessList,
        }

        ## Write out to file
        dumpJson(runSettings, prefsPath)

        prefsExist = True

    elif prefsPath.exists:
        logging.debug("Found existing preferences file")
        prefsExist = True
    else:
        logging.warning(
            "Something went wrong handling the preferences file, but script execution can continue"
        )
        prefsExist = False

    return prefsExist


## Create and load LaunchDaemon(s) for setup mode (scheduled runs)
def setupRunSchedule(setupType):
    logging.debug(f"Creating and loading {setupType} LaunchDaemon")

    ## Set the LaunchDaemon label and file path
    daemonLabel = f"com.{orgName.lower()}.appUpdates.{setupType}Run"
    daemonFile = f"/Library/LaunchDaemons/{daemonLabel}.plist"
    logging.debug(f"Creating daemon at {daemonFile}")

    ## Start constructing the daemon
    daemonData = {
        "Label": daemonLabel,
        "ProgramArguments": [pythonPath, scriptPath],
        "RunAtLoad": True,
    }

    ## If we have a preferences file, use it
    if setPrefsFile():
        logging.info("Using existing preferences file")

        daemonData["ProgramArguments"].append("--prefsfile")
        daemonData["ProgramArguments"].append(str(prefsPath))

    ## Otherwise, use current command-line arguments
    else:
        logging.info("Using command-line preferences")

        prefs = ["--dialog", str(dialogPath), "--icon", str(iconPath), "--org", orgName]

        # for line in prefs:
        daemonData["ProgramArguments"] += prefs

    ## For silent or prompt runs, set the start interval and appropriate run type
    if setupType in ["silent", "prompt"]:
        intervalVar = globals()[f"{setupType}Interval"]
        startCondition = {"StartInterval": int(intervalVar)}
        runType = "--silent" if setupType == "silent" else "--no-silent"

    ## For watch path runs, set the watch path start condition and --silent run type
    elif setupType == "watchpath":
        startCondition = {"WatchPaths": ("/Library/Managed Preferences")}
        runType = "--silent"

    ## Something unexpected was encountered
    else:
        logging.error(f"Something went wrong creating {setupType} LaunchDaemon")
        return 1

    ## Add the start condition and run type to the daemon
    daemonData.update(startCondition)
    daemonData["ProgramArguments"].append(runType)

    ## Convert ProgramArguments to a tuple for proper plistlib ingestion
    daemonData["ProgramArguments"] = tuple(daemonData["ProgramArguments"])

    ## Write out the LaunchDaemon file
    logging.info(f"Creating {setupType} daemon using current run settings")
    dumpPlist(daemonData, Path(daemonFile))

    loadResultCode = loadLaunchDaemon(daemonFile)
    return loadResultCode


## Do the thing
def run():
    ## Make sure the script can run
    if not requirementsCheck():
        endRun(
            1,
            "error",
            "Some requirements were not met. See critical level logging above for details. This script cannot continue.",
        )
    else:
        logging.debug("Requirements met, continuing with execution")

    ## Setting global vars
    global forcePrompt
    global silentRun
    global deferredRun

    ## If setup mode was selected, configure specified LaunchDaemons and exit
    global silentInterval
    global promptInterval

    if any(
        [
            (silentInterval := args.setsilent),
            (promptInterval := args.setprompt),
            args.setwatchpath,
        ]
    ):
        logging.info("Running selected setup actions and exiting...")
        setupCodeSum = 0

        setupTypes = {
            "silent": True if silentInterval else False,
            "prompt": True if promptInterval else False,
            "watchpath": True if args.setwatchpath else False,
        }

        for setupType in [x for x in setupTypes.keys() if setupTypes[x] is True]:
            setupResultCode = setupRunSchedule(setupType)
            setupCodeSum = setupCodeSum + setupResultCode

        endRun(setupCodeSum, "info", "Setup actions complete")

    logging.info("Update attempt started")

    if silentRun:
        logging.info("Silent run is enabled")

    ## Determine what apps need to be updated and what state they're in
    promptList = getUpdateRequirements()

    ## No updates to install? Exit!
    if not promptList:
        runRecon()
        endRun(0, "info", "No prompt list generated, updating inventory and exiting...")

    ## If this is a single-item Self Service run, generate the ultralight interface and install the update
    if selfService:
        logging.info(f"Running Self Service update for {selfService}")

        appData = appListEntries.get(list(appListEntries.keys())[0])
        appName = list(appListEntries.keys())[0]
        bundleID = appData["bundleID"]
        backgroundUpdate = appData["background"]

        dialogConfig = {
            "title": "none",
            "icon": promptList[0]["icon"],
            "message": f'{list(appListEntries.keys())[0]} will be {"quit and " if not backgroundUpdate else ""}updated in 30 seconds.<br>You may click Cancel to stop the update.',
            "mini": True,
            "timer": "30",
            "position": position,
            "button1text": "Update Now",
            "button1disabled": True,
            "button2text": "Cancel",
        }

        promptJson = "/var/tmp/selfserviceprompt.json"

        Path(promptJson).write_text(json.dumps(dialogConfig))

        dialogCmd = ["/opt/chime/bin/dialog", "--jsonfile", promptJson]

        logging.debug("Generating prompt dialog...")
        logging.debug(f"Prompt dialog configuration: {loadJson(Path(promptJson))}")
        prompt = subprocess.run(dialogCmd, text=True, capture_output=True)

        if prompt.returncode == 0:
            logging.info("Self Service update accepted")

            for key in ["timer", "button1text", "button1disabled", "button2text"]:
                dialogConfig.pop(key)

            statusKeys = {
                "progress": 100,
                "message": "Update in progress, please wait...",
            }

            dialogConfig.update(statusKeys)

            statusJson = "/var/tmp/selfservicestatus.json"
            Path(statusJson).write_text(json.dumps(dialogConfig))

            dialogCmd.pop(-1)
            dialogCmd += [statusJson, "--commandfile", dialogCommandFile, "&"]

            logging.debug("Generating status dialog...")
            logging.debug(f"Status dialog configuration: {loadJson(Path(statusJson))}")
            subprocess.Popen(dialogCmd, text=True, start_new_session=True)

            quitApp(bundleID)
            time.sleep(0.5)
            runJamfPolicy(appName)

            updateResult = appListEntries.get(list(appListEntries.keys())[0]).get(
                "result"
            )
            time.sleep(0.5)
            if updateResult == "success":
                updateDialog("Update complete! This window will be dismissed shortly.")
            else:
                updateDialog(
                    "Something went wrong during the update. Please try again. This window will be dismissed shortly."
                )

            if not backgroundUpdate:
                logging.info(f"Relaunching {appName}...")
                reopenCmd = [
                    "/bin/launchctl",
                    "asuser",
                    userUID,
                    "sudo",
                    "-u",
                    userName,
                    "/usr/bin/open",
                    "-g",
                    "-b",
                    bundleID,
                ]
                subprocess.run(reopenCmd, text=True)

        else:
            logging.info("Self Service update was canceled")

        runRecon()
        updateDialog("quit:")
        endRun(
            0,
            "info",
            "Self Service update completed, updating inventory and exiting...",
        )

    ## Determine which updates (if any) can be installed in the background (not currently running)
    backgroundStatus = [appListEntries[x].get("background") for x in appListEntries]

    ## If this is a silent run AND there are updates pending, OR all pending updates can run in the background, update them and exit silently
    if (silentRun and promptList and not forcePrompt) or all(backgroundStatus):
        logging.info("Installing updates in the background...")
        for app in appListEntries.keys():
            runJamfPolicy(app)
        writeRunReceipt()
        runRecon()
        time.sleep(2)
        endRun(0, "info", "Background updates completed")

    ## If the user is in a Zoom meeting, presenting in an app, or has Focus/DND enabled, defer for a random 5-15 minute interval and exit
    if checkInterruptions() and not forcePrompt:
        setDeferral(None)
        time.sleep(2)
        endRun(0, "info", "Interruption check failed after 5 minutes, deferring...")

    ## If the timing of this run is otherwise invalid (see validateRunTiming for details), exit
    if not validateRunTiming() and not forcePrompt:
        endRun(
            0,
            "warning",
            "Invalid run timing. This does not necessarily mean something is wrong, but no prompt will be generated now.",
        )

    ## All checks completed, send the prompt!
    if speedtest:
        getDownloadSpeed()
    userSelections, promptReturnCode = promptForUpdates()

    ## If the timer expires (4) or the user closes the prompt with Cmd + Q (10), update any apps not running or being forced
    ## Defer anything remaining and exit
    if promptReturnCode in [4, 10]:
        logging.warning(
            "Timer expired or user killed dialog; running any background or force updates and deferring the rest..."
        )

        for app in appListEntries.keys():
            appData = appListEntries[app]
            if appData["background"] or appData["force"]:
                logging.info(f"Updating {app} anyway...")
                quitApp(appData["bundleID"])
                runJamfPolicy(app)

        setDeferral(None)
        runRecon()
        time.sleep(2)
        endRun(0, "info", "Set randomized deferral for running apps.")

    ## From the prompt result, determine which apps will be updated and deferred
    parseUserSelections(userSelections)

    ## Finally, update the apps
    for app in appListEntries.keys():
        appData = appListEntries[app]

        if appData["result"] == "deferred":
            continue

        appName = app
        bundleID = appData["bundleID"]
        backgroundUpdate = appData["background"]
        forceUpdate = appData["force"]

        ## If the app is running or update is being forced, close it
        if forceUpdate or not backgroundUpdate:
            quitApp(bundleID)

        ## Call the jamf policy to install the new package
        runJamfPolicy(appName)

        ## If the app was running prior to updating, relaunch it
        if not backgroundUpdate:
            logging.info(f"Relaunching {appName}...")
            reopenCmd = [
                "/bin/launchctl",
                "asuser",
                userUID,
                "sudo",
                "-u",
                userName,
                "/usr/bin/open",
                "-g",
                "-b",
                bundleID,
            ]
            subprocess.run(reopenCmd, text=True)

    ## Clean up and exit
    time.sleep(1)

    updateDialog("list: clear")
    updateDialog("list: All set! Updating inventory and cleaning up...")
    updateDialog("listitem: index: 0, status: wait")
    for appItem in dialogProgressList["listItem"]:
        updateDialog(
            f'listitem: add, title: {appItem["title"]}, icon: {appItem["icon"]}, status: {appItem["status"]}, statustext: {appItem["statustext"]}'
        )

    writeRunReceipt()

    runRecon()

    updateDialog("quit:")
    time.sleep(2)
    endRun(0, "info", "Run completed.")


## Main
if __name__ == "__main__":
    run()