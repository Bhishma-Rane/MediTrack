#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <HTTPClient.h>
#include <LittleFS.h>
#include <Preferences.h>
#include <Adafruit_SH110X.h>
#include <WiFi.h>
#include <time.h>
#include "config.h"

namespace Pins { constexpr uint8_t SDA=21, SCL=22, LID=18, BUZZER=19, CHUTE=27;
constexpr uint8_t CONFIRM=4, MUTE=16, SNOOZE=17, GREEN=2, RED=15;
constexpr uint8_t SERVO[3]={23,25,26}; }
constexpr bool LID_CLOSED_LEVEL = LOW;
constexpr uint32_t DEBOUNCE_MS=50, WIFI_RETRY_MS=15000, NTP_RETRY_MS=60000;
constexpr uint32_t GATE_SETTLE_MS=900, CHUTE_TIMEOUT_MS=5000, ALARM_MS=250;
constexpr size_t QUEUE_LIMIT=64*1024;
const char *QUEUE_FILE="/telemetry.queue", *QUEUE_TMP="/telemetry.tmp";

enum class State : uint8_t { IDLE, DOSE_DUE, WAITING_FOR_CONFIRM, CHECK_LID, DISPENSING,
  WAITING_FOR_CHUTE, CLOSE_GATE, DISPENSE_CONFIRMED, DISPENSE_UNCONFIRMED, FAULT };
const char *stateName(State s) { static const char* n[]={"IDLE","DOSE_DUE","WAITING_FOR_CONFIRM","CHECK_LID","DISPENSING","WAITING_FOR_CHUTE","CLOSE_GATE","DISPENSE_CONFIRMED","DISPENSE_UNCONFIRMED","FAULT"}; return n[(uint8_t)s]; }

Adafruit_SH1106G oled(128,64,&Wire,-1); Preferences prefs; Servo servos[3];
State state=State::IDLE; uint8_t compartment=MEDITRACK_COMPARTMENT; uint32_t stateSince=0;
bool chuteSeen=false, doseHandled=false; String handledDay; uint32_t lastWifi=0,lastNtp=0,lastHeartbeat=0,lastAlarm=0;
struct Button { uint8_t pin; bool stable=true, last=true; uint32_t changed=0; } buttons[]={{Pins::CONFIRM},{Pins::MUTE},{Pins::SNOOZE}};

bool pressed(Button &b) { bool now=digitalRead(b.pin); if(now!=b.last){b.last=now;b.changed=millis();} if(millis()-b.changed>=DEBOUNCE_MS && now!=b.stable){b.stable=now;return now==LOW;} return false; }
bool lidClosed(){ return digitalRead(Pins::LID)==LID_CLOSED_LEVEL; }
String dayKey(){ struct tm t; if(!getLocalTime(&t,10)) return "unknown"; char b[16]; strftime(b,sizeof(b),"%Y-%m-%d",&t); return b; }
String isoNow(){ struct tm t; if(!getLocalTime(&t,10)) return "1970-01-01T00:00:00Z"; char b[32]; strftime(b,sizeof(b),"%Y-%m-%dT%H:%M:%SZ",&t); return b; }
void persist(){ prefs.putUChar("state",(uint8_t)state); prefs.putString("day",handledDay); prefs.putUChar("comp",compartment); }
void transition(State next){ state=next; stateSince=millis(); persist(); }
void display(const char* line){ oled.clearDisplay(); oled.setTextSize(1); oled.setTextColor(SH110X_WHITE); oled.setCursor(0,0); oled.println("MediTrack"); oled.println(stateName(state)); oled.println(line); oled.display(); }
void alarm(bool on){ digitalWrite(Pins::BUZZER,on); digitalWrite(Pins::RED,on); }
void gatesClosed(){ for(auto &s:servos) s.write(5); }
void gateOpen(){ if(compartment>=1 && compartment<=3) servos[compartment-1].write(90); }

bool postOrQueue(const String &payload){
  if(WiFi.status()!=WL_CONNECTED || String(MEDITRACK_BACKEND_URL).length()==0) return false;
  HTTPClient http; http.setTimeout(2500); if(!http.begin(MEDITRACK_BACKEND_URL)) return false;
  http.addHeader("Content-Type","application/json"); int code=http.POST(payload); http.end(); return code>=200 && code<300;
}
bool queuePayload(const String &payload){
  File f=LittleFS.open(QUEUE_FILE,"a"); if(!f) return false; if(f.size()+payload.length()+1>QUEUE_LIMIT){f.close();return false;} f.println(payload); f.close(); return true;
}
void telemetry(const char *event){
  JsonDocument d; d["device_id"]=MEDITRACK_DEVICE_ID; d["event"]=event; d["timestamp"]=isoNow(); d["compartment"]=compartment;
  if(MEDITRACK_PATIENT_ID>0)d["patient_id"]=MEDITRACK_PATIENT_ID; if(MEDITRACK_SCHEDULE_ID>0)d["schedule_id"]=MEDITRACK_SCHEDULE_ID;
  char id[64]; snprintf(id,sizeof(id),"%s-%lu-%s",MEDITRACK_DEVICE_ID,(unsigned long)millis(),event); d["event_id"]=id; String p; serializeJson(d,p); if(!postOrQueue(p)) queuePayload(p);
}
void replayQueue(){ if(WiFi.status()!=WL_CONNECTED || !LittleFS.exists(QUEUE_FILE)) return; File in=LittleFS.open(QUEUE_FILE,"r"), out=LittleFS.open(QUEUE_TMP,"w"); if(!in||!out){in.close();out.close();return;} bool blocked=false; while(in.available()){String line=in.readStringUntil('\n');line.trim();if(!line.length())continue; if(!blocked && postOrQueue(line))continue; blocked=true;out.println(line);} in.close();out.close();LittleFS.remove(QUEUE_FILE);LittleFS.rename(QUEUE_TMP,QUEUE_FILE); }

