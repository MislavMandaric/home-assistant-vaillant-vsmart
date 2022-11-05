from datetime import datetime, timedelta

from vaillant_netatmo_api.thermostat import Program, TimeSlot, Zone


def map_program_to_schedule(
    schedule_entity_id: str, profile_entity_id: str, program: Program
) -> dict:
    """TODO"""

    daily_slots = program.get_timeslots_for_today()

    return {
        "schedule_id": program.id,
        "weekdays": ["daily"],
        "timeslots": map_timetable_to_timeslots(
            profile_entity_id,
            daily_slots,
            program.zones,
        ),
        "repeat_type": "repeat",
        "name": program.name,
        "enabled": program.selected,
        "next_entries": map_timetable_to_next_entries(daily_slots),
        "timestamps": map_timetable_to_timestamps(daily_slots),
        "entity_id": schedule_entity_id,
        "tags": [],
    }


def map_timetable_to_timestamps(timetable: list[TimeSlot]) -> list[str]:
    """TODO"""

    timestamps = []

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    for time_slot in timetable:
        d = datetime.combine(today, time_slot.time)

        if time_slot.is_already_started:
            d = datetime.combine(tomorrow, time_slot.time)

        timestamps.append(d.isoformat())

    return timestamps


def map_timetable_to_next_entries(timetable: list[TimeSlot]) -> list[int]:
    """TODO"""

    previous_entries = []
    next_entries = []

    for i, time_slot in enumerate(timetable):
        if time_slot.is_already_started:
            previous_entries.append(i)
        else:
            next_entries.append(i)

    return next_entries + previous_entries


def map_timetable_to_timeslots(
    profile_entity_id: str,
    timetable: list[TimeSlot],
    zones: list[Zone],
) -> list[dict]:
    """TODO"""

    r = []

    for i, time_slot in enumerate(timetable):
        zone_name = ""
        for zone in zones:
            if zone.id == time_slot.id:
                zone_name = zone.name

        next_time_slot = timetable[(i + 1) % len(timetable)]
        r.append(
            {
                "start": format_time(time_slot),
                "stop": format_time(next_time_slot),
                "actions": [
                    {
                        "service": "select.select_option",
                        "entity_id": profile_entity_id,
                        "service_data": {"option": zone_name},
                    }
                ],
            }
        )

    return r


def format_time(time_slot: TimeSlot) -> str:
    """Returns a formatted start time for the time slot."""

    return time_slot.time.isoformat()
