# Pico W Macro Deck: Input Regression Investigation

## 1. Incident Summary

- **Device:** Raspberry Pi Pico W macro deck
- **Firmware:** MicroPython v1.28.0 on 2026-04-06 (RP2040)
- **Hardware:** SH1106-compatible 128×64 OLED + 10 buttons + rotary encoder with push switch
- **Known-good baseline:** Git commit `a36ca87` - "all buttons, encoder and oled working"
- **Regression:** After changing four `print()` statement strings, all 10 buttons and all encoder functions became apparently unresponsive
- **OLED behavior:** OLED continued displaying the application screen ("Now Playing:", "No Track", "Playing", "Ready")
- **USB serial:** COM4 remained accessible, REPL responsive
- **Physical verification:** The same hardware was previously physically verified working with commit `a36ca87`

## 2. Hardware Configuration

**Verified pinout (fixed, not changed during incident):**

- **Encoder DT:** GP6 (Pin.IN, Pin.PULL_UP)
- **Encoder CLK:** GP7 (Pin.IN, Pin.PULL_UP)
- **Encoder SW (push switch):** GP0 (Pin.IN, Pin.PULL_UP)
- **Button 1:** GP9 (Pin.IN, Pin.PULL_UP)
- **Button 2:** GP10 (Pin.IN, Pin.PULL_UP)
- **Button 3:** GP11 (Pin.IN, Pin.PULL_UP)
- **Button 4:** GP12 (Pin.IN, Pin.PULL_UP)
- **Button 5:** GP13 (Pin.IN, Pin.PULL_UP)
- **Button 6:** GP14 (Pin.IN, Pin.PULL_UP)
- **Button 7:** GP15 (Pin.IN, Pin.PULL_UP)
- **Button 8:** GP16 (Pin.IN, Pin.PULL_UP)
- **Button 9:** GP17 (Pin.IN, Pin.PULL_UP)
- **Button 10:** GP18 (Pin.IN, Pin.PULL_UP)
- **OLED SDA:** GP20 (I2C0)
- **OLED SCL:** GP21 (I2C0)
- **OLED I2C address:** 0x3C
- **I2C bus:** I2C0 at 400 kHz
- **OLED controller:** SH1106-compatible
- **OLED resolution:** 128×64
- **Button logic:** All use `Pin.IN, Pin.PULL_UP`, pressed state = 0, released state = 1

## 3. Known-Good Baseline

**Git commit:** `a36ca87`  
**Commit description:** "all buttons, encoder and oled working"  
**Verification status:** PHYSICALLY VERIFIED before the regression

**Known-good source properties:**
- **SHA256:** `D4E7E954A2092BCC5A38AD0B82639CC2D5DF83A4371776E199ABBEB5173FE76C`
- **Size:** 5890 bytes
- **Physical verification:** All 10 buttons, encoder CW, encoder CCW, encoder push switch, and OLED were manually tested and confirmed working

**Important:** This is a PHYSICALLY VERIFIED baseline, not merely an assumed-good commit. The user personally verified:
- OLED shows normal screen
- Button 1 works
- Button 2 works
- Button 3 works
- Button 4 works
- Button 5 works repeatedly
- Button 6 works
- Button 7 works
- Button 8 works
- Button 9 works
- Button 10 works
- Encoder clockwise works
- Encoder counter-clockwise works
- Encoder push switch works
- Repeated events do not freeze the Pico

## 4. Regressed Version

**Current source properties:**
- **SHA256:** `079F360A4751830BA128CDDB1FC43A84ACBAD6314B9F967C7093A76536A80371`
- **Size:** 5984 bytes

**Source differences from a36ca87 (exactly four print() changes):**

**Change 1 - Encoder CW output:**
```python
# Old (a36ca87):
print(
    "Encoder CW | Position:",
    encoder_position
)

# New (regressed):
print("ENCODER_CW")
```