void connectWifi(){ if(WiFi.status()==WL_CONNECTED)return; if(millis()-lastWifi<WIFI_RETRY_MS)return; lastWifi=millis(); WiFi.mode(WIFI_STA); WiFi.begin(MEDITRACK_WIFI_SSID,MEDITRACK_WIFI_PASSWORD); }
void syncClock(){ if(WiFi.status()!=WL_CONNECTED || millis()-lastNtp<NTP_RETRY_MS)return; lastNtp=millis(); configTzTime(MEDITRACK_TZ,"pool.ntp.org","time.nist.gov"); }
bool dueNow(){ struct tm t; if(!getLocalTime(&t,10))return false; String today=dayKey(); if(today==handledDay)return false; return t.tm_hour==MEDITRACK_DOSE_HOUR && t.tm_min==MEDITRACK_DOSE_MINUTE; }

void setup(){ Serial.begin(115200); pinMode(Pins::LID,INPUT_PULLUP); pinMode(Pins::CHUTE,INPUT_PULLUP); pinMode(Pins::BUZZER,OUTPUT); pinMode(Pins::GREEN,OUTPUT);pinMode(Pins::RED,OUTPUT); for(auto &b:buttons)pinMode(b.pin,INPUT_PULLUP);
  Wire.begin(Pins::SDA,Pins::SCL); oled.begin(0x3C,true); oled.clearDisplay(); oled.display(); LittleFS.begin(true); prefs.begin("meditrack",false); handledDay=prefs.getString("day",""); compartment=prefs.getUChar("comp",MEDITRACK_COMPARTMENT); State saved=(State)prefs.getUChar("state",0); state=(saved==State::IDLE)?State::IDLE:State::FAULT; stateSince=millis(); for(uint8_t i=0;i<3;i++){servos[i].setPeriodHertz(50);servos[i].attach(Pins::SERVO[i],500,2400);servos[i].write(5);} display("Starting safely"); connectWifi(); }

void loop(){ uint32_t now=millis(); connectWifi(); syncClock(); replayQueue(); if(now-lastHeartbeat>300000){lastHeartbeat=now;telemetry("DEVICE_HEARTBEAT");}
  if(pressed(buttons[0]) && state==State::FAULT){ alarm(false); transition(State::IDLE); }
  if(pressed(buttons[1])||pressed(buttons[2])){ if(state==State::DOSE_DUE||state==State::WAITING_FOR_CONFIRM){handledDay=dayKey();telemetry("DOSE_SNOOZED");transition(State::IDLE);} }
  if(state==State::IDLE){digitalWrite(Pins::GREEN,HIGH);digitalWrite(Pins::RED,LOW);alarm(false);gatesClosed(); if(dueNow())transition(State::DOSE_DUE);}
  else if(state==State::DOSE_DUE){alarm((now/ALARM_MS)%2);display("Dose due - confirm");transition(State::WAITING_FOR_CONFIRM);}
  else if(state==State::WAITING_FOR_CONFIRM){alarm((now/ALARM_MS)%2);display("Press confirm");if(pressed(buttons[0]))transition(State::CHECK_LID);}
  else if(state==State::CHECK_LID){alarm(false);display("Close lid to continue");if(!lidClosed())transition(State::FAULT);else{telemetry("DISPENSE_ATTEMPTED");gateOpen();transition(State::DISPENSING);}}
  else if(state==State::DISPENSING){display("Dispensing");if(!lidClosed()||now-stateSince>3000)transition(State::FAULT);else{chuteSeen=false;transition(State::WAITING_FOR_CHUTE);}}
  else if(state==State::WAITING_FOR_CHUTE){display("Checking chute");if(MEDITRACK_ENABLE_CHUTE_SENSOR && digitalRead(Pins::CHUTE)==LOW)chuteSeen=true;if(chuteSeen||!MEDITRACK_ENABLE_CHUTE||now-stateSince>CHUTE_TIMEOUT_MS)transition(State::CLOSE_GATE);}
  else if(state==State::CLOSE_GATE){gatesClosed();display("Closing gate");if(now-stateSince>GATE_SETTLE_MS)transition(chuteSeen?State::DISPENSE_CONFIRMED:State::DISPENSE_UNCONFIRMED);}
  else if(state==State::DISPENSE_CONFIRMED){digitalWrite(Pins::GREEN,HIGH);display("Object confirmed");telemetry("DISPENSE_CONFIRMED");handledDay=dayKey();transition(State::IDLE);}
  else if(state==State::DISPENSE_UNCONFIRMED){digitalWrite(Pins::RED,HIGH);display("Not confirmed");telemetry("DISPENSE_UNCONFIRMED");handledDay=dayKey();transition(State::IDLE);}
  else if(state==State::FAULT){gatesClosed();alarm((now/ALARM_MS)%2);display("FAULT: inspect, confirm");}
}
