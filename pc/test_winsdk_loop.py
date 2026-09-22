"""
Test winsdk in a loop context
"""

import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

async def get_media():
    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    sessions = manager.get_sessions()
    
    vivaldi_aumid = "Vivaldi.Z5DLQOUXBXTNP4UT4UK7IYQSGM"
    vivaldi_session = None
    
    for session in sessions:
        if session.source_app_user_model_id == vivaldi_aumid:
            vivaldi_session = session
            break
    
    target_session = vivaldi_session if vivaldi_session else manager.get_current_session()
    
    if target_session:
        playback_info = target_session.get_playback_info()
        if playback_info.playback_status == 4:
            props = await target_session.try_get_media_properties_async()
            if props and props.title and props.artist:
                return props.title, props.artist, "Vivaldi"
    
    return None, None, None

def get_sync():
    return asyncio.run(get_media())

print("Test 1: First call")
try:
    result1 = get_sync()
    print(f"Result: {result1}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 2: Second call")
try:
    result2 = get_sync()
    print(f"Result: {result2}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest 3: Third call")
try:
    result3 = get_sync()
    print(f"Result: {result3}")
except Exception as e:
    print(f"Error: {e}")

print("\nDone")