**Change 2 - Encoder CCW output:**
```python
# Old (a36ca87):
print(
    "Encoder CCW | Position:",
    encoder_position
)

# New (regressed):
print("ENCODER_CCW")
```

**Change 3 - Button output:**
```python
# Old (a36ca87):
print("Button", i + 1, "pressed")

# New (regressed):
print("BUTTON_" + str(i + 1))
```

**Change 4 - Encoder switch output:**
```python
# Old (a36ca87):
print("Encoder switch pressed")

# New (regressed):
print("ENCODER_SW")
```

**Git verification confirmed NO changes to:**
- GPIO configuration (Pin assignments, modes, pull-ups)
- Encoder transition table
- Encoder thresholds (±2 transitions per detent)
- Button scanning logic
- OLED initialization code
- I2C configuration
- Main loop structure
- Timing (2ms loop delay)
- Serial input code (`check_serial_input()`, `sys.stdin.any()`, `sys.stdin.read(1)`)
- Exception handling
- Encoder state calculation
- Button debounce logic

## 5. Investigation and Incorrect Hypotheses

### 5.1 Hardware/GPIO Failure

**Initial suspicion:** REPL observations showed static GPIO values and no response to physical inputs, suggesting hardware failure.

**Evidence:**
- REPL commands like `Pin(6).value()` returned static values (0)
- Repeated GPIO queries showed no change despite physical button presses
- No main.py globals present in REPL after reset

**Disproven by:** Restoring the exact `a36ca87` source and physically verifying that all inputs worked. The same hardware, wiring, and Pico functioned correctly with the known-good firmware.

**Conclusion:** Hardware/GPIO was NOT the cause. The regression was software-specific.

### 5.2 sys.stdin.any() API Incompatibility

**Observation:** In the REPL context, `sys.stdin` was observed as a `TextIOWrapper` object without an `any()` method:
```python
>>> import sys
>>> type(sys.stdin)
<class 'TextIOWrapper'>
>>> 'any' in dir(sys.stdin)
False
```

**Relevant code:**
```python
def check_serial_input():
    global serial_buffer
    try:
        if sys.stdin.any():
            char = sys.stdin.read(1)
            if char:
                serial_buffer += char
                while '\n' in serial_buffer:
                    line, serial_buffer = serial_buffer.split('\n', 1)
                    line = line.strip()
                    if line and parse_serial_message(line):
                        show_screen()
    except Exception:
        pass
```

**Investigation:** The `sys.stdin.any()` call is wrapped in a broad `except Exception: pass` handler. This means if `sys.stdin.any()` raises an `AttributeError`, it would be caught and suppressed locally within `check_serial_input()`.

**What this proves:** The REPL stdin object lacks the `any()` method in REPL context.

**What this does NOT prove:** This observation alone does NOT establish that `sys.stdin.any()` caused the main loop to stop. The exception is caught locally, so the function would return silently and the main loop would continue to encoder/button polling. The REPL context may have a different stdin object than the running application context.

**Conclusion:** Unproven as the root cause. The exception handling makes it unlikely to stop the main loop.

### 5.3 Missing boot.py

**Observation:** No `boot.py` or `boot.mpy` existed on the Pico filesystem.

**Investigation:** MicroPython documentation states that `boot.py` is optional. If present, it runs before `main.py`. If absent, MicroPython proceeds directly to `main.py` execution.

**What this proves:** No custom startup script exists.

**What this does NOT prove:** The absence of `boot.py` is not itself an autostart failure. MicroPython is designed to run `main.py` automatically even without `boot.py`.

**Conclusion:** Not the cause. boot.py is optional and its absence is normal.

### 5.4 main.py Autostart Behavior

**Investigation challenges:** Several early tests were invalid or inconclusive because they used separate mpremote action commands.

**Invalid tests:**
1. `mpremote connect COM4 reset` followed by `mpremote connect COM4 exec "print('TEST')"`
2. `mpremote connect COM4 reset` followed by `mpremote connect COM4 exec "print('DT' in globals())"`

