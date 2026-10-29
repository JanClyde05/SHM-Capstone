# Inactive dashboard scaffold

These three files preserve the earlier dashboard scaffold. The active dashboard is embedded in `../ui_assets.h` and served directly by `../web_server.cpp`; no LittleFS asset upload is required. Edit `ui_assets.h` for active UI changes. See `../../../docs/WEB_INTERFACE.md` for transport, routes and schemas.

Do not upload this directory as a filesystem image over retained research records. LittleFS is used independently for measurement storage.
