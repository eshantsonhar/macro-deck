# Pico W Physical Recovery Procedure

## Pre-Recovery Checklist

- [ ] Project root: `C:\Eshant_Sonhar\misc coding projects\diy_macro_deck`
- [ ] Git clean state (no uncommitted changes)
- [ ] Known-good firmware: `backups/hardware-known-good/main.py` (commit 45a13de)
- [ ] MicroPython v1.28.0: `backups/firmware/RPI_PICO_W-20260406-v1.28.0.uf2`
- [ ] Flash erase tool: `backups/firmware/flash_nuke.uf2`
- [ ] Windows COM4 currently enumerated (USB Serial Device)
- [ ] No Python/mpremote processes holding COM4
- [ ] Current Pico state: REPL unresponsive (filesystem blocking)

## Exact Files Required

### Flash Erase Tool
- **File:** `backups\firmware\flash_nuke.uf2`
- **Size:** 114,688 bytes
- **SHA256:** F3C3B6A62D2D7E944F336BC2EC73393F00ADFBB56B6FA7440BA7EE3D5AD5B49D
- **Source:** https://datasheets.raspberrypi.com/soft/flash_nuke.uf2 (official Raspberry Pi)
- **Purpose:** Completely erases Pico flash (firmware + filesystem)
- **Documentation:** Raspberry Pi RP-008273-DS (official bootrom specification)

### MicroPython Firmware
- **File:** `backups\firmware\RPI_PICO_W-20260406-v1.28.0.uf2`
- **Size:** 1,749,504 bytes
- **SHA256:** A0210C9C8A085391CB66F530C298A5A4FB804A9D072289254C24DF5FDF210F7A
- **Release Date:** April 6, 2026
- **Version:** v1.28.0
- **Source:** https://micropython.org/download/RPI_PICO_W/
- **Purpose:** Clean MicroPython runtime

### Known-Good Hardware Firmware
- **File:** `backups\hardware-known-good\main.py`
- **SHA256:** 2AE4F9BC8A8B5BEDDD5920CDB84B9E91273A4B6CD2FAFA92D94DA0534693DFD9
- **Git Commit:** 45a13de - "Initial commit of software"
- **Purpose:** Verified hardware firmware (OLED, encoder, buttons)
- **Verified:**
  - SH1106 OLED working
  - Encoder working (exact 1 event per detent)
  - Encoder direction correct
  - Encoder switch working
  - All 10 buttons working

## Exact Physical Steps

### Step 1: Enter BOOTSEL Mode
1. While the Pico W is connected to the PC, press and hold the BOOTSEL button
2. While continuing to hold BOOTSEL, press the RESET button on the Pico W
3. Release the RESET button while still holding BOOTSEL
4. Wait 1-2 seconds, then release the BOOTSEL button
5. Windows should show the RPI-RP2 drive appears in File Explorer
6. **Continue to Step 2 only when RPI-RP2 drive is visible**
7. Note: This is the ONLY physical button interaction required for the entire recovery

### Step 2: Erase Flash
1. Open Windows Explorer
2. Navigate to RPI-RP2 drive
3. Copy `backups\firmware\flash_nuke.uf2` to RPI-RP2 drive
4. Wait ~10 seconds for Pico to process the erase operation
5. The Pico LED will flash briefly to indicate erase completion
6. RPI-RP2 drive will remain visible (flash_nuke automatically returns to BOOTSEL mode)
7. **Critical:** At this point, the Pico has NO firmware and NO filesystem
8. **Do NOT re-enter BOOTSEL mode** - the drive is already ready for MicroPython installation

### Step 3: Install MicroPython v1.28.0
1. RPI-RP2 drive should still be visible from Step 2
2. Copy `backups\firmware\RPI_PICO_W-20260406-v1.28.0.uf2` to RPI-RP2 drive
3. Wait ~5 seconds for Pico to reboot
4. RPI-RP2 drive will disappear
5. Pico is now running clean MicroPython v1.28.0

### Step 4: Verify Clean REPL
1. Open PowerShell in project directory: `cd "C:\Eshant_Sonhar\misc coding projects\diy_macro_deck"`
2. Run: `py -m mpremote connect COM4`
3. You should see the MicroPython prompt: `>>>`
4. Run: `1+1`
5. Expected output: `2`
6. If REPL works, press Ctrl+D to exit mpremote
7. If REPL does NOT work, STOP and report error

## Exact Windows Commands After Pico Returns

### Step 5: Upload Known-Good Hardware Firmware
```powershell
cd "C:\Eshant_Sonhar\misc coding projects\diy_macro_deck"
.\upload.ps1
```

This uploads `main.py` (commit 45a13de) to the Pico.