**Why invalid:** According to current mpremote documentation, action commands such as `exec` and `fs` interrupt a running program. Therefore, observing missing globals after a subsequent `exec` does NOT prove that `main.py` never started. The `exec` command itself may have interrupted a running `main.py`.

**Evidence from manual execution:** When `exec(open('/main.py').read())` was manually executed, it entered the infinite loop and could be interrupted with Ctrl+C, producing a traceback showing line 286 (the `time.sleep_ms(2)` in the main loop). This proved the code could run, but did not prove automatic execution after reset.

**Serial monitoring attempts:** Raw serial monitoring after reset captured no output (0 bytes). This could indicate:
- main.py never started
- main.py started but produced no serial output
- main.py started but serial output was not captured due to timing/methodology

**Conclusion:** Autostart behavior could not be conclusively determined from the available tests due to mpremote command interference. The absence of REPL globals after a separate `exec` command does NOT prove that main.py never started.

### 5.5 mpremote Test Methodology

**Critical lesson learned:**

Current mpremote documentation states that action commands such as `exec` and `fs` interrupt a running program, while `repl` acts as a serial monitor and does not itself stop a running program.

**Reference:** https://docs.micropython.org/en/latest/reference/mpremote.html

**Therefore:**
- `reset` followed by a separate `exec` is NOT a valid test for whether `main.py` remained running after reset.
- State observed after `exec` cannot by itself prove that `main.py` never started.
- The `repl` subcommand was attempted but failed with a Windows serial permission error, preventing direct observation of running program behavior.

**Conclusion:** Future debugging must avoid using action commands to infer program state when investigating autostart behavior.

## 6. Filesystem Verification

**Pico filesystem contents:**
- Only file: `main.py`
- Size on Pico: 5984 bytes (as reported by `mpremote fs ls`)
- No `main.mpy`
- No `boot.py`
- No `boot.mpy`

**File extraction and comparison:**
- Extracted Pico source via `mpremote fs cat :main.py > main_from_pico.py`
- Extracted file size: 6270 bytes
- Local source size: 5984 bytes
- Size difference: 286 bytes

**SHA256 hashes:**
- Local `main.py`: `079F360A4751830BA128CDDB1FC43A84ACBAD6314B9F967C7093A76536A80371`
- Extracted `main_from_pico.py`: `5A991C0BE461C92DF2202C14268EAF59E77D4565C14792F36E7F370B0751F858`

**Initial concern:** Hashes differed, suggesting possible source discrepancy.

**Resolution:** Git diff analysis showed the files were identical except for line endings:
- Local file: Unix line endings (LF `\n`)
- Pico file: Windows line endings (CRLF `\r\n`)
- Number of lines: 286
- Size difference: Exactly 1 byte per line (286 bytes = 286 lines × 1 CR byte)

**Conclusion:** The Pico source content matched the local source exactly. The size/hash difference was solely due to line-ending conversion by the Pico's filesystem. No source-code discrepancy existed.

## 7. Exact Control-Flow Verification

**Main loop operation order (lines 198-286):**

Every loop iteration executes in this exact order:
1. `check_serial_input()` (line 204)
2. Encoder state read: `current_state = (CLK.value() << 1) | DT.value()` (line 210)
3. Encoder transition processing (lines 212-248, conditional)
4. Encoder print if movement occurs: `print("ENCODER_CW")` or `print("ENCODER_CCW")` (lines 233, 244, conditional)
5. `show_screen()` after encoder event (lines 235, 246, conditional)
6. Button scanning (lines 255-267, 10-button loop)
7. Button print if pressed: `print("BUTTON_" + str(i + 1))` (line 263, conditional per button)
8. `show_screen()` after button event (line 265, conditional)
9. Encoder switch handling (lines 274-284)
10. Encoder switch print if pressed: `print("ENCODER_SW")` (line 280, conditional)
11. `show_screen()` after switch event (line 282, conditional)
12. `time.sleep_ms(2)` (line 286)

