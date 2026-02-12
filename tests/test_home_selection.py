"""Tests for home selection."""

import pytest
from homeassistant.exceptions import HomeAssistantError
from vaillant_netatmo_api import Home

from custom_components.vaillant_vsmart.entity import VaillantData, _select_home, _select_room


def _make_data(homes: list[Home]) -> VaillantData:
    return VaillantData(client=None, homes=homes, devices=[], measurements={})


def test_select_home_uses_configured_home_id() -> None:
    homes = [
        Home(id="home_a", name="Wildenborch", rooms=[{"id": "room_a"}]),
        Home(id="home_b", name="Wildenborch", rooms=[{"id": "room_b"}]),
    ]
    data = _make_data(homes)

    selected = _select_home(data, "home_b")

    assert selected.id == "home_b"


def test_select_home_raises_when_multiple_homes_without_configuration() -> None:
    homes = [
        Home(id="home_a", name="Wildenborch", rooms=[{"id": "room_a"}]),
        Home(id="home_b", name="Wildenborch", rooms=[{"id": "room_b"}]),
    ]
    data = _make_data(homes)

    with pytest.raises(HomeAssistantError, match="Multiple homes detected"):
        _select_home(data, None)


def test_select_room_uses_first_room() -> None:
    home = Home(
        id="home_a",
        name="Wildenborch",
        rooms=[{"id": "room_a"}, {"id": "room_b"}],
    )

    selected = _select_room(home)
    assert selected.id == "room_a"
