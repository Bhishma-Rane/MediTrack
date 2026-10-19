#pragma once

// Safe development defaults. Copy config.example.h and edit this file locally
// for a deployment; never commit real Wi-Fi credentials or private endpoints.
#define MEDITRACK_DEVICE_ID "ESP32_MED_01"
#define MEDITRACK_WIFI_SSID "change-me"
#define MEDITRACK_WIFI_PASSWORD "change-me"
#define MEDITRACK_BACKEND_URL "http://192.168.1.10:8000/api/v1/telemetry"
#define MEDITRACK_TZ "UTC0"
#define MEDITRACK_DOSE_HOUR 8
#define MEDITRACK_DOSE_MINUTE 0
#define MEDITRACK_COMPARTMENT 1
#define MEDITRACK_PATIENT_ID 0
#define MEDITRACK_SCHEDULE_ID 0
#define MEDITRACK_ENABLE_CHUTE_SENSOR 1
