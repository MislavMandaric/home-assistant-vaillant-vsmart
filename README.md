# Vaillant vSMART

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintainer-shield]][maintainer]

[![Community Forum][forum-shield]][forum]

**This component will set up the following platforms.**

| Platform        | Description                                |
| --------------- | ------------------------------------------ |
| `climate`       | Management of Vaillant thermostat.         |
| `switch`        | Hot water boost switch of the thermostat.  |
| `sensor`        | Battery sensor for the thermostat.         |

## Installation

### HACS (recommended)

1. Open HACS
1. Search for "Vaillant vSMART"
    1. If it doesn't exist yet, you first need to add `https://github.com/MislavMandaric/home-assistant-vaillant-vsmart` as custom repository
1. Click "Install this repository in HACS"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Vaillant vSMART"

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
1. If you do not have a `custom_components` directory (folder) there, you need to create it
1. In the `custom_components` directory (folder) create a new folder called `vaillant_vsmart`
1. Download _all_ the files from the `custom_components/vaillant_vsmart/` directory (folder) in this repository
1. Place the files you downloaded in the new directory (folder) you created
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Vaillant vSMART"

## Configuration is done in the UI

### Informations to add in the integration

For Vaillant Vsmart
- Client ID : na_client_android_vaillant
- Client secret : 929XXXXXXXXXXXXXXXX45f0 (see below)
- Username : MY_VAILLANT_APP_USERNAME
- Password : MY_VAILLANT_APP_PWD
- User prefix : vaillant
- App version : 1.0.4.0

For MiGo
- Client ID : na_client_android_sdbg
- Client secret : 28d36XXXXXXXXXXXXffeb (see below)
- Username : MY_MIGO_APP_USERNAME
- Password : MY_MIGO_APP_PWD
- User prefix : sdbg
- App version : 1.3.0.4

### Finding secret key:

You can ask this thread for additional support if you can't find the key : https://community.home-assistant.io/t/added-support-for-vaillant-thermostat-how-to-integrate-in-official-release

For Vaillant :
- Download this app (do not install!) : https://m.apkpure.com/vaillant-vsmart-control/com.vaillantgroup.vaillant.thermostat/download/3100400-APK
- Change the extension from .apk to .zip (if you don’t see the extension you need to enable the option in windows explorer
- Unzip the file
- Rename classes.dex to classes.txt
- Open the file with an editor such as Notepad++, VS code or Wordpad (it is too big for notepad)
- Search for the string “45f0”
- The secret key is the line starting by 929 and ending by 45f0

For Migo :
- Download this app (do not install!) : https://apkpure.com/migo-your-heating-assistant/com.vaillantgroup.migo.thermostat
- If this is an xapk file just rename it .zip and uncompress it with winzip you will obtain the apk
- Disassemble the apk with your favorite tool. I took google android sdk
- When disassembling work is done search for na_client_android_sdbg
- You will find the KEY of the form : 28d36#######################ffeb. (32 Characters)

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint](https://github.com/custom-components/integration_blueprint) template

This integration is a complete rewrite of [@pjmaenh](https://github.com/pjmaenh)'s original [Vaillant integration](https://github.com/pjmaenh/home-assistant-vaillant).

Thanks to [@philippelt](https://github.com/philippelt), [@jabesq](https://github.com/jabesq), [@samueldumont](https://github.com/samueldumont), [@jabesq](https://github.com/jabesq), [@pjmaenh](https://github.com/pjmaenh) and [@superbunika](https://github.com/superbunika) for providing many details of the underlying API, which this component uses.


[maintainer]: https://github.com/MislavMandaric
[maintainer-shield]: https://img.shields.io/badge/maintainer-%40MislavMandaric-blue.svg?style=for-the-badge

[releases]: https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/releases
[releases-shield]: https://img.shields.io/github/release/MislavMandaric/home-assistant-vaillant-vsmart.svg?style=for-the-badge

[commits]: https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commits
[commits-shield]: https://img.shields.io/github/commit-activity/y/MislavMandaric/home-assistant-vaillant-vsmart.svg?style=for-the-badge

[license]: https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/blob/master/LICENSE
[license-shield]: https://img.shields.io/github/license/MislavMandaric/home-assistant-vaillant-vsmart.svg?style=for-the-badge

[hacs]: https://hacs.xyz
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge

[forum]: https://community.home-assistant.io/
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge

[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge

[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
