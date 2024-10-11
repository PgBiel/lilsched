import enum
import io
import itertools
import functools
import tomllib
import sys
import os
import argparse
import datetime
from typing import NoReturn

class Weekday(enum.IntEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6

def error(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    exit(1)

def parse_weekday(value: str) -> Weekday:
    match value:
        case "Mon" | "Monday":
            return Weekday.Monday
        case "Tue" | "Tuesday":
            return Weekday.Tuesday
        case "Wed" | "Wednesday":
            return Weekday.Wednesday
        case "Thu" | "Thursday":
            return Weekday.Thursday
        case "Fri" | "Friday":
            return Weekday.Friday
        case "Sat" | "Saturday":
            return Weekday.Saturday
        case "Sun" | "Sunday":
            return Weekday.Sunday
        case _:
            error(f"Invalid weekday, expected Mon/Tue/Wed/Thu/Fri/Sat/Sun, got '{value}'")

# Returns [((Sun, 13.5), ["Student A", "Student B"])]
def process(data: dict) -> list[tuple[tuple[Weekday, float], list[str]]]:
    if "students" not in data or not isinstance(data["students"], dict):
        error(f"Expected 'students' as top-level dictionary in data")

    # (Sun, 13.5) not present => no student asked for this time slot
    # (Sun, 13.5) = set("Jason", "Joseph") => both are available here
    availabilities: dict[tuple[Weekday, float], set[str]] = {}
    all_students: set[str] = set()
    students: dict = data["students"]
    for name, info in students.items():
        all_students.add(name)
        if type(info) != dict or "slots" not in info or type(info["slots"]) != list:
            error(f"Invalid student '{name}': missing 'slots' list.")

        slots: list = info["slots"]
        for slot in slots:
            if type(slot) != dict or "weekday" not in slot or "slot" not in slot:
                error(f"Invalid slot for student '{name}': must have 'weekday' and 'slot' keys.")
            if type(slot["weekday"]) != str or type(slot["slot"]) not in (float, int):
                error(f"Invalid slot for student '{name}': weekday must be a string, and slot must be a number (12 for 12:00, 13.5 for 13:30).")
            weekday_str = slot["weekday"]
            weekday = parse_weekday(weekday_str)
            timeslot = float(slot["slot"])
            # Time slot key
            key = (weekday, timeslot)
            if key not in availabilities:
                availabilities[key] = set()
            availabilities[key].add(name)

    # Now, collect the information
    all_slots = list(availabilities.keys())

    def search_combinatorial_pass(n) -> list[tuple[tuple[Weekday, float], list[str]]] | None:
        for items in itertools.combinations(availabilities.items(), n):
            all_available = functools.reduce(set.union, map(lambda x: x[1], items), set())
            if all_available == all_students:
                found_cover_keys = set()
                found_cover = []

                for slot, available in items:
                    found_cover_keys.add(slot)
                    found_cover.append((slot, sorted(available)))

                while len(found_cover_keys) < 3 and len(all_slots) > 0:
                    # Fill missing slots arbitrarily
                    new_slot = all_slots.pop()
                    if new_slot not in found_cover_keys:
                        found_cover_keys.add(new_slot)
                        found_cover.append((new_slot, sorted(availabilities.get(new_slot, set()))))
                return sorted(found_cover, key=lambda x: x[0])
        return None

    # First pass: find a slot with everyone
    res = search_combinatorial_pass(1)

    # Second pass: search all pairs of slots
    if res is None:
        res = search_combinatorial_pass(2)

    # Third pass: search all triples of slots (slowest)
    if res is None:
        res = search_combinatorial_pass(3)

    if res is None:
        res = []

    return res

def main():
    parser = argparse.ArgumentParser(
        description="Pick N time slots where everyone is available."
    )
    parser.add_argument("data", help="TOML data file with available time slots", type=argparse.FileType("rb"))
    res = parser.parse_args()

    tom: dict
    with res.data as f:
        tom = tomllib.load(res.data)

    slots = process(tom)
    if slots == []:
        error("There are no shared slots between the students.")
    else:
        for i, ((weekday, time), students) in enumerate(slots):
            formatted_time = f"{int(time)}:30" if time % 1 == 0.5 else f"{int(time)}:00"
            print(f"Slot {i + 1}: {weekday.name}, {formatted_time} (students: {', '.join(students)})")

if __name__ == "__main__":
    main()
