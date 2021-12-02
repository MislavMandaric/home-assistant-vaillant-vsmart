# Changelog

<!--next-version-placeholder-->

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
