from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import Sine
from io import BytesIO
from itertools import groupby
from typing import NamedTuple
import os

class TimedInstruction(NamedTuple):
    instruction: str
    beat: int


def text_to_audio_chunk(text, cache_dir="audio_cache"):
    """Convert text to an audio chunk (AudioSegment), using cached files if available."""
    # Ensure the cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    # Create a file path based on the text (hashed to avoid issues with special characters)
    filename = os.path.join(cache_dir, f"{text}.mp3")

    # If the audio file already exists, load it from the file
    if os.path.exists(filename):
        return AudioSegment.from_file(filename)

    # Otherwise, generate the audio and save it
    tts = gTTS(text, lang="es")
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)  # Write the audio data to an in-memory buffer
    audio_buffer.seek(0)

    # Save the audio file to the cache directory
    with open(filename, "wb") as f:
        f.write(audio_buffer.read())

    # Return the generated audio
    return AudioSegment.from_file(filename)


def create_metronome_track(bpm, num_beats, counts=[1, 2, 3, 5, 6, 7]):
    """
    Create a metronome track with beats on the specified counts.

    :param bpm: Beats per minute.
    :param num_beats: Total number of beats in the track.
    :param counts: List of beat numbers (within an 8-count) to play.
    :return: AudioSegment with the metronome beats.
    """
    beat_interval = 60 / bpm * 1000  # Interval between beats in milliseconds
    silence_after_beat = AudioSegment.silent(duration=beat_interval - 50)
    regular_beat_sound = Sine(1000).to_audio_segment(duration=50).apply_gain(-10) + silence_after_beat
    first_beat_sound = Sine(2000).to_audio_segment(duration=50).apply_gain(-10) + silence_after_beat

    metronome = AudioSegment.silent(duration=0)
    for beat in range(num_beats):
        count = (beat % 8) + 1  # Determine the count within the 8-count cycle
        if count == 1:
            metronome += first_beat_sound
        elif count in counts:
            metronome += regular_beat_sound
        else:
            metronome += AudioSegment.silent(duration=beat_interval)

    return metronome


def create_instruction_audio(instructions, bpm, output_file="output.mp3"):
    """
    Create an audio file with instructions at specified beats, using speedup if needed.

    :param instructions: List of tuples (instruction_text, beat_number).
    :param bpm: Beats per minute.
    :param output_file: Output audio file name.
    """
    beat_interval = 60 / bpm  # Seconds per beat
    combined_audio = AudioSegment.silent(duration=0)  # Start with an empty audio

    for i, (instruction, beat) in enumerate(instructions):
        # Convert instruction to an audio chunk
        instruction_audio = text_to_audio_chunk(instruction)

        # Calculate timing for this and the next instruction
        current_start_time = int((beat - 1) * beat_interval * 1000)  # Current instruction start time (ms)
        next_start_time = (
            int((instructions[i + 1].beat - 1) * beat_interval * 1000) if i + 1 < len(instructions) else None
        )

        # Calculate available time for this instruction
        available_time = next_start_time - current_start_time if next_start_time else None

        # If the instruction audio is too long, speed it up to fit
        if available_time and len(instruction_audio) > available_time:
            speed_factor = len(instruction_audio) / available_time
            instruction_audio = instruction_audio.speedup(playback_speed=speed_factor)

        if available_time and available_time > len(instruction_audio):
            padding_after_duration = available_time - len(instruction_audio)
            instruction_audio += AudioSegment.silent(duration=padding_after_duration)

        # Add silence to align the start time
        padding_before_duration = current_start_time - len(combined_audio)
        if padding_before_duration > 0:
            combined_audio += AudioSegment.silent(duration=padding_before_duration)

        # Append the instruction audio
        combined_audio += instruction_audio

    metronome = create_metronome_track(bpm, instructions[-1].beat + 8)

    final_audio = metronome.overlay(combined_audio)

    # Save the final audio file
    final_audio.export(output_file, format="mp3")
    print(f"Audio file saved as {output_file}")


def correct_times(instructions):
    return [
        TimedInstruction(" i ".join([ins.instruction for ins in group]), beat)
        for beat, group in groupby(instructions, key=lambda ins: ins.beat)
    ]


def get_instruction_collector_callback(instructions):
    def callback(params):
        if params.is_only_option:
            return
        signal_beat = params.current_beat + params.waiting
        instruction_beat = signal_beat - 4
        # if signal_beat % 4 == 0:
        #     instruction_beat = signal_beat - 4
        # else:
        #     instruction_beat = signal_beat // 4 * 4
        instructions.append(TimedInstruction(params.next_node, instruction_beat))

    return callback
