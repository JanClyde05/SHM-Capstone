#include <Arduino.h>
#include "app.h"
#include "version.h"
#include "session.h"
#include "storage.h"
#include "acquisition.h"
#include "wifi_manager.h"
#include "web_server.h"
namespace {
bool download(const String &id, const String &kind, fs::File &f, String &mime, String &name) {
    if (sessionBusy() || !storageOpen(id, kind, f))
        return false;
    mime = kind == "raw"       ? "application/octet-stream"
           : kind == "windows" ? "text/csv"
                               : "application/json";
    name = id + "_" + kind + (kind == "raw" ? ".shmb" : kind == "windows" ? ".csv" : ".json");
    return true;
}
String command;
void serialCommands() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\r')
            continue;
        if (c != '\n') {
            if (command.length() < 100)
                command += c;
            continue;
        }
        command.trim();
        if (!sessionBusy()) {
            if (command == "FORMAT_ERASE_ALL") {
                acquisitionSuspend();
                bool ok = storageFormatConfirmed();
                sessionReloadBaseline();
                acquisitionResume();
                sessionInvalidatePrecheck();
                Serial.println(ok ? "Filesystem formatted." : "Format did not complete.");
            } else if (command.startsWith("PURGE_RAW ") && command.endsWith(" CONFIRM")) {
                String id = command.substring(10, command.length() - 8);
                acquisitionSuspend();
                bool ok = storagePurgeRawConfirmed(id);
                acquisitionResume();
                sessionInvalidatePrecheck();
                Serial.println(ok ? "Raw file removed; summary retained."
                                  : "Purge did not complete.");
            } else if (command.length())
                Serial.println(
                    "Commands: FORMAT_ERASE_ALL or PURGE_RAW S123 CONFIRM (after backup).");
        } else
            Serial.println("Command blocked during acquisition or processing.");
        command = "";
    }
}
} // namespace
void appInit() {
    Serial.begin(115200);
    delay(300);
    Serial.printf("\nSHM %s, N16R8 + three MPU6050\n", SHM_FW_VERSION);
    storageBegin();
    sessionBegin();
    acquisitionBegin(sessionOnSample);
    wifiManagerBegin();
    WebApiCallbacks api{};
    api.getJson = sessionGetJson;
    api.postForm = sessionPost;
    api.openDownload = download;
    api.isCapturing = sessionBusy;
    webServerConfigure(api);
    webServerBegin();
    if (!storageReady())
        Serial.println("LittleFS not mounted. For a new/blank device, explicitly send "
                       "FORMAT_ERASE_ALL. This erases all recordings.");
}
void appUpdate() {
    sessionUpdate();
    webServerUpdate();
    wifiManagerUpdate();
    serialCommands();
    delay(1);
}
