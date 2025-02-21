import os
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    """
    Detects silence at the beginning of an audio segment.

    :param sound: The audio segment to analyze.
    :param silence_threshold: The dBFS value below which sound is considered silence.
    :param chunk_size: The size of each chunk to analyze in milliseconds.
    :return: The duration of the leading silence in milliseconds.
    """
    trim_ms = 0  # Duration of silence in milliseconds

    assert chunk_size > 0  # Prevent infinite loop
    while trim_ms < len(sound):
        chunk = sound[trim_ms:trim_ms + chunk_size]
        if chunk.dBFS >= silence_threshold:
            break
        trim_ms += chunk_size

    return trim_ms


# Directory containing your MP3 files
directory = r"C:\Users\whois\OneDrive\The Casket Diaries Soundtrack\Main Theme"

# Parameters for silence detection
silence_threshold = -50.0  # Adjust this value if needed
chunk_size = 10            # Size of each chunk in milliseconds

for filename in os.listdir(directory):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(directory, filename)
        print(f"Processing: {file_path}")

        # Load the audio file
        audio = AudioSegment.from_mp3(file_path)

        # Reverse the audio to detect silence at the end
        reversed_audio = audio.reverse()

        # Detect leading silence in the reversed audio (which is trailing silence in the original)
        trim_ms = detect_leading_silence(
            reversed_audio,
            silence_threshold=silence_threshold,
            chunk_size=chunk_size
        )

        # Calculate the new duration
        new_duration = len(audio) - trim_ms
        trimmed_audio = audio[:new_duration]

        # Export the trimmed audio back to the same file
        trimmed_audio.export(file_path, format="mp3")
        print(f"Trimmed {trim_ms} ms of silence from the end of {filename}.")

print("All files have been processed.")
