[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintainer-shield]][maintainer]

[![Community Forum][forum-shield]][forum]

**This component will set up the following platforms.**

| Platform        | Description                         |
| --------------- | ----------------------------------- |
| `climate`       | Management of Vaillant thermostat.  |

{% if not installed %}

## Installation

1. Click "Install this repository in HACS"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Vaillant vSMART".

{% endif %}

## Configuration is done in the UI

<!---->

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint](https://github.com/custom-components/integration_blueprint) template

This integration is a complete rewrite of [@pjmaenh](https://github.com/pjmaenh)'s original [Vaillant integration](https://github.com/pjmaenh/home-assistant-vaillant).


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
