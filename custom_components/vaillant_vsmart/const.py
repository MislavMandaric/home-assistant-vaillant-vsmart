"""Constants for Vaillant vSMART."""

# Base component constants
NAME = "Vaillant vSMART"
DOMAIN = "vaillant_vsmart"

# Platforms
CLIMATE = "climate"
SWITCH = "switch"
PLATFORMS = [CLIMATE, SWITCH]

# Configuration and options
CONF_APP_VERSION = "app_version"
CONF_USER_PREFIX = "user_prefix"
SCOPE = "read_thermostat write_thermostat"