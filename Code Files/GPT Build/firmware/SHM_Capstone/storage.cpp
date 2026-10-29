#include <LittleFS.h>
#include "storage.h"
#include "config.h"
namespace {
bool mounted = false;
}
bool storageBegin() {
    mounted = LittleFS.begin(false);
    return mounted;
}
bool storageReady() {
    return mounted;
}
size_t storageFreeBytes() {
    return mounted ? LittleFS.totalBytes() - LittleFS.usedBytes() : 0;
}
bool storageValidId(const String &id) {
    if (id.length() < 2 || id.length() > 16 || id[0] != 'S')
        return false;
    for (unsigned i = 1; i < id.length(); ++i)
        if (!isDigit(id[i]))
            return false;
    return true;
}
bool storageCreateSession(const String &id) {
    return mounted && storageValidId(id) && !LittleFS.exists("/" + id) && LittleFS.mkdir("/" + id);
}
bool storageSaveRaw(const String &id, const RawRecord *raw, uint32_t count, uint64_t start,
                    uint32_t *crc) {
    if (!mounted || !storageValidId(id))
        return false;
    size_t bytes = size_t(count) * sizeof(RawRecord);
    if (storageFreeBytes() < bytes + sizeof(RawHeader) + 131072)
        return false;
    auto file = LittleFS.open("/" + id + "/raw.shmb", "w");
    if (!file)
        return false;
    RawHeader h{{'S', 'H', 'M', 'R', 'A', 'W', '2', 0}, 2, 32, start, SHM_SESSION_SECONDS, 3};
    bool ok = file.write(reinterpret_cast<const uint8_t *>(&h), sizeof(h)) == sizeof(h);
    const auto *p = reinterpret_cast<const uint8_t *>(raw);
    uint32_t c = 0xffffffff;
    for (size_t pos = 0; ok && pos < bytes;) {
        size_t n = bytes - pos;
        if (n > 4096)
            n = 4096;
        ok = file.write(p + pos, n) == n;
        // EQ-CRC-01 CRC32/ISO-HDLC, corruption check only.
        for (size_t i = 0; i < n; ++i) {
            c ^= p[pos + i];
            for (int b = 0; b < 8; ++b)
                c = (c >> 1) ^ (0xedb88320u & uint32_t(-int32_t(c & 1)));
        }
        pos += n;
        delay(1);
    }
    file.flush();
    file.close();
    if (crc)
        *crc = c ^ 0xffffffff;
    return ok;
}
bool storageWriteText(const String &id, const char *name, const String &text) {
    if (!mounted || !storageValidId(id))
        return false;
    String target = "/" + id + "/" + name, tmp = target + ".tmp";
    auto f = LittleFS.open(tmp, "w");
    if (!f)
        return false;
    bool ok = f.print(text) == text.length();
    f.flush();
    f.close();
    if (!ok)
        return false;
    return LittleFS.rename(tmp, target);
}
bool storageOpen(const String &id, const String &kind, fs::File &file) {
    if (!mounted || !storageValidId(id))
        return false;
    const char *suffix = kind == "raw"       ? "raw.shmb"
                         : kind == "windows" ? "windows.csv"
                         : kind == "summary" ? "summary.json"
                                             : nullptr;
    if (!suffix)
        return false;
    file = LittleFS.open("/" + id + "/" + suffix, "r");
    return bool(file);
}
bool storageFormatConfirmed() {
    LittleFS.end();
    mounted = false;
    if (!LittleFS.format())
        return false;
    return storageBegin();
}
bool storagePurgeRawConfirmed(const String &id) {
    return mounted && storageValidId(id) && LittleFS.remove("/" + id + "/raw.shmb");
}
