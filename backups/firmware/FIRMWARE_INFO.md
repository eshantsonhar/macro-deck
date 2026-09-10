# MicroPython Firmware Information

## Tested Firmware

### v1.28.0 (Recommended)
- **Filename:** RPI_PICO_W-20260406-v1.28.0.uf2
- **Size:** 1,749,504 bytes
- **SHA256:** A0210C9C8A085391CB66F530C298A5A4FB804A9D072289254C24DF5FDF210F7A
- **Release Date:** 2026-04-06
- **Source:** https://micropython.org/download/RPI_PICO_W/
- **Status:** Downloaded, tested, working baseline
- **Notes:** This version was tested and should be used for this project

### v1.29.0
- **Filename:** RPI_PICO_W-20260824-v1.29.0.uf2
- **Size:** 1,811,456 bytes
- **SHA256:** F918C0A082C6DAF53E27998B7F990BA5F065DB2E298B21A34024532A20786794
- **Release Date:** 2026-08-24
- **Source:** https://micropython.org/download/RPI_PICO_W/
- **Status:** Downloaded but not verified for this project
- **Notes:** Latest stable release, downloaded during recovery investigation

## Important Notes

### UF2 Flashing Does NOT Erase Filesystem
From Raspberry Pi Forums:
> "A MicroPython '.uf2' will only overwrite itself, will not touch the file system at all, except when it's so large that it impinges on what file system there was."

This means:
- Booting in BOOTSEL mode and flashing a UF2 only replaces the firmware binary
- The MicroPython filesystem region of flash is preserved
- Any problematic `boot.py`/`main.py` survive the firmware update

### RP2/Pico W USB MSC is Disabled
From MicroPython source code (`ports/rp2/mpconfigport.h`):
```c
// Enable USB Mass Storage with FatFS filesystem.
#ifndef MICROPY_HW_USB_MSC
#define MICROPY_HW_USB_MSC (0)
#endif
```

USB MSC is DISABLED by default for the entire RP2 port. The Pico W does NOT expose its filesystem via USB mass storage in the standard MicroPython firmware.

### No Safe Mode on RP2
From MicroPython documentation:
> "These ports don't have any MicroPython-specific recovery features like Safe Mode boots, the factory reset process is to erase the entire flash."

The RP2 port does not support safe mode boot to skip `boot.py`/`main.py`.

### Filesystem Recovery Requires BOOTSEL
When the REPL is inaccessible, the only recovery method is:
1. Enter BOOTSEL mode
2. Use `flash_nuke.uf2` to erase entire flash
3. Re-flash MicroPython UF2
4. Upload project files

This is an emergency recovery procedure, not part of normal development.
