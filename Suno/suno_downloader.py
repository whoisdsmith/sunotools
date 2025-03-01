#!/usr/bin/env python3
"""
Suno Downloader - Main Script

A tool to download all songs, cover images, lyrics and metadata from a Suno.com account.
"""

import os
import argparse
import time
import json
from pathlib import Path
from getpass import getpass

from tqdm import tqdm

from authenticate import SunoAuthenticator
from downloader import SunoDownloader
from utils import setup_logger, format_size, create_directory

# Set up logging
logger = setup_logger()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download songs from Suno.com account')
    parser.add_argument('--username', '-u', type=str, help='Suno.com username (e.g. @thecasketdiaries)')
    parser.add_argument('--email', '-e', type=str, help='Suno.com login email')
    parser.add_argument('--output-dir', '-o', type=str, default='suno_downloads', 
                        help='Output directory for downloaded content')
    parser.add_argument('--max-songs', '-m', type=int, help='Maximum number of songs to download (for testing)')
    parser.add_argument('--resume', '-r', action='store_true', help='Resume interrupted download')
    parser.add_argument('--skip-audio', action='store_true', help='Skip downloading audio files')
    parser.add_argument('--skip-images', action='store_true', help='Skip downloading cover images')
    parser.add_argument('--skip-lyrics', action='store_true', help='Skip downloading lyrics')
    parser.add_argument('--delay', '-d', type=float, default=1.0, 
                        help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    return parser.parse_args()


def main():
    """Main function to run the Suno downloader."""
    args = parse_arguments()
    
    # Set default username if not provided
    username = args.username or "@thecasketdiaries"
    if username and not username.startswith('@'):
        username = f'@{username}'
    
    print(f"Suno Downloader - Download all content from {username}")
    print("-" * 50)
    
    # Initialize directories
    base_dir = Path(args.output_dir)
    create_directory(base_dir)
    metadata_dir = base_dir / "metadata"
    audio_dir = base_dir / "audio"
    images_dir = base_dir / "images"
    lyrics_dir = base_dir / "lyrics"
    
    for directory in [metadata_dir, audio_dir, images_dir, lyrics_dir]:
        create_directory(directory)
    
    # Resume state file path
    resume_file = base_dir / "download_state.json"
    
    # Load resume state if requested
    downloaded_songs = set()
    if args.resume and resume_file.exists():
        try:
            with open(resume_file, 'r') as f:
                download_state = json.load(f)
                downloaded_songs = set(download_state.get('downloaded_songs', []))
            print(f"Resuming download. Already downloaded: {len(downloaded_songs)} songs")
        except Exception as e:
            logger.error(f"Failed to load resume state: {e}")
            print("Failed to load resume state. Starting from scratch.")
    
    # Authenticate
    print("Authenticating with Suno.com...")
    email = args.email or input("Enter your Suno.com email: ")
    password = getpass("Enter your Suno.com password: ")
    
    authenticator = SunoAuthenticator()
    session, user_info = authenticator.login(email, password)
    
    if not session:
        print("Authentication failed. Please check your credentials and try again.")
        return
    
    print(f"Authentication successful! Logged in as {user_info.get('username', 'User')}")
    
    # Initialize downloader
    downloader = SunoDownloader(
        session=session,
        user_info=user_info,
        base_dir=base_dir,
        audio_dir=audio_dir,
        images_dir=images_dir,
        lyrics_dir=lyrics_dir,
        metadata_dir=metadata_dir,
        request_delay=args.delay,
        verbose=args.verbose
    )
    
    # Fetch song list
    print(f"\nFetching song list for {username}...")
    songs = downloader.get_user_songs(username)
    
    if not songs:
        print("No songs found for this user. Please check the username and try again.")
        return
    
    print(f"Found {len(songs)} songs")
    
    # Limit songs if requested (for testing)
    if args.max_songs and args.max_songs > 0:
        songs = songs[:args.max_songs]
        print(f"Limited to {len(songs)} songs for testing")
    
    # Filter out already downloaded songs if resuming
    if args.resume and downloaded_songs:
        songs = [song for song in songs if song['id'] not in downloaded_songs]
        print(f"After filtering already downloaded, {len(songs)} songs remaining")
    
    # Start downloading
    total_songs = len(songs)
    progress_bar = tqdm(total=total_songs, desc="Downloading songs", unit="song")
    
    try:
        for i, song in enumerate(songs):
            song_id = song['id']
            song_title = song.get('title', f"Song-{song_id}")
            
            try:
                # Update progress
                progress_bar.set_description(f"Downloading {song_title}")
                
                # Download song components
                metadata_saved = downloader.save_metadata(song)
                
                audio_saved = True
                if not args.skip_audio:
                    audio_saved = downloader.download_audio(song)
                
                image_saved = True
                if not args.skip_images:
                    image_saved = downloader.download_image(song)
                
                lyrics_saved = True
                if not args.skip_lyrics:
                    lyrics_saved = downloader.download_lyrics(song)
                
                # Only mark as completed if everything was successful
                if metadata_saved and audio_saved and image_saved and lyrics_saved:
                    downloaded_songs.add(song_id)
                    
                    # Update resume state
                    download_state = {
                        'last_updated': time.time(),
                        'total_songs': total_songs,
                        'downloaded_songs': list(downloaded_songs)
                    }
                    with open(resume_file, 'w') as f:
                        json.dump(download_state, f)
                
                # Respect rate limits
                if i < total_songs - 1:  # No need to sleep after the last song
                    time.sleep(args.delay)
                    
            except Exception as e:
                logger.error(f"Error downloading song {song_id}: {e}")
                print(f"Error downloading {song_title}. See log for details.")
            
            # Update progress
            progress_bar.update(1)
            
    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Progress has been saved.")
    finally:
        progress_bar.close()
    
    # Summary
    downloaded_count = len(downloaded_songs)
    print("\nDownload Summary:")
    print(f"Total songs found: {total_songs}")
    print(f"Songs downloaded: {downloaded_count}")
    print(f"Songs remaining: {total_songs - downloaded_count}")
    print(f"Content saved to: {base_dir.absolute()}")
    
    if downloaded_count == total_songs:
        # Clean up resume file if all songs were downloaded
        if resume_file.exists():
            os.remove(resume_file)
        print("\nAll songs have been successfully downloaded!")
    else:
        print("\nDownload incomplete. Run with --resume to continue downloading.")
    

if __name__ == "__main__":
    main()
