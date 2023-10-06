# SwiftPatch
Keep apps up to date--swiftly and transparently!

## Overview
First, a full wiki with screenshots, customization options, and usage examples will be coming soon! I've been excited to get this project published, so I've opted to release the code first and document second.

I've been a fan of AutoPkg for a long time, and paired with Jamf-Upload (previously JSSImporter), getting apps imported to jamf has been a breeze.
What about keeping end user devices up to date with these apps? Well, that's been more of a headache. A number of solutions have been developed, but I wanted something that is:
- Friendly with a native-looking interface
- Transparent to users both before and during the update process
- Flexible with both deferrals and forced updates
- Effective yet not annoying -- this is the most difficult!

Finding nothing that fit the bill, I decided to take on the challenge.

## How It Works

### Dependencies
In order to use this script, you must have:
- [SwiftDialog](https://github.com/bartreardon/swiftDialog) 2.3.0 or higher
- Python 3 -- I suggest the "recommended" flavor of [MacAdmins Python](https://github.com/macadmins/python), as it includes everything this script needs. This script has been tested with versions 3.10.2 - 3.10.11.
- Jamf Pro

At a high level, this script generates its list of required updates from configuration profiles installed on the device. These profiles are created and deployed as part of my customized [AutoPkg/Jamf-Upload recipes](https://github.com/mhrono/autopkg-recipes).
**This is a known limitation I intend to address!**

For each profile, the script will read the data contained and perform a version comparison to make sure the app _actually_ needs to be updated. For example, if a user installs an update on their own before the next inventory update, jamf will still think the app is out of date. We don't need to update an already-updated app.

Once a list of required updates has been generated, it will be presented to the user with deferral options (if available). The behavior of the update process is configurable per-app in the app's configuration profile.

Updates selected for installation will be shown in a new list, with live progress updates to let the user know what's happening.

## Example Screenshots

<img width="932" alt="prompt" src="https://github.com/mhrono/SwiftPatch/assets/37225540/c5a3bbf9-d195-4b8e-b83e-3f3ccbac4ca1">
<img width="932" alt="progress" src="https://github.com/mhrono/SwiftPatch/assets/37225540/5fc20847-0279-4cad-ab83-33f355ce85a1">
<img width="932" alt="complete" src="https://github.com/mhrono/SwiftPatch/assets/37225540/e0dd92de-c01e-4a0e-91b4-c8437ca04145">

## Getting Started
In lieu of a full wiki, here's how to start testing this script:
- Modify the shebang at the top to point to your Python 3 installation
- Generate a preferences file or assemble your command line arguments (run the script with the -h argument for help)
- Create a policy in jamf to install the updated package. The policy **must** have a custom trigger formatted as `autoupdate-$displayName`. This display name must match the app's configuration profile.
- Create and deploy at least one configuration profile with update metadata. An example plist is in the `Examples` folder of this repo. The following keys in the `com.appUpdates.managedApps.$displayName` domain are required:
  - `bundleID`: The bundle ID of the app
  - `deferLimit`: Number of deferrals allowed before the update is forced. Defaults to `10`.
  - `displayName`: Name of the app
  - `forceUpdate`: Set to 'true' or 'false' as a **string**, not boolean
  - `pkgSize`: Size of the update package in bytes--set to an **integer**. Defaults to `0`.
  - `rollbackVersion`: Set to 'true' or 'false' as a **string**. This feature is not yet implemented and should always be set to false.
  - `targetVersionRegex`: Regex pattern to match the latest version of the app or greater. I use Graham Pugh's [Version Regex Generator](https://github.com/autopkg/grahampugh-recipes/tree/main/CommonProcessors#VersionRegexGenerator) AutoPkg processor to generate this.
  - `targetVersionRegex2` and `targetVersionRegex3` will be populated as spillover if the pattern is too large for jamf to manage
  - `targetVersionString`: The version number for the app's latest version, i.e. `8.10.16`. If version regex is not provided, the script will fall back to this string for version comparisons.
  - `versionKey`: The Info.plist key to use when doing version comparisons. Defaults to `CFBundleShortVersionString`. This key should be set to one of 3 options:
    - `CFBundleVersion`
    - `CFBundleShortVersionString`
    - `/path/to/non/app/binary`: In the case of updates to binaries (such as the aws cli), specify the full path to the binary (ex: `/usr/local/bin/aws`). The script will invoke the binary with common version arguments in an attempt to retrieve the currently-installed version of the binary. This is then used for version comparisons.
- Run the script with the appropriate arguments

## Upcoming Features
This is a not-at-all exhaustive list of features I already have in mind to build:

- Set script preferences using a configuration profile
- Add preference for required macOS update source (Apple catalog, Nudge configuration, or other)
- Add preference or profile key for policy trigger (currently hardcoded to `autoupdate-$appName`)
- Complete implementation of version rollback functionality
- Create more extensible workflow for generating and managing update configuration profiles (i.e. remove the dependency on my own AutoPkg recipes)
- Publish the script as a signed pkg for easier deployment

## Known Issues/Limitations
This list is also not exhaustive:

- Updates occasionally will install out-of-order compared to their display order in the progress window. This does not degrade any functionality, but can be confusing to users.

## Contributing
I'd love to have the community contribute! If there's a feature you'd like to see or issue you're experiencing, please feel free to open an issue.
Alternatively, you're welcome to fork this repo and open a pull request to bring changes upstream.

## Thanks
Thanks to @franton for inspiring the name of this project. I spent lots of time running through possibilities until I settled on shamelessly copying his [SwiftDeploy](https://github.com/franton/SwiftDeploy) name format.

Additionally and in no particular order, from the MacAdmins Slack:
- @tlark
- @grahamrpugh
- @nick.mcspadden
- @bartreardon
- @BigMacAdmin
- @drtaru
- @adamcodega
- @dan-snelson
- All the other fine folks in #autopkg, #python, #jamf-upload, and #swiftdialog
