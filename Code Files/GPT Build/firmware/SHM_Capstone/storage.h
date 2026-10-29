#pragma once
#include <Arduino.h>
#include <FS.h>
#include "measurement_types.h"
bool storageBegin();
bool storageReady();
size_t storageFreeBytes();
bool storageCreateSession(const String &id);
bool storageSaveRaw(const String &, const RawRecord *, uint32_t, uint64_t, uint32_t *);
bool storageWriteText(const String &, const char *, const String &);
bool storageOpen(const String &, const String &, fs::File &);
bool storageValidId(const String &);
bool storageFormatConfirmed();
bool storagePurgeRawConfirmed(const String &);
