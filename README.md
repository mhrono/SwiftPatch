# SwiftPatch
Keep apps up to date--swiftly and transparently!

## Overview
First, a full wiki with screenshots, customization options, and usage examples will be coming soon! I've been excited to get this project published, so I've opted to release the code first and document second.

I've been a fan of AutoPkg for a long time, and paired with Jamf-Upload (previously JSSUploader), getting apps imported to jamf has been a breeze.
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
- Python 3 -- I suggest the "recommended" flavor of [MacAdmins Python](https://github.com/macadmins/python), as it includes everything this script needs
- Jamf Pro

At a high level, this script generates its list of required updates from configuration profiles installed on the device. These profiles are created and deployed as part of my customized [AutoPkg/Jamf-Upload recipes](https://github.com/mhrono/autopkg-recipes).
**This is a known limitation I intend to address!**

For each profile, the script will read the data contained and perform a version comparison to make sure the app _actually_ needs to be updated. For example, if a user installs an update on their own before the next inventory update, jamf will still think the app is out of date. We don't need to update an already-updated app.

Once a list of required updates has been generated, it will be presented to the user with deferral options (if available). The behavior of the update process is configurable per-app in the app's configuration profile.

Updates selected for installation will be shown in a new list, with live progress updates to let the user know what's happening.

## Upcoming Features
This is a not-at-all exhaustive list of features I already have in mind to build:

- Set script preferences using a configuration profile
- Add preference for required macOS update source (Apple catalog, Nudge configuration, or other)
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
