#pragma once

// Copy to include/config.h for a local build. Do not put credentials in git.
#define MEDITRACK_DEVICE_ID "ESP32_MED_01"
#define MEDITRACK_WIFI_SSID "change-me"
#define MEDITRACK_WIFI_PASSWORD "change-me"
#define MEDITRACK_BACKEND_URL "http://192.168.1.10:8000/api/v1/telemetry"

// NTP uses UTC; the due hour/minute are UTC unless your backend/device policy
// chooses a different TZ string. Set MEDITRACK_TZ to a POSIX TZ value.
#define MEDITRACK_TZ "UTC0"
#define MEDITRACK_DOSE_HOUR 8
#define MEDITRACK_DOSE_MINUTE 0
#define MEDITRACK_COMPARTMENT 1
#define MEDITRACK_PATIENT_ID 0
#define MEDITRACK_SCHEDULE_ID 0
#define MEDITRACK_ENABLE_CHUTE_SENSOR 1
