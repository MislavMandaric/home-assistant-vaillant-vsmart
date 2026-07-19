"""Test Vaillant vSMART entities."""

from custom_components.vaillant_vsmart.entity import _format_firmware_version


def test_format_firmware_version() -> None:
    """Test firmware versions are compatible with the device registry."""

    assert _format_firmware_version(42) == "42"
    assert _format_firmware_version("3.2.1") == "3.2.1"
    assert _format_firmware_version(None) is None
