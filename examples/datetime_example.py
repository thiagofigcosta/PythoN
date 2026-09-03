#!/bin/python3
# Dates, times and durations.

from datetime import date, datetime, timedelta, timezone

fixed = datetime(2026, 9, 3, 14, 30, 15, tzinfo=timezone.utc)

print("a fixed moment:", fixed.isoformat())
print("its parts:", fixed.year, fixed.month, fixed.day, fixed.hour, fixed.minute)
print("weekday, 0 is Monday:", fixed.weekday())
print("formatted:", fixed.strftime("%Y-%m-%d %H:%M:%S %Z"))

parsed = datetime.strptime("2026-01-15 08:00", "%Y-%m-%d %H:%M")
print("parsed from a string:", parsed.isoformat())

later = fixed + timedelta(days=10, hours=3)
print("ten days and three hours later:", later.isoformat())

span = later - fixed
print("difference:", span, "which is", span.total_seconds(), "seconds")
print("in days:", span.days)

birthday = date(2026, 12, 25)
today = date(2026, 9, 3)
print("days until:", (birthday - today).days)

print("comparison:", fixed < later, fixed == fixed)

meetings = [
    datetime(2026, 9, 3, 9, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 3, 8, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 3, 17, 30, tzinfo=timezone.utc)
]
for moment in sorted(meetings) {
    print("  " + moment.strftime("%H:%M"))
}

durations = {"short": timedelta(minutes=15), "long": timedelta(hours=2)}
for label, duration in sorted(durations.items()) {
    print("  {} lasts {}".format(label, duration))
}
