import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import re
import json
import pandas as pd
from music21 import converter
from music21.stream.base import Score
from music21 import metadata
from glob import glob
from source.preprocess.preprocessutilities import keep_first_n_measures
from source.preprocess import chord_preprocesing


class Serializer(ABC):
    """Interface for concrete Seralization methods."""

    @abstractmethod
    def dump(self, obj: Any, save_path: Path) -> None:
        pass

    @abstractmethod
    def load(self, load_path: Path) -> Any:
        pass


class Music21Serializer(Serializer):

    """Saves and loads a Music21 file. It's a concrete serializer."""

    def __init__(
            self,
            lakh_clean_version: str = "8bars",
            save_format: str = "midi",
            genre_file: Path = "/MMM_tokenization_customized/source/preprocess/loading/"+"lmd_genres.csv",
    ) -> None:
        self.save_format = save_format
        # Read the genre CSV file into a DataFrame.
        
        self.genre_df = pd.read_csv(genre_file)
        self.bars_per_track = int(lakh_clean_version.replace("bars", ""))

        if lakh_clean_version == "4bars":
            self.music_metadata_path = "/Users/apoxeredhs/Documents/MyProjects/datasets/MIDI/lmd_metadata/metadata_lmd_clean_chunked_4bars/"
        elif lakh_clean_version == "8bars":
            self.music_metadata_path = "/Users/apoxeredhs/Documents/MyProjects/datasets/MIDI/lmd_metadata/metadata_lmd_clean_chunked_8bars/"
        elif lakh_clean_version == "16bars":
            self.music_metadata_path = "/Users/apoxeredhs/Documents/MyProjects/datasets/MIDI/lmd_metadata/metadata_lmd_clean_chunked_16bars/"
        else:
            raise ValueError("Cant link to the directory of the musical metadata")

    def dump(self, m21_stream: Score, save_path: Path) -> None:
        m21_stream.write(fmt=self.save_format, fp=save_path, quantizePost=False)

    def load(self, load_path: Path) -> Score:
        print("I AM IN HERE")
        # Get the number of bars for the current segment
        bar_length = str(load_path).split('bars')[0].split('_')[-1]

        # Extract the artist name from the load_path.
        artist_name = load_path.parts[-2]

        # Search for the artist name in the DataFrame.
        genre_row = self.genre_df.loc[self.genre_df["Artist"] == artist_name]

        # Get the genre if the artist was found.
        genre = genre_row["Genre_ChatGPT"].values[0] if not genre_row.empty else "other"
        artist = artist_name
        artist = re.sub(r'[^\w]', '', artist.upper())
        print("---ALSO HERE---")


        # Check if the file has metadata on KEY, BPM & CHORD PROGRESSION
        try:
            music_metadata_fname = ('/').join(load_path.parts[-1:]).replace(".mid", ".json")
            music_metadata_fullpath = glob(self.music_metadata_path + f"/*/{music_metadata_fname}")
            music_metadata_fullpath = music_metadata_fullpath[0]
            # music_metadata_fname = ('/').join(load_path.parts[-1:]).replace(".mid", ".wav.json")
            # music_metadata_fullpath = glob(self.music_metadata_path + f"/*/{music_metadata_fname}")
            # if len(music_metadata_fullpath) == 0:
            #     music_metadata_fname = ('/').join(load_path.parts[-1:]).replace(".mid", ".json")
            #     music_metadata_fullpath = glob(self.music_metadata_path + f"/*/{music_metadata_fname}")
            # music_metadata_fullpath = music_metadata_fullpath[0]
        except FileExistsError:
            print(f"Metadata file not found: {music_metadata_fullpath}")
            raise ValueError("Metadata file not found")

        key = None
        bpm = None
        chord_progression = None
        fname = load_path.parts[-1].replace(".mid","")

        if os.path.exists(music_metadata_fullpath):
            with open(music_metadata_fullpath, "r") as f:

                music_metadata = json.load(f)

                # Account for double-BPM detection of unusually high BPMs
                bpm = music_metadata["bpm"]
                if int(bpm) >= 160:
                    bpm = round((int(bpm) / 2) / 5) * 5
                    bpm = str(bpm)

                key = music_metadata["key"]
                chord_progression = music_metadata["chord_progression"][0]
                chord_progression = chord_preprocesing.find_most_frequent_chord_progression(chord_progression)
                print(chord_progression)
                #chord_progression = chord_preprocesing.standard_to_roman(key,chord_progression)
                chord_progression = ('_').join(chord_progression)
                print(chord_progression)
        else:
            print(f"Metadata file WAS found BUT metadata values are missing: {music_metadata_fullpath}")
            raise ValueError("Metadata file not found")
            key = 'NA'
            bpm = 'NA'
            chord_progression = 'NA'
        # Load the score from the file.
        print(f"Loading {load_path}")

        stream = converter.parse(load_path, quantizePost=False)
        # Remove final measure with just rests
        stream = keep_first_n_measures(stream,num_of_measuers=self.bars_per_track)
        # Add metadata
        stream.insert(0, metadata.Metadata())

        # Set metadata
        stream.metadata.title = load_path.parts[-1].split(".")[0]
        if genre is not None:
            stream.metadata.setCustom("genre", genre)
        if artist is not None:
            stream.metadata.setCustom("artist", artist)

        # Set key, bpm and chord progression
        stream.metadata.setCustom("fname", fname)
        stream.metadata.setCustom("key", key)
        stream.metadata.setCustom("bpm", bpm)
        stream.metadata.setCustom("chord_progression_belinda", chord_progression)
        stream.metadata.setCustom("bar_length", bar_length)

        return stream
