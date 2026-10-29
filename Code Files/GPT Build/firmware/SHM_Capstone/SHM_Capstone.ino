/*
 * SHM-Capstone Arduino IDE sketch.
 * Module orchestration lives in app.cpp; subsystem logic lives in the
 * adjacent module .cpp/.h files so Arduino IDE can compile the sketch folder.
 */

#include "app.h"

void setup() {
    appInit();
}

void loop() {
    appUpdate();
}
