"""Names and fixed constants shared by every module. Values come from the spec (§5-§8); never tune them."""

RAW_DAY_FIELDS = ["steps", "weekday", "holiday", "feels_max", "rain_mm", "rain_hours", "wind_max", "cloud_mean", "pm25"]
WEATHER_FIELDS = ["feels_max", "rain_mm", "rain_hours", "wind_max", "cloud_mean"]
TODAY_FIELDS = ["weekday", "holiday", *WEATHER_FIELDS]
FEATURES = [
    "steps_yday_rel", "mean3_rel", "mean7_rel", "active_yday", "streak",
    "weekday", "off_day", *WEATHER_FIELDS, "pm25_yday",
]
WEEKDAY_IDX = FEATURES.index("weekday")
EXCUSES = ("heat", "rain", "air", "workday", "tired")

MISSING_STEPS_BELOW = 200
TARGET_WINDOW = 28
TARGET_MIN_VALID = 20
TARGET_PCT = 70
STREAK_CAP = 7

MIN_HISTORY_ROWS = 60
MAX_HISTORY_ROWS = 1000
MIN_LABELLED = 30
