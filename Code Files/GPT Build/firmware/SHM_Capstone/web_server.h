#pragma once

#include <Arduino.h>
#include <FS.h>

// Transport strings are validated by app/session before any state change.
struct WebForm {
    String mode, operatorName, weatherNote, stationId, orientation, epoch;
    String vehicleCount, cutoff1, cutoff2, confirm, sessionId;
    String bandLo, bandHi, timingToleranceUs;
};

struct WebApiCallbacks {
    String (*getJson)(const String& route) = nullptr;
    bool (*postForm)(const String& route, const WebForm& form,
                     String& responseJson, int& responseStatus) = nullptr;
    bool (*openDownload)(const String& sessionId, const String& kind,
                         fs::File& file, String& contentType, String& filename) = nullptr;
    bool (*isCapturing)() = nullptr;
};

void webServerConfigure(const WebApiCallbacks& callbacks);
void webServerBegin();
void webServerUpdate();