### Step 6: Reset Pico
```powershell
cd "C:\Eshant_Sonhar\misc coding projects\diy_macro_deck"
.\upload.ps1 -Reset
```

This resets the Pico to run the uploaded firmware.

## Clean-REPL Verification

After Step 4 (before uploading project code), verify:

- [ ] mpremote connects successfully
- [ ] `>>>` prompt appears
- [ ] `1+1` returns `2`
- [ ] `import os; os.listdir('/')` returns empty list `[]`
- [ ] No `boot.py` or `main.py` present

**STOP HERE if any check fails.**

## Firmware Upload

The `upload.ps1` script performs:
1. Uploads `main.py` to Pico via mpremote
2. Optionally resets Pico (recommended)
3. Exits cleanly, releasing COM4

## Hardware Verification

After Steps 5-6, verify hardware functionality:

### OLED Display
- [ ] OLED initializes (screen should not remain blank)
- [ ] Default screen shows "Now Playing:" and "No Track Playing"
- [ ] SH1106 initialization is preserved

### Rotary Encoder
- [ ] Clockwise rotation produces exactly one OLED update per physical detent
- [ ] Counterclockwise rotation produces exactly one OLED update per physical detent
- [ ] 10 physical clicks = 10 OLED updates
- [ ] Direction is correct (CW/CCW)
- [ ] Encoder state machine is preserved (2 transitions per detent)

### Encoder Switch
- [ ] Single press produces one OLED update
- [ ] Holding switch does not repeat events
- [ ] Release produces one OLED update

### Buttons 1-10
- [ ] Each button press produces OLED update
- [ ] Button numbers correspond correctly (1-10)
- [ ] All buttons respond independently

## Recovery Success Criteria

**ALL of the following must pass:**

- [ ] MicroPython REPL responds to `1+1` with `2`
- [ ] mpremote can enter and exit cleanly
- [ ] Firmware uploads successfully
- [ ] Pico resets successfully
- [ ] OLED initializes and displays default screen
- [ ] Encoder CW works (1 event per detent, correct direction)
- [ ] Encoder CCW works (1 event per per detent, correct direction)
- [ ] Encoder switch works (single event per press)
- [ ] Buttons 1-10 all work
- [ ] COM4 can be opened independently after firmware deployment
- [ ] No BOOTSEL required for normal development
- [ ] Git contains clean commit with known-good baseline

**DO NOT proceed to Spotify bridge until ALL hardware verification passes.**

## Rollback/Emergency Notes

### If Flash Erase Fails
- Ensure BOOTSEL button is held firmly while pressing RESET
- Ensure RESET button is pressed while BOOTSEL is held
- Try a different USB cable
- Try a different USB port on PC
- Check Windows Device Manager for USB enumeration errors

### If MicroPython Installation Fails
- Verify UF2 file SHA256 matches: A0210C9C9C8A085391CB66F530C298A5A4FB804A9D072289254C24DF5FDF210F7A
- Re-download from official source if corrupted
- Ensure complete file copy to RPI-RP2 drive

### If REPL Does Not Respond After Clean Install
- Try waiting 5-10 seconds for Pico to boot
- Check COM4 is still enumerated in Windows
- Try connecting at 115200 baud with serial terminal
- If still unresponsive, repeat entire recovery procedure

### If Hardware Verification Fails
- Check physical connections (OLED, encoder, buttons)
- Verify pin assignments match HARDWARE.md
- Restore main.py from Git commit 45a13de
- Re-upload and re-test
- If hardware fails, issue is physical (not firmware-related)

### Emergency Rollback
If firmware causes issues after hardware verification:
1. Restore commit 45a13de from Git: `git checkout 45a13de -- main.py`
2. Re-upload: `.\upload.ps1 -Reset`
3. Verify again
4. If commit 45a13de also fails, investigate hardware

### NEVER Re-use Bootsel for Normal Development
After recovery, normal development workflow:
1. Modify `main.py` in project directory
2. Test via `.\upload.ps1` and `.\upload.ps1 -Reset`
3. Do NOT use BOOTSEL unless REPL is completely inaccessible
4. Do NOT flash firmware unless changing MicroPython version

## Important Notes

- **BOOTSEL is emergency recovery ONLY**, not part of normal development
- This procedure requires exactly ONE BOOTSEL entry (enter once, perform both erase and MicroPython install while in bootloader mode)
- The flash_nuke UF2 automatically returns to BOOTSEL mode after erasing, so no second BOOTSEL entry is required
- The Pico will be left in a clean, verified state
- All project files are preserved locally with Git
- Recovery is deterministic and reversible
- No further BOOTSEL operations should be needed if firmware design principles are followed
