/*
 * ============================================================
 * main.ino  —  v2 (UPDATED)
 *
 * CHANGE vs v1:
 *   taskSignalProcessing:
 *     OLD:  if (result.anomaly)    → fired every ~2.5 s per node
 *     NEW:  if (result.newAnomaly) → fires ONCE per anomaly event
 *
 *   This is the firmware-side fix for the popup spam issue.
 *   The newAnomaly flag is a rising-edge signal set in
 *   sp_computeNode() and cleared by the hysteresis state machine
 *   only when the anomaly fully resolves.
 *
 * All other code is identical to v1.
 * ============================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <esp_heap_caps.h>

#include "imu_manager.h"
#include "signal_processing.h"
#include "websocket_server.h"

// ── Shared data arrays ────────────────────────────────────────
IMUData       g_latestIMUData [NUM_SENSORS];
ProcessedData g_processedData [NUM_SENSORS];

// ── Synchronisation ───────────────────────────────────────────
SemaphoreHandle_t g_dataMutex;
SemaphoreHandle_t g_processingReady;

// ── Task handles ──────────────────────────────────────────────
TaskHandle_t g_hSensorAcq;
TaskHandle_t g_hSigProc;
TaskHandle_t g_hWSStream;

// ── Forward declarations ──────────────────────────────────────
void taskSensorAcquisition (void *pvParameters);
void taskSignalProcessing  (void *pvParameters);
void taskWebSocketStream   (void *pvParameters);

// ============================================================
// SETUP
// ============================================================

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {}

    Serial.println(F("\n"
        "╔══════════════════════════════════════════════════╗\n"
        "║  ESP32-S3  Structural Health Monitoring v2       ║\n"
        "║  9× MPU6050  |  FreeRTOS  |  WebSocket Stream   ║\n"
        "╚══════════════════════════════════════════════════╝\n"));

    Serial.printf("[Main] Free heap at boot: %u bytes\n", esp_get_free_heap_size());

    Wire.begin(21, 22);
    Wire.setClock(400000UL);
    Wire.setTimeOut(3000);
    Serial.println("[Main] I2C bus: SDA=GPIO21, SCL=GPIO22, 400 kHz");

    g_dataMutex       = xSemaphoreCreateMutex();
    g_processingReady = xSemaphoreCreateBinary();
    configASSERT(g_dataMutex       != NULL);
    configASSERT(g_processingReady != NULL);

    memset(g_latestIMUData, 0, sizeof(g_latestIMUData));
    memset(g_processedData, 0, sizeof(g_processedData));

    imu_init();
    signal_processing_init();
    websocket_server_init();

    imu_printStatus();
    Serial.printf("[Main] Free heap after init: %u bytes\n\n",
                  esp_get_free_heap_size());

    BaseType_t rc;

    rc = xTaskCreatePinnedToCore(
        taskSensorAcquisition, "SensorAcq",
        8192, NULL, 3, &g_hSensorAcq, 0);
    configASSERT(rc == pdPASS);

    rc = xTaskCreatePinnedToCore(
        taskSignalProcessing, "SigProc",
        20480, NULL, 2, &g_hSigProc, 1);
    configASSERT(rc == pdPASS);

    rc = xTaskCreatePinnedToCore(
        taskWebSocketStream, "WSStream",
        8192, NULL, 1, &g_hWSStream, 1);
    configASSERT(rc == pdPASS);

    Serial.println("[Main] All tasks created. System operational.\n");
}

// ============================================================
// LOOP  — diagnostics only
// ============================================================

void loop() {
    static uint32_t lastDiag = 0;
    if (millis() - lastDiag >= 10000) {
        lastDiag = millis();
        Serial.printf("[Diag] Uptime=%lus | Heap=%u | WiFi clients=%d\n",
                      millis() / 1000,
                      esp_get_free_heap_size(),
                      ws_getConnectedClients());
        Serial.printf("[Diag] Stack HWM — SensorAcq:%u SigProc:%u WSStream:%u\n",
                      uxTaskGetStackHighWaterMark(g_hSensorAcq) * sizeof(StackType_t),
                      uxTaskGetStackHighWaterMark(g_hSigProc)   * sizeof(StackType_t),
                      uxTaskGetStackHighWaterMark(g_hWSStream)   * sizeof(StackType_t));
    }
    vTaskDelay(pdMS_TO_TICKS(250));
}

// ============================================================
// TASK 1: SENSOR ACQUISITION  (Core 0, Priority 3)
// ============================================================

void taskSensorAcquisition(void *pvParameters) {
    Serial.println("[Task|SensorAcq] Started on Core 0");

    const TickType_t PERIOD = pdMS_TO_TICKS(5);
    TickType_t       wake   = xTaskGetTickCount();

    uint32_t scanCount = 0, errCount = 0;
    uint32_t diagTick  = millis();

    while (true) {
        for (int i = 0; i < NUM_SENSORS; i++) {
            IMUData data;
            if (imu_readSensor(i, data)) {
                sp_pushSample(i, data);
                if (xSemaphoreTake(g_dataMutex, pdMS_TO_TICKS(2)) == pdTRUE) {
                    g_latestIMUData[i] = data;
                    xSemaphoreGive(g_dataMutex);
                }
            } else {
                errCount++;
            }
        }

        scanCount++;
        if ((scanCount % RMS_WINDOW) == 0) xSemaphoreGive(g_processingReady);

        if (millis() - diagTick >= 5000) {
            float elapsed = (millis() - diagTick) / 1000.0f;
            Serial.printf("[SensorAcq] %.0f Hz total | %.0f Hz/node | Err: %u\n",
                          scanCount / elapsed,
                          (scanCount / elapsed) / NUM_SENSORS,
                          errCount);
            scanCount = errCount = 0;
            diagTick  = millis();
        }

        vTaskDelayUntil(&wake, PERIOD);
    }
}

// ============================================================
// TASK 2: SIGNAL PROCESSING  (Core 1, Priority 2)
//
// KEY FIX: result.newAnomaly instead of result.anomaly
//   → ws_broadcastAlert fires once per event, not every cycle
// ============================================================

void taskSignalProcessing(void *pvParameters) {
    Serial.println("[Task|SigProc]   Started on Core 1");

    while (true) {
        if (xSemaphoreTake(g_processingReady, pdMS_TO_TICKS(2000)) != pdTRUE) {
            Serial.println("[SigProc] WARNING: semaphore timeout");
            continue;
        }

        for (int i = 0; i < NUM_SENSORS; i++) {
            ProcessedData result;
            bool ok = sp_computeNode(i, result);

            if (ok) {
                if (xSemaphoreTake(g_dataMutex, pdMS_TO_TICKS(10)) == pdTRUE) {
                    g_processedData[i] = result;
                    xSemaphoreGive(g_dataMutex);
                }

                // ─────────────────────────────────────────────────────
                // FIX ②: Use result.newAnomaly (rising edge only),
                //         NOT result.anomaly (which stays true for the
                //         entire duration of the anomaly event).
                //         This ensures ws_broadcastAlert() is called
                //         exactly ONCE per anomaly, not every 2.5 s.
                // ─────────────────────────────────────────────────────
                if (result.newAnomaly) {
                    Serial.printf("[ANOMALY!] Node %d | RMS=%.4f g | "
                                  "Freq=%.2f Hz | Heat=%.1f%%\n",
                                  i, result.rms,
                                  result.dominantFreq,
                                  result.heatmap * 100.0f);

                    char alertMsg[140];
                    snprintf(alertMsg, sizeof(alertMsg),
                             "Node %d — RMS=%.4fg  Freq=%.2fHz  Heat=%.1f%%",
                             i, result.rms,
                             result.dominantFreq,
                             result.heatmap * 100.0f);
                    ws_broadcastAlert(alertMsg);
                }
            }
        }
    }
}

// ============================================================
// TASK 3: WEBSOCKET STREAMING  (Core 1, Priority 1)
// ============================================================

void taskWebSocketStream(void *pvParameters) {
    Serial.println("[Task|WSStream]  Started on Core 1");

    const TickType_t PERIOD = pdMS_TO_TICKS(STREAM_PERIOD_MS);
    TickType_t       wake   = xTaskGetTickCount();

    while (true) {
        ws_sendData(g_latestIMUData, g_processedData, g_dataMutex);
        vTaskDelayUntil(&wake, PERIOD);
    }
}
