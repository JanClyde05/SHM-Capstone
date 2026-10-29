# Arduino IDE and global UI standard

The current build uses the normal SHM_Capstone sketch and peer .cpp/.h modules. See ARDUINO_IDE_SETUP.md for exact board menus. ESP32-S3-WROOM-1-N16R8 is confirmed; no PlatformIO configuration is used.

The global visual standard remains the user's Danger Monitoring System V2: dark zinc canvas, restrained surfaces/thin borders, blue live values, green connected/in-range, amber provisional/waiting, rose review/disconnected,8px spacing, monospace numeric measurements and inline SVG. Use offline system font fallbacks. No fake signals, canned peaks or invented records.

Active assets are embedded in ui_assets.h. Built-in WebServer serves HTTP endpoints with modest polling. LittleFS is for research recordings and does not need a web asset image. Previous data/ HTML/CSS/JS is inactive reference. WebSocket can also work with either embedded or filesystem assets; see WEB_INTERFACE.md for the transport/hosting distinction.

Every channel has X/Y/Z; retain all nine streams and independent baseline cells. Exact display labels remain NO BASELINE YET, PROVISIONAL (n<5), WITHIN BASELINE, OUTSIDE BASELINE – REVIEW. An unavailable current estimate stays undefined. No SNR or PSD plot is fabricated for the approved FFT-magnitude method.