**Exception handling in `check_serial_input()`:**
- The entire function body (lines 111-124) is wrapped in `try/except Exception: pass`
- This catches ALL exceptions, including:
  - `AttributeError` from `sys.stdin.any()` (if method doesn't exist)
  - `OSError` from USB CDC access
  - I2C/OLED exceptions from `show_screen()` (called at line 122 inside the try block)
  - Memory errors from string operations
  - Any other runtime exception
- Exceptions do NOT escape to the main loop
- If `check_serial_input()` fails, it returns silently and the loop continues to encoder/button polling

**Changed print statement analysis:**
- All four changed print statements are simple string literals
- None call external code beyond ordinary string formatting
- None have explicit blocking behavior
- All are followed immediately by `show_screen()` calls
- The only potential exception source is USB CDC output failure (unlikely to be caught by the local exception handler in `check_serial_input()`)

**Conclusion:** The control flow structure is identical between the known-good and regressed versions. The only source-level differences are the four print statement strings.

## 8. Decisive A/B Test

**Test procedure:**
1. Extracted exact source from Git commit `a36ca87`:
   ```bash
   git show a36ca87:main.py > main_a36ca87.py
   ```
2. Verified SHA256: `D4E7E954A2092BCC5A38AD0B82639CC2D5DF83A4371776E199ABBEB5173FE76C`
3. Verified size: 5890 bytes
4. Deleted existing `main.py` on Pico
5. Uploaded the exact `a36ca87` source to Pico as `main.py`:
   ```bash
   mpremote connect COM4 fs cp main_a36ca87.py :main.py
   ```
6. Hard reset the Pico:
   ```bash
   mpremote connect COM4 reset
   ```
7. Waited 3 seconds for boot
8. Physically tested all inputs

**Test results:**
- Button 1: **WORKING**
- Button 2: **WORKING**
- Button 3: **WORKING**
- Button 4: **WORKING**
- Button 5: **WORKING**
- Button 6: **WORKING**
- Button 7: **WORKING**
- Button 8: **WORKING**
- Button 9: **WORKING**
- Button 10: **WORKING**
- Encoder clockwise: **WORKING**
- Encoder counter-clockwise: **WORKING**
- Encoder switch: **WORKING**
- OLED: **WORKING**

**Conclusion:** Restoring the exact physically verified `a36ca87` source restored all physical inputs. The regression is software-specific and localized to the four print-statement changes.

## 9. Final Technical Conclusion

**Proven:**
- The regression is strongly localized to the four print-statement changes because they were the ONLY source-code differences between the failing version and the physically verified working version
- Restoring the known-good source restored all inputs
- The hardware, wiring, and Pico are functional

**Unproven:**
- The investigation did NOT isolate which of the four print statements, or which underlying runtime/USB-serial interaction, produced the regression
- The exact low-level mechanism remains unproven
- It is unknown whether the issue is:
  - A specific MicroPython USB CDC behavior with certain print strings
  - A timing interaction between print() and serial input checking
  - A specific character sequence in the new print strings
  - A USB buffer/flow control issue
  - Or another mechanism

**Not supported by evidence:**
- "GPIO was broken" - disproven by A/B test
- "The hardware was broken" - disproven by A/B test
- "sys.stdin.any() was definitely the cause" - unproven, exception handling makes this unlikely
- "MicroPython print is definitely broken" - unproven, only specific strings were changed
- "main.py definitely failed to autostart" - unproven due to mpremote command interference

## 10. Current Safe State

The Pico is currently running the known-good `a36ca87` firmware with SHA256 `D4E7E954A2092BCC5A38AD0B82639CC2D5DF83A4371776E199ABBEB5173FE76C`.

All 10 buttons, encoder CW/CCW, encoder switch, and OLED have been physically verified working.

No BOOTSEL or firmware reflashing was required for the final resolution. The issue was resolved by restoring the known-good source code via `mpremote fs cp` and a hard reset.

## 11. Future Debugging Rules

**For future coding agents:**

1. **Never diagnose hardware failure from a REPL test alone** when a known-good firmware baseline exists. Always perform a controlled A/B test against the known-good commit.

2. **Never use a separate mpremote exec/fs action after reset** to infer whether main.py is running, because action commands can interrupt a running program. Use the `repl` subcommand for monitoring if possible, or accept that program state cannot be reliably inferred after action commands.

3. **Do not change GPIO/wiring/firmware** while a known-good software baseline exists unless evidence specifically requires it. Preserve the hardware baseline and test software changes first.

4. **Preserve a known-good Git commit** before experimental changes. Always have a reference point that has been physically verified.

5. **For regressions, use controlled A/B tests** against the known-good commit. Change one thing at a time and verify each change physically.

6. **When changing output/serial code** on a USB-connected MicroPython device, treat stdout/USB CDC interaction as a possible regression surface, but do not assume causality without a controlled test.

7. **Never use BOOTSEL as a first-line debugging step** for a software regression. BOOTSEL/firmware flashing is a destructive operation that should only be used when there is specific evidence of firmware/filesystem corruption.

8. **Distinguish between "proven", "strongly supported", "possible", and "unknown"** conclusions. Do not present unproven hypotheses as facts.

9. **Always verify file content, not just size/hash**, when comparing deployed and local files. Line-ending differences can produce hash mismatches without source-code differences.

10. **When REPL observations suggest hardware failure**, first verify by restoring a known-good software baseline before assuming hardware issues.

## 12. Evidence Table

| Observation | What it proves | What it does NOT prove |
|------------|----------------|------------------------|
| a36ca87 physically worked before regression | Hardware and original firmware were functional | Current issue is not hardware-specific |
| Current version failed physically | Regression exists in current version | Does not identify the specific change causing it |
| Git diff has exactly four print changes | Only those lines changed at source level | Does not prove those changes are the cause (just the candidates) |
| Pico file content matches local source (ignoring line endings) | Correct file was deployed | Does not prove the deployed file executed correctly |
| No boot.py exists | No custom startup script | Does not prove autostart failure (boot.py is optional) |
| sys.stdin.any() absent in observed REPL context | REPL stdin lacks .any() method | Does not prove running application has same stdin object |
| check_serial_input() catches exceptions | Exceptions won't escape to main loop | Does not prove exceptions occur or cause the regression |
| Restoring a36ca87 restores all inputs | Regression is localized to the four print changes | Does not identify which print change or underlying mechanism |

## 13. Reproduction / Recovery

**Safe recovery procedure:**

1. Preserve the current failing source in Git (commit or stash)
2. Restore the known-good commit: `git checkout a36ca87`
3. Upload main.py with `mpremote fs cp main.py :main.py`
4. Hard reset with `mpremote connect COM4 reset`
5. Physically verify all inputs (OLED, all 10 buttons, encoder CW/CCW, encoder switch)
6. Only then test one isolated code change at a time
7. After each change, upload, reset, and physically verify
8. If regression appears, revert to known-good and test a different change

**DO NOT include BOOTSEL as part of normal recovery.** BOOTSEL should only be used when there is specific evidence of firmware/filesystem corruption (e.g., filesystem corruption, wrong firmware version, or unable to access COM4).

## 14. References

- **MicroPython mpremote documentation:** https://docs.micropython.org/en/latest/reference/mpremote.html
- **MicroPython reset/boot sequence documentation:** https://docs.micropython.org/en/latest/reference/reset_boot.html

---

**Status:** RESOLVED. Known-good a36ca87 restored. All 10 buttons, encoder CW/CCW, encoder switch, and OLED physically verified working.
