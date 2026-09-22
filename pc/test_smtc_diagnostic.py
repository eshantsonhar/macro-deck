"""
Diagnostic script to test Windows Global System Media Transport Controls (SMTC)
Uses winsdk library to access Windows Runtime Media API
"""

import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

async def test_smtc():
    print("=== Windows SMTC Diagnostic ===")
    print()

    try:
        # Request media session manager
        print("Step 1: Requesting GlobalSystemMediaTransportControlsSessionManager...")
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        print("Session manager obtained successfully")
        print()

        # Get all sessions
        print("Step 2: Getting all media sessions...")
        sessions = manager.get_sessions()
        print(f"Number of sessions: {len(sessions)}")
        print()

        # Display session information
        print("=== Session Details ===")
        for i, session in enumerate(sessions):
            print(f"\nSession {i}:")
            print(f"  SourceAppUserModelId: {session.source_app_user_model_id}")

            # Get playback info
            try:
                playback_info = session.get_playback_info()
                print(f"  PlaybackStatus: {playback_info.playback_status}")
                print(f"  PlaybackType: {playback_info.playback_type}")
            except Exception as e:
                print(f"  Error getting playback info: {e}")

            # Get media properties with timing consideration
            try:
                await asyncio.sleep(0.2)
                media_properties = session.try_get_media_properties_async().get_results()
                if media_properties:
                    print(f"  Title: {media_properties.title}")
                    print(f"  Artist: {media_properties.artist}")
                    print(f"  AlbumTitle: {media_properties.album_title}")
                    print(f"  Subtitle: {media_properties.subtitle}")
                else:
                    print("  Media properties: None")
            except Exception as e:
                print(f"  Error getting media properties: {e}")

        print()
        print("=== Current Session ===")
        try:
            current_session = manager.get_current_session()
            if current_session:
                print(f"SourceAppUserModelId: {current_session.source_app_user_model_id}")
                try:
                    await asyncio.sleep(0.2)
                    media_properties = current_session.try_get_media_properties_async().get_results()
                    if media_properties:
                        print(f"Title: {media_properties.title}")
                        print(f"Artist: {media_properties.artist}")
                        print(f"AlbumTitle: {media_properties.album_title}")
                except Exception as e:
                    print(f"Error getting media properties: {e}")
            else:
                print("No current session")
        except Exception as e:
            print(f"Error getting current session: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smtc())
