#pragma once

#include <Arduino.h>

void wifiManagerBegin();
void wifiManagerUpdate();
bool wifiManagerIsReady();
String wifiManagerSsid();
String wifiManagerAddress();
