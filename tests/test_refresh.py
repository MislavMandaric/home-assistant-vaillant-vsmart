"""Test refresh scheduling, options, and firmware registry compatibility."""
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
import voluptuous as vol
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vaillant_vsmart.config_flow import VaillantOptionsFlow
from custom_components.vaillant_vsmart.const import CONF_REFRESH_DELAY, DOMAIN
from custom_components.vaillant_vsmart.entity import (
    VaillantCoordinator,
    VaillantDeviceEntity,
    VaillantMeasurementEntity,
    VaillantModuleEntity,
    VaillantProgramEntity,
)


async def test_follow_up_refresh(hass):
    """A second read replaces a stale immediate result after the delay."""
    coordinator = VaillantCoordinator(hass, Mock(), refresh_delay=7)
    coordinator.async_request_refresh = AsyncMock()
    cancel = Mock()
    with patch('custom_components.vaillant_vsmart.entity.async_call_later', return_value=cancel) as later:
        await coordinator.async_refresh_after_change()
        coordinator.async_request_refresh.assert_awaited_once()
        assert later.call_args.args[:2] == (hass, 7)
        await later.call_args.args[2](datetime.now())
        assert coordinator.async_request_refresh.await_count == 2
        coordinator.async_cancel_follow_up_refresh()
        cancel.assert_not_called()


async def test_replace_and_cancel_refresh(hass):
    """Further changes replace a timer; unload cancellation is idempotent."""
    coordinator = VaillantCoordinator(hass, Mock())
    coordinator.async_request_refresh = AsyncMock()
    first, second = Mock(), Mock()
    with patch('custom_components.vaillant_vsmart.entity.async_call_later', side_effect=[first, second]):
        await coordinator.async_refresh_after_change()
        await coordinator.async_refresh_after_change()
        first.assert_called_once_with()
        second.assert_not_called()
        coordinator.async_cancel_follow_up_refresh()
        coordinator.async_cancel_follow_up_refresh()
        second.assert_called_once_with()


async def test_disabled_refresh(hass):
    """Zero keeps the immediate refresh and schedules no follow-up."""
    coordinator = VaillantCoordinator(hass, Mock(), refresh_delay=0)
    coordinator.async_request_refresh = AsyncMock()
    with patch('custom_components.vaillant_vsmart.entity.async_call_later') as later:
        await coordinator.async_refresh_after_change()
        coordinator.async_request_refresh.assert_awaited_once()
        later.assert_not_called()


async def test_refresh_options(hass):
    """The options form retains saved values and rejects fractions/negatives."""
    entry = MockConfigEntry(domain=DOMAIN, options={CONF_REFRESH_DELAY: 12})
    flow = VaillantOptionsFlow(entry)
    result = await flow.async_step_init()
    schema = result['data_schema']
    assert schema({}) == {CONF_REFRESH_DELAY: 12}
    for value in (-1, 1.5, '5'):
        with pytest.raises(vol.Invalid):
            schema({CONF_REFRESH_DELAY: value})
    for value in (0, 5, 60):
        assert schema({CONF_REFRESH_DELAY: value}) == {CONF_REFRESH_DELAY: value}
    result = await flow.async_step_init({CONF_REFRESH_DELAY: 0})
    assert result['data'] == {CONF_REFRESH_DELAY: 0}


@pytest.mark.parametrize('firmware,expected', [(123, '123'), ('1.2', '1.2'), (None, None)])
@pytest.mark.parametrize('entity_type', [VaillantDeviceEntity, VaillantModuleEntity, VaillantProgramEntity, VaillantMeasurementEntity])
def test_firmware_version(entity_type, firmware, expected):
    """Every entity base supplies string firmware or an unknown value."""
    module = SimpleNamespace(id='module', module_name='Room', firmware=firmware)
    device = SimpleNamespace(id='device', station_name='Home', firmware=firmware, type='Vaillant')
    coordinator = Mock()
    coordinator.data.devices = {'device': device}
    coordinator.data.modules = {'module': module}
    args = [coordinator, 'device']
    if entity_type is not VaillantDeviceEntity:
        args.append('module')
    if entity_type in (VaillantProgramEntity, VaillantMeasurementEntity):
        args.append('program')
    entity = entity_type(*args)
    assert entity.device_info['sw_version'] == expected


async def test_unload_during_refresh(hass):
    """An action finishing during unload must not schedule a new timer."""
    coordinator = VaillantCoordinator(hass, Mock())
    coordinator.async_request_refresh = AsyncMock(side_effect=coordinator.async_stop_follow_up_refresh)
    with patch('custom_components.vaillant_vsmart.entity.async_call_later') as later:
        await coordinator.async_refresh_after_change()
        later.assert_not_called()
