# Recovery Procedures

## Incident Summary

### What Happened
During development of the USB serial protocol for volume control, the Pico W's MicroPython REPL became completely unresponsive. Multiple firmware changes and serial experiments led to a state where:
- USB enumeration worked (COM4 visible)
- Windows driver loaded correctly
- COM4 could be opened
- MicroPython REPL gave no response
- mpremote could not enter raw REPL
- No spontaneous data from fresh firmware

### Root Cause
UF2 flashing of MicroPython firmware does NOT erase the Pico's filesystem. The previous project's `boot.py` and/or `main.py` files persisted across firmware updates and likely contained blocking code that prevented USB services from becoming available.

From MicroPython documentation:
> "USB services on an RP2 board are no longer made available until after boot.py completes execution. If it never exits the RP2 board will never deliver USB services."

### Why COM4 Being Visible Does Not Imply REPL is Functional
- USB enumeration is a hardware-level function (boot ROM)
- MicroPython REPL is a firmware runtime function
- The USB device can enumerate before MicroPython starts
- If `boot.py`/`main.py` block before USB initialization, the REPL never becomes accessible
- Windows sees the USB serial device but cannot communicate with the MicroPython runtime

### Why UF2 Flashing Did Not Restore the Filesystem
From Raspberry Pi Forums:
> "A MicroPython '.uf2' will only overwrite itself, will not touch the file system at all, except when it's so large that it impinges on what file system there was."

This means:
- Booting the Pico in BOOTSEL mode and flashing a UF2 only replaces the firmware binary
- The MicroPython filesystem region of flash is preserved
- Any problematic `boot.py`/`main.py` survive the firmware update
- Both v1.29.0 and v1.28.0 behaved identically because they executed the same blocking startup code

### Why RP2 Has No MicroPython Safe Mode
From MicroPython GitHub PR #15956:
> "These ports don't have any MicroPython-specific recovery features like Safe Mode boots, the factory reset process is to erase the entire flash."

The RP2 port intentionally does not support safe mode boot to skip `boot.py`/`main.py`.

### Why Filesystem Recovery Requires BOOTSEL/Flash Erase
- No software-only filesystem access when REPL is inaccessible
- RP2 port does not expose USB MSC in standard firmware
- No MicroPython command can erase flash without REPL access
- No alternative recovery mechanism exists for RP2
- The only method is to enter BOOTSEL mode and use `flash_nuke.uf2` to erase the entire flash

## Recovery Methods

### Emergency Recovery (BOOTSEL)
**Required when:** REPL is completely inaccessible

**Steps:**
1. Hold BOOTSEL button on Pico W
2. Connect USB cable (or press RESET if already connected)
3. RPI-RP2 drive appears as mass storage device
4. Copy `flash_nuke.uf2` to RPI-RP2 drive
5. Wait ~10 seconds for Pico to reboot
6. Pico will appear as RPI-RP2 drive again (flash is now erased)
7. Copy MicroPython UF2 to RPI-RP2 drive
8. Pico reboots into clean MicroPython
9. Verify REPL is accessible
10. Upload known-good firmware

**Impact:**
- Erases entire flash (firmware + filesystem)
- All Pico files are lost
- Requires re-flashing MicroPython
- Requires re-uploading all project files

**Safety:**
- BOOTSEL mode is in read-only ROM (cannot be bricked)
- Standard Raspberry Pi recovery method
- Authorized only for emergency recovery

### Software-Only Recovery (When REPL is Accessible)
**Required when:** REPL is accessible but `boot.py`/`main.py` cause issues

**Steps:**
1. Connect to REPL via mpremote or serial terminal
2. Delete problematic files:
   ```
   import os
   os.remove('boot.py')
   os.remove('main.py')
   ```
3. Reset Pico
4. Upload corrected firmware

**Impact:**
- Only removes specified files
- Firmware remains intact
- Can be done without physical intervention

### Normal Development Workflow
**Required for:** Regular firmware updates

**Workflow:**
```powershell
# Upload firmware
py -m mpremote connect COM4 fs cp main.py :main.py

# Reset Pico
py -m mpremote connect COM4 reset

# Close mpremote (releases COM4)

# Start PC bridge
py pc/spotify_bridge.py
```

**Important:**
- Do NOT use `mpremote run` for deployment - it holds COM4 open
- Allow Pico to run autonomously after upload
- PC bridge opens COM4 independently

## Known-Good Baselines

### Hardware Firmware
- **Git Commit:** 45a13de - "Initial commit of software"
- **Location:** `backups/hardware-known-good/main.py`
- **Verified:**
  - OLED working
  - Encoder working (exact 1 event per detent)
  - Encoder direction correct
  - Encoder switch working
  - All 10 buttons working
- **Current Project Status:** main.py has been restored to this commit and is ready for upload after physical recovery

### MicroPython Firmware
- **Version:** v1.28.0 (used during BOOTSEL test)
- **File:** `backups/firmware/RPI_PICO_W-20260406-v1.28.0.uf2`
- **Size:** 1,749,504 bytes
- **SHA256:** A0210C9C8A085391CB66F530C298A5A4FB804A9D072289254C24DF5FDF210F7A
- **Release Date:** 2026-04-06
- **Source:** https://micropython.org/download/RPI_PICO_W/
- **Verified:** Downloaded from official source, SHA256 verified

### Alternative Firmware (v1.29.0)
- **File:** `backups/firmware/RPI_PICO_W-20260824-v1.29.0.uf2`
- **Size:** 1,811,456 bytes
- **SHA256:** F918C0A082C6DAF53E27998B7F990BA5F065DB2E298B21A34024532A20786794
- **Release Date:** 2026-08-24
- **Source:** https://micropython.org/download/RPI_PICO_W/
- **Verified:** Downloaded from official source, SHA256 verified
- **Note:** Latest stable release, available but not used during BOOTSEL test

## Prevention

### Firmware Design Principles
1. Never use `boot.py` unless absolutely necessary
2. Keep `main.py` non-blocking
3. Never disable the normal MicroPython REPL
4. Handle serial exceptions gracefully
5. Allow hardware to continue working even if serial fails
6. Use short polling intervals (2ms main loop)
7. Never assume PC bridge is connected
8. Keep application exceptions recoverable

### Development Practices
1. Test firmware changes incrementally
2. Commit working states before major changes
3. Preserve known-good baselines
4. Never modify hardware calibration without testing
5. Use Git tags for stable releases
6. Document recovery procedures

### Serial Protocol
1. Keep protocol machine-readable only
2. Separate protocol from debug output
3. Handle malformed messages on PC side
4. Never send errors back to Pico
5. Allow graceful reconnection

## BOOTSEL Policy

**BOOTSEL is emergency recovery ONLY.**

**NOT for:**
- Normal development
- Firmware updates
- Serial debugging
- Application changes
- Experimental changes

**ONLY for:**
- REPL completely inaccessible
- No software-only recovery possible
- Explicit user authorization

**Reason:**
- Physical access is difficult
- Repeated BOOTSEL operations risk damage
- Software-only recovery should always be attempted first
- Normal workflow must never require BOOTSEL

## Verification After Recovery

After any recovery operation, verify:
1. [ ] MicroPython REPL responds
2. [ ] `1+1` returns `2`
3. [ ] Known-good firmware uploads
4. [ ] OLED initializes
5. [ ] Encoder works (1 event per detent)
6. [ ] Encoder direction correct
7. [ ] Encoder switch works
8. [ ] All 10 buttons work
9. [ ] USB protocol works
10. [ ] PC bridge can connect
11. [ ] Volume control works
12. [ ] Spotify display works
