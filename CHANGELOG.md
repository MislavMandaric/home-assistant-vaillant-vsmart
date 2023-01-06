# Changelog

<!--next-version-placeholder-->

## v0.7.0 (2023-01-06)
### Feature
* Add spanish translation ([`5c7511a`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/5c7511a11d49edb1a67423a17543534792a495a0))

## v0.6.3-beta.3 (2022-11-07)
### Fix
* Resolve issue with hass variable not being passed to entity registry because of the wrong helper usage ([`904fc4f`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/904fc4fa34f1e0b6c467852ee34dc36464269dae))

## v0.6.3-beta.2 (2022-11-07)
### Fix
* Replace deprecated async_get_registry call with async_get ([`05fd8a6`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/05fd8a6b2eb50ffba62a0b0f0a549de8f075cbc6))

## v0.6.3-beta.1 (2022-11-05)
### Fix
* Update minimum HA version to 2022.11 because new temperature enum which replaces deprecated constants is used ([`f72c0e7`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/f72c0e785752b3bd04005738112090171cb3d3d1))
* Replaces temperature constant with temperature enum ([`8042aa3`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/8042aa37b5f8bcb4497ddb18ca5486da949d9603))
* Adds integration_type to manifest ([`aacd662`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/aacd662839820ea53bbec2a6d3211dc444961b85))
* Replace async_setup_platforms with async_forward_entry_setups ([`fc8876a`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/fc8876a714564e6907371c050f492ab395a29fc2))

## v0.6.2 (2022-11-05)
### Fix
* Parallel run of prerelease and release because release can't be triggered from multiple branches ([`6cbcc44`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/6cbcc44d789d262466cff5b1d59acd78fd169369))

## v0.6.2-beta.1 (2022-11-05)
### Fix
* Update to new versions of semantic release ([`944d387`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/944d387941c5887a766950c09463bc09772f2f6a))

## v0.6.1 (2022-11-05)
### Fix
* Remove reading measure data manually and use new version of API which syncs data on each getthermostatsdata call to get up-to-date data instead of cached one ([`0aa28ab`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/0aa28abcd43e3d0729755ec2927420d96a53ca07))
* Use proper est_setpoint_temp value for target temperature and fallback to setpoint_temp if it doesn't exist ([`e4b02d1`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/e4b02d1e0a8422ac5489590ff18a52cd6625342f))

## v0.6.0 (2022-07-16)
### Feature
* Updates docs and prepares hacs.json for publishing ([`dbfaaea`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/dbfaaeaf84de3b93899f24a6afda1a3e67aac7d7))

## v0.5.1 (2022-05-15)
### Fix
* Replaces deprecated constants with enums ([`5c202fe`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/5c202fec5f323356615f18cb6f4aa83caeddc4f5))

### Documentation
* Removed secret key ([`fa7d5fe`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/fa7d5fed45118ba808430c564c638db26e04b7bb))
* Add Vaillant and Migo parameters in readme ([`6549a0d`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/6549a0d9b8a95f68643ba1692d134f7468bc4cae))

## v0.5.0 (2022-04-18)
### Feature
* Add french translation ([`6804fe5`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/6804fe594ac0dace1a5d3734b769f45c8cbb1a19))
* Improves existing translations by using predefined HA Core translations and adds new reauth translations. ([`da6b9f9`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/da6b9f9c3284713f7bc07cd0a85f8d32f6f64eb8))
* Adds reauth handler in config flow which is triggered by unauthorized error from the API. ([`e7ea00b`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/e7ea00b414e742be83a471b2d78086777db26140))

## v0.4.1 (2022-04-08)
### Fix
* Fixes issue when comparing temperatures in case setpoint temperature is not set, like in summer mode ([`a00ead5`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/a00ead5ee6d36677eca84885d97160bc0b6c2a5c))
* Removes custom title translation for configuring the integration through the UI ([`bb471f4`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/bb471f40ba42ffeab072b4964619a9b34cc45910))
* Replaces deprecated entity config consts with new enum with the same purpose ([`ef18d97`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/ef18d97db6741b2ec768c22a85799c65196b12b1))

