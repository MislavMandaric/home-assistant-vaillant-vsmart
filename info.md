[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintainer-shield]][maintainer]

[![Community Forum][forum-shield]][forum]

{% if installed %}

## Breaking changes in v0.9.0

Updating to v0.9.0 or later release, from any release before v0.9.0, introduces some breaking changes. The list is the following:
* `switch.{thermostat_name}_hwb` is now removed and integrated into `water_heater.{boiler_name}` entity, as one of the operations of the water heater
    * If this switch was used in automations, solution is to change automations to use `water_heater.set_operation_mode` service instead of `switch.turn_on` and `switch.turn_off` - operation mode to turn on HWB is `hot_water_boost`, while any other operation mode turns it off
* `number.{thermostat_name}_dhw_temperature` is now removed and integrated into `water_heater.{boiler_name}` entity, as desired temperature of the water heater
    * If this value was used in automations, solution is to change automations to use `water_heater.set_temperature` service instead of `number.set_native_value`
* `climate.{thermostat_name}` now has only `auto` and `heating` modes, `off` is removed
    * This means thermostat "can't be turned off", but boiler can. Turn it off by setting water heater operation mode to `stand_by` - `water_heater.set_operation_mode(stand_by)`
* `climate.{thermostat_name}` now has only `AWAY` preset (in addition to `NONE`), `SUMMER`, `WINTER` and `HOME` presets are removed
    * To toggle between away and home presets, simply toggle between away and none
    * Other presets are now also water heater operations, which can be set by calling `water_heater.set_operation_mode` service
        * To use `WINTER` preset, use `heating` operation mode
        * To use `SUMMER` preset, use `hot_water_only` operation mode

In addition to these breaking changes, all entities now follow new conventions for naming entities. This **will not** rename any of the existing entities after upgrading, but if the integration is removed and reinstalled, all the entities **will** have the new names, instead of the old names, which will break automations referencing entities by names.

These changes align the integration better with the newly redesigned releases of the Vaillant vSMART app, while also making them more consistent and native to the Home Assistant.

{% endif %}

**This component will set up the following platforms.**

| Platform        | Description                                      |
| --------------- | ------------------------------------------------ |
| `climate`       | Management of Vaillant thermostat.               |
| `select`        | Selector showing currently selected schedule.    |
| `sensor`        | Battery sensor for the thermostat.               |
| `switch`        | On/off switch for schedules.                     |
| `water_heater`  | Management of Vaillant boiler.                   |

{% if not installed %}

## Installation

1. Click "Install this repository in HACS"
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Vaillant vSMART".

{% endif %}

## Configuration is done in the UI

Check out the [community page](https://community.home-assistant.io/t/added-support-for-vaillant-thermostat-how-to-integrate-in-official-release/31858). You can find out how to extract client ID and client secret there.

For Vaillant Vsmart
- Client ID : na_client_android_vaillant
- Client secret : XXXXXXXXXXXXXXXXXXXXXXX (see above)
- Username : MY_VAILLANT_APP_USERNAME
- Password : MY_VAILLANT_APP_PWD
- User prefix : vaillant
- App version : 1.0.4.0

For MiGo
- Client ID : na_client_android_sdbg
- Client secret : XXXXXXXXXXXXXXXXXXXXXXX (see above)
- Username : MY_MIGO_APP_USERNAME
- Password : MY_MIGO_APP_PWD
- User prefix : sdbg
- App version : 1.3.0.4

<!---->

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
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge

[forum]: https://community.home-assistant.io/
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
