#include <esp_timer.h>
#include "timebase.h"
namespace {
uint64_t epoch = 0, epochAt = 0;
}
uint64_t timebaseNowUs() {
    return esp_timer_get_time();
}
void timebaseSetEpoch(uint64_t seconds) {
    epoch = seconds;
    epochAt = timebaseNowUs();
}
uint64_t timebaseEpochSeconds() {
    return epoch ? epoch + (timebaseNowUs() - epochAt) / 1000000 : 0;
}
