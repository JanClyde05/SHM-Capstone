#include "wifi_manager.h"
#include <WiFi.h>
#include <Preferences.h>
#include <esp_random.h>
#include <string.h>

namespace {
bool ready = false;
String ssid;
constexpr char alphabet[] = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";

bool credentialValid(const String &password) {
    if (password.length() != 16)
        return false;
    for (size_t i = 0; i < password.length(); ++i) {
        if (strchr(alphabet, password[i]) == nullptr)
            return false;
    }
    return true;
}

String generatePassword() {
    char bytes[17];
    for (size_t i = 0; i < sizeof(bytes) - 1; ++i) {
        uint8_t byte;
        // Rejection sampling avoids modulo bias for the credential alphabet.
        do {
            esp_fill_random(&byte, 1);
        } while (byte >= (256 / (sizeof(alphabet) - 1)) * (sizeof(alphabet) - 1));
        bytes[i] = alphabet[byte % (sizeof(alphabet) - 1)];
    }
    bytes[16] = '\0';
    String result(bytes);
    memset(bytes, 0, sizeof(bytes));
    return result;
}

void stopWithMessage(const char *message) {
    ready = false;
    WiFi.mode(WIFI_OFF);
    Serial.println(message);
}
} // namespace

void wifiManagerBegin() {
    if (ready)
        return;
    WiFi.persistent(false);
    WiFi.setHostname("shm-monitor");
    Preferences network;
    if (!network.begin("shm-network", false)) {
        stopWithMessage(
            "Network credential storage unavailable; local access point remains stopped.");
        return;
    }
    String password;
    if (network.isKey("ap-pass")) {
        password = network.getString("ap-pass", "");
        if (!credentialValid(password)) {
            network.end();
            stopWithMessage("Stored network credential unreadable; local access point remains "
                            "stopped. See the credential recovery guide.");
            return;
        }
    } else {
        // Enable RF without an AP while obtaining first-use entropy.
        if (!WiFi.mode(WIFI_STA)) {
            network.end();
            stopWithMessage("Radio initialization incomplete; local access point remains stopped.");
            return;
        }
        password = generatePassword();
        const size_t stored = network.putString("ap-pass", password);
        const String readback = network.getString("ap-pass", "");
        if (stored != password.length() || readback != password || !credentialValid(readback)) {
            network.end();
            stopWithMessage("Network credential could not be verified in storage; local access "
                            "point remains stopped.");
            return;
        }
    }
    network.end();
    char name[24];
    snprintf(name, sizeof(name), "SHM-%06lX",
             static_cast<unsigned long>(ESP.getEfuseMac() & 0xFFFFFF));
    ssid = name;
    if (!WiFi.mode(WIFI_AP)) {
        stopWithMessage("Access-point radio initialization incomplete.");
        return;
    }
    ready = WiFi.softAP(ssid.c_str(), password.c_str(), 1, 0, 2);
    if (ready) {
        Serial.printf("\nLocal dashboard SSID: %s\nStored network password: %s\nOpen http://%s/\n",
                      ssid.c_str(), password.c_str(), WiFi.softAPIP().toString().c_str());
    } else {
        stopWithMessage("Local access point did not start.");
    }
}

void wifiManagerUpdate() { /* AP-only operation; no blocking scan/reconnect loop. */
}
bool wifiManagerIsReady() {
    return ready;
}
String wifiManagerSsid() {
    return ssid;
}
String wifiManagerAddress() {
    return ready ? WiFi.softAPIP().toString() : String();
}
