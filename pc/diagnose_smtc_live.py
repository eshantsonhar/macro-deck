"""
Diagnostic to isolate which condition causes SMTC to fail
Tests four cases:
A. SMTC only
B. SMTC + ordinary background thread
C. SMTC + COM4 open
D. SMTC + COM4 + volume listener
"""

import asyncio
import threading
import time
import serial
import sys
import traceback
from datetime import datetime
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

def log_marker(stage, thread_name=None):
    """Print a marker with timestamp and thread name"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    tn = thread_name or threading.current_thread().name
    print(f"[{timestamp}] [{tn}] {stage}", flush=True)

async def get_media_smtc_async():
    """Get media from SMTC with instrumentation"""
    log_marker("get_media_smtc_async: ENTRY")
    
    log_marker("get_media_smtc_async: BEFORE request_async")
    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    log_marker("get_media_smtc_async: AFTER request_async")
    
    log_marker("get_media_smtc_async: BEFORE get_sessions")
    sessions = manager.get_sessions()
    log_marker("get_media_smtc_async: AFTER get_sessions")
    
    vivaldi_aumid = "Vivaldi.Z5DLQOUXBXTNP4UT4UK7IYQSGM"
    vivaldi_session = None
    
    for session in sessions:
        if session.source_app_user_model_id == vivaldi_aumid:
            vivaldi_session = session
            break
    
    target_session = vivaldi_session if vivaldi_session else manager.get_current_session()
    
    if target_session:
        log_marker("get_media_smtc_async: BEFORE get_playback_info")
        playback_info = target_session.get_playback_info()
        log_marker("get_media_smtc_async: AFTER get_playback_info")
        
        if playback_info.playback_status == 4:
            log_marker("get_media_smtc_async: BEFORE try_get_media_properties_async")
            props = await target_session.try_get_media_properties_async()
            log_marker("get_media_smtc_async: AFTER try_get_media_properties_async")
            
            if props and props.title and props.artist:
                log_marker(f"get_media_smtc_async: RETURN {props.title}")
                return props.title, props.artist, "Vivaldi"
    
    log_marker("get_media_smtc_async: RETURN None,None,None")
    return None, None, None

def get_media_smtc():
    """Synchronous wrapper with instrumentation"""
    log_marker("get_media_smtc: ENTRY")
    log_marker("get_media_smtc: BEFORE asyncio.run")
    try:
        result = asyncio.run(get_media_smtc_async())
        log_marker("get_media_smtc: AFTER asyncio.run")
        log_marker(f"get_media_smtc: RETURN {result}")
        return result
    except Exception as e:
        log_marker(f"get_media_smtc: EXCEPTION {type(e).__name__}: {e}")
        traceback.print_exc()
        return None, None, None

def watchdog(timeout_seconds, test_name):
    """Watchdog thread to detect hangs"""
    time.sleep(timeout_seconds)
    log_marker(f"WATCHDOG: {test_name} exceeded {timeout_seconds} seconds")

def run_test_a():
    """Test A: SMTC only"""
    log_marker("=== TEST A: SMTC ONLY ===")
    watchdog_thread = threading.Thread(target=watchdog, args=(5, "Test A"), daemon=True)
    watchdog_thread.start()
    
    try:
        result = get_media_smtc()
        log_marker(f"TEST A: RESULT {result}")
        return "PASS", result
    except Exception as e:
        log_marker(f"TEST A: EXCEPTION {type(e).__name__}: {e}")
        traceback.print_exc()
        return "ERROR", str(e)

def run_test_b():
    """Test B: SMTC + ordinary background thread"""
    log_marker("=== TEST B: SMTC + BACKGROUND THREAD ===")
    
    stop_event = threading.Event()
    
    def harmless_thread():
        log_marker("Background thread: START")
        while not stop_event.is_set():
            time.sleep(0.1)
        log_marker("Background thread: STOP")
    
    bg_thread = threading.Thread(target=harmless_thread, daemon=True)
    bg_thread.start()
    
    watchdog_thread = threading.Thread(target=watchdog, args=(5, "Test B"), daemon=True)
    watchdog_thread.start()
    
    try:
        result = get_media_smtc()
        log_marker(f"TEST B: RESULT {result}")
        stop_event.set()
        bg_thread.join(timeout=1)
        return "PASS", result
    except Exception as e:
        log_marker(f"TEST B: EXCEPTION {type(e).__name__}: {e}")
        traceback.print_exc()
        stop_event.set()
        bg_thread.join(timeout=1)
        return "ERROR", str(e)

def run_test_c():
    """Test C: SMTC + COM4 open"""
    log_marker("=== TEST C: SMTC + COM4 OPEN ===")
    
    watchdog_thread = threading.Thread(target=watchdog, args=(5, "Test C"), daemon=True)
    watchdog_thread.start()
    
    ser = None
    try:
        log_marker("TEST C: BEFORE serial.Serial")
        ser = serial.Serial("COM4", 115200, timeout=1)
        log_marker("TEST C: AFTER serial.Serial")
        
        result = get_media_smtc()
        log_marker(f"TEST C: RESULT {result}")
        
        ser.close()
        log_marker("TEST C: serial closed")
        return "PASS", result
    except Exception as e:
        log_marker(f"TEST C: EXCEPTION {type(e).__name__}: {e}")
        traceback.print_exc()
        if ser:
            ser.close()
        return "ERROR", str(e)

def run_test_d():
    """Test D: SMTC + COM4 + volume listener"""
    log_marker("=== TEST D: SMTC + COM4 + VOLUME LISTENER ===")
    
    stop_event = threading.Event()
    ser = None
    
    def volume_listener(ser):
        log_marker("Volume listener: START")
        while not stop_event.is_set():
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    log_marker(f"Volume listener: READ {repr(line)}")
                time.sleep(0.05)
            except Exception as e:
                log_marker(f"Volume listener: ERROR {e}")
                break
        log_marker("Volume listener: STOP")
    
    watchdog_thread = threading.Thread(target=watchdog, args=(5, "Test D"), daemon=True)
    watchdog_thread.start()
    
    try:
        log_marker("TEST D: BEFORE serial.Serial")
        ser = serial.Serial("COM4", 115200, timeout=1)
        log_marker("TEST D: AFTER serial.Serial")
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        vol_thread = threading.Thread(target=volume_listener, args=(ser,), daemon=True)
        vol_thread.start()
        log_marker("TEST D: Volume listener started")
        
        result = get_media_smtc()
        log_marker(f"TEST D: RESULT {result}")
        
        stop_event.set()
        vol_thread.join(timeout=1)
        
        ser.close()
        log_marker("TEST D: serial closed")
        return "PASS", result
    except Exception as e:
        log_marker(f"TEST D: EXCEPTION {type(e).__name__}: {e}")
        traceback.print_exc()
        stop_event.set()
        if ser:
            ser.close()
        return "ERROR", str(e)

def main():
    log_marker("=== SMTC DIAGNOSTIC START ===")
    log_marker(f"Python version: {sys.version}")
    log_marker(f"Current thread: {threading.current_thread().name}")
    
    results = []
    
    # Test A
    result_a, value_a = run_test_a()
    results.append(("A", result_a, value_a))
    time.sleep(1)
    
    # Test B
    result_b, value_b = run_test_b()
    results.append(("B", result_b, value_b))
    time.sleep(1)
    
    # Test C
    result_c, value_c = run_test_c()
    results.append(("C", result_c, value_c))
    time.sleep(1)
    
    # Test D
    result_d, value_d = run_test_d()
    results.append(("D", result_d, value_d))
    
    log_marker("=== DIAGNOSTIC COMPLETE ===")
    
    print("\n" + "="*60)
    print("RESULTS TABLE")
    print("="*60)
    print(f"{'Test':<6} {'Serial':<6} {'Bg Thread':<12} {'Vol Listener':<12} {'Result':<10}")
    print("-"*60)
    print(f"{'A':<6} {'No':<6} {'No':<12} {'No':<12} {result_a:<10}")
    print(f"{'B':<6} {'No':<6} {'Yes':<12} {'No':<12} {result_b:<10}")
    print(f"{'C':<6} {'Yes':<6} {'No':<12} {'No':<12} {result_c:<10}")
    print(f"{'D':<6} {'Yes':<6} {'Yes':<12} {'Yes':<12} {result_d:<10}")
    print("="*60)
    
    print("\nDETAILED RESULTS:")
    for test, result, value in results:
        print(f"Test {test}: {result} - {value}")

if __name__ == "__main__":
    main()
