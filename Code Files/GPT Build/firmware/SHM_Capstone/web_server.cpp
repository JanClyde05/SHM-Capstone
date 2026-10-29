#include "web_server.h"

#include <WebServer.h>
#include "ui_assets.h"

namespace {
WebServer server(80);
WebApiCallbacks api;
bool begun = false;
bool capturing() { return api.isCapturing && api.isCapturing(); }
void headers() {
    server.sendHeader("Cache-Control", "no-store");
    server.sendHeader("X-Content-Type-Options", "nosniff");
    server.sendHeader("X-Frame-Options", "DENY");
    server.sendHeader("Referrer-Policy", "no-referrer");
}
void json(int status, const String& content) {
    headers();
    server.send(status, "application/json; charset=utf-8", content);
}
void asset(const char* mime, const char* content, size_t length) {
    if (capturing()) { json(409, "{\"message\":\"Open the dashboard before starting capture.\"}"); return; }
    headers();
    server.sendHeader("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'");
    server.send_P(200, mime, content, length);
}
void getJson() {
    if (!api.getJson) { json(503, "{\"message\":\"Application API is not configured.\"}"); return; }
    const String response = api.getJson(server.uri());
    if (response.length() == 0) { json(404, "{\"message\":\"Resource is unavailable.\"}"); return; }
    json(200, response);
}
void postForm() {
    // A custom header requires browser mutations to come from this origin.
    if (server.header("X-SHM-Request") != "local") {
        json(403, "{\"message\":\"Use the local dashboard to submit this request.\"}"); return;
    }
    if (server.header("Content-Type").indexOf("application/x-www-form-urlencoded") != 0) {
        json(415, "{\"message\":\"Expected URL-encoded form fields.\"}"); return;
    }
    if (server.args() > 16) { json(413, "{\"message\":\"Too many fields.\"}"); return; }
    for (int i = 0; i < server.args(); ++i) {
        if (server.arg(i).length() > 256) { json(413, "{\"message\":\"A field exceeds 256 characters.\"}"); return; }
    }
    WebForm form;
    form.mode = server.arg("mode"); form.operatorName = server.arg("operator");
    form.weatherNote = server.arg("weather_note"); form.stationId = server.arg("station_id");
    form.orientation = server.arg("orientation"); form.epoch = server.arg("epoch");
    form.vehicleCount = server.arg("vehicle_count"); form.cutoff1 = server.arg("cutoff1");
    form.cutoff2 = server.arg("cutoff2"); form.confirm = server.arg("confirm");
    form.sessionId = server.arg("session_id"); form.bandLo = server.arg("band_lo");
    form.bandHi = server.arg("band_hi"); form.timingToleranceUs = server.arg("timing_tolerance_us");
    String response; int status = 200;
    if (!api.postForm || !api.postForm(server.uri(), form, response, status)) {
        json(404, "{\"message\":\"Operation is unavailable.\"}"); return;
    }
    json(status, response);
}
bool validId(const String& id) {
    if (id.length() == 0 || id.length() > 64) return false;
    for (size_t i = 0; i < id.length(); ++i) {
        const char c = id[i];
        if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') ||
              (c >= 'a' && c <= 'z') || c == '_' || c == '-')) return false;
    }
    return true;
}
void notFound() {
    const String path = server.uri(); const String prefix = "/api/sessions/";
    if (server.method() != HTTP_GET || !path.startsWith(prefix)) {
        json(404, "{\"message\":\"Resource is unavailable.\"}"); return;
    }
    const int split = path.indexOf('/', prefix.length());
    if (split < 0) { json(404, "{\"message\":\"Record path is incomplete.\"}"); return; }
    const String id = path.substring(prefix.length(), split), kind = path.substring(split + 1);
    if (!validId(id) || (kind != "raw" && kind != "summary" && kind != "windows")) {
        json(400, "{\"message\":\"Record path is invalid.\"}"); return;
    }
    if (capturing()) { json(409, "{\"message\":\"Wait for capture to finish before downloading.\"}"); return; }
    fs::File file; String mime, filename;
    if (!api.openDownload || !api.openDownload(id, kind, file, mime, filename) || !file) {
        json(404, "{\"message\":\"Record file is unavailable.\"}"); return;
    }
    filename.replace("\r", ""); filename.replace("\n", ""); filename.replace("\"", "");
    headers();
    server.sendHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
    server.streamFile(file, mime); file.close();
}
}
void webServerConfigure(const WebApiCallbacks& callbacks) { api = callbacks; }
void webServerBegin() {
    if (begun) return;
    const char* keys[] = {"X-SHM-Request", "Content-Type"}; server.collectHeaders(keys, 2);
    server.on("/", HTTP_GET, [] { asset("text/html; charset=utf-8", SHM_INDEX_HTML, sizeof(SHM_INDEX_HTML)-1); });
    server.on("/index.html", HTTP_GET, [] { asset("text/html; charset=utf-8", SHM_INDEX_HTML, sizeof(SHM_INDEX_HTML)-1); });
    server.on("/style.css", HTTP_GET, [] { asset("text/css; charset=utf-8", SHM_STYLE_CSS, sizeof(SHM_STYLE_CSS)-1); });
    server.on("/app.js", HTTP_GET, [] { asset("application/javascript; charset=utf-8", SHM_APP_JS, sizeof(SHM_APP_JS)-1); });
    const char* reads[] = {"/api/status", "/api/live", "/api/sessions", "/api/baseline", "/api/config"};
    for (const char* path : reads) server.on(path, HTTP_GET, getJson);
    const char* writes[] = {"/api/session/precheck", "/api/session/start", "/api/session/stop", "/api/session/finalize", "/api/config/freeze"};
    for (const char* path : writes) server.on(path, HTTP_POST, postForm);
    server.onNotFound(notFound); server.begin(); begun = true;
}
void webServerUpdate() { if (begun) server.handleClient(); }
