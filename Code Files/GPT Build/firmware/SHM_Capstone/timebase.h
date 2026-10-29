#pragma once
#include <stdint.h>
uint64_t timebaseNowUs();
void timebaseSetEpoch(uint64_t epochSeconds);
uint64_t timebaseEpochSeconds();