## v0.4.0 (2022-02-20)
### Feature
* Changes start time for measure api to 1h instead of 30mins ([`d7a3daa`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/d7a3daaa89bbf7b7562cf5e9ed23c0b5e999e565))
* Adds debug log for changes of temp measurements ([`cfc81b6`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/cfc81b6bacad69f169c0864b92aadcd5faa38586))

## v0.3.0 (2022-01-22)
### Feature
* Adds getting temperature data from real time measure API ([`e89a3f0`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/e89a3f05fb6f69c3a4948ef32193f2cd30d1992c))

## v0.2.4 (2022-01-02)
### Fix
* Updates library to new version which contains cache control updates ([`99f944c`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/99f944c34f0e8b00f0fbf9dba7ffed4462730c42))

## v0.2.3 (2021-12-31)
### Fix
* Adds no-cache cache control header to all http requests to Vaillant API. ([`f6a1235`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/f6a12352d9c9602012d7a8ded8ed425f802fa08b))

## v0.2.2 (2021-12-29)
### Fix
* Adds debug logging to the climate entity when writing to HA state. ([`29a4e4a`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/29a4e4a3f1f19fda2f611b79ebd0a0e1a5ca87a9))

## v0.2.1 (2021-12-03)
### Fix
* Fixes crash when schedule contains custom profile ([`42449fd`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/42449fd36a0727a613aa933c6195ac6a3b56fd26))

## v0.2.0 (2021-12-02)
### Feature
* Adds dummy updated websocket handler ([`7973553`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/7973553ddf734c2855e9b644c8935ff06b4e50ae))
* Changes websockets to use vaillant vsmart specific domain url ([`e2a4dc5`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/e2a4dc5da92866edfbd7d2535816a427d928d9c9))
* Adds POC backend for supporting scheduler-card Lovelace cards ([`9f8efef`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/9f8efef8ff74fd7a4311b37f87f0a4c4ab895eb4))
* Adds profile select entity which shows currently active profile for a schedule ([`273ee17`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/273ee17b4c97d863f0d2f2b7627f594bcf96dba2))
* Adds switch entity for each schedule defined for a thermostat ([`cf6b108`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/cf6b1084db8b1c9547c710e153e3585c828dc594))

### Fix
* Changes select schedule entity to type diagnostic ([`1384e45`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/1384e45ee4453cc59ff73286cdc0eaa67342fe1c))

### Documentation
* Adds credits for people who contributed API docs to readme ([`6b940d4`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/6b940d47910c4ac45576c91815c6110033284cad))

## v0.1.1 (2021-11-19)
### Fix
* Fixes automated release config. ([`06193b0`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/06193b0f531d7df25f0c06571336f3640ae097bf))

## v0.1.0 (2021-11-19)
### Feature
* Adds battery level sensor ([`0a89d09`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/0a89d09e86c9c8f38c0e4eafe2f9e68803e33a94))
* Adds entity category to HWB switch ([`91c65a7`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/91c65a77f40adf84b831eb45b41a203c4f624ee5))
* Upgrades api library to new version without authlib, refactors integration to use it ([`bacd6af`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/bacd6afb9789ea2b9cc8fdbbeea593aa849fc51b))
* Improves error handling and logging; updates library with better timeouts and request retries ([`878f455`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/878f455ce7531024f3d3ce353b385721cfc2745d))
* Adds HWB switch to the component ([`6b9910e`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/6b9910eb53fd2eb1755ff763012af8377940725c))
* Adds translations ([`e8def47`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/e8def47e0c5bae5c201dd1ef7bcd28a769d18af6))
* Adds manifest ([`ef3ea0d`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/ef3ea0d39131fd1d5222baa4bbbd5d1b5138ae54))
* Refactors and adds required integration code ([`ad34ebf`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/ad34ebfd67242d97a93b7b85f66af1db40e87919))

### Fix
* Fixes switch import issue ([`5d9159e`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/5d9159e05ef1497bb4537c878b46053e17586a57))
* Updates library to include sanitized logging ([`1bbe3be`](https://github.com/MislavMandaric/home-assistant-vaillant-vsmart/commit/1bbe3bebc1741cdd831df8a10d1a37926e4e6373))
