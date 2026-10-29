#pragma once
#include <Arduino.h>
#include "measurement_types.h"
#include "web_server.h"
void sessionBegin();
void sessionUpdate();
void sessionOnSample(const RawRecord &);
bool sessionBusy();
String sessionGetJson(const String &route);
bool sessionPost(const String &, const WebForm &, String &, int &);
void sessionReloadBaseline();
void sessionInvalidatePrecheck();
