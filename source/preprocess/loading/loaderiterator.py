from pathlib import Path
from typing import List, Dict, Optional
import os
from source.preprocess.loading.serialization import Serializer

import json
from pathlib import Path

def save_filenames(filename_list, json_file="processed_files.json"):
    json_file_path = Path(json_file)
    if json_file_path.exists():
        with open(json_file_path, 'r') as f:
            existing_list = json.load(f)
        updated_list = existing_list + filename_list
    else:
        updated_list = filename_list

    with open(json_file_path, 'w') as f:
        json.dump(updated_list, f)

class LoaderIterator:
    """Iterator that loads data from multiple files in batches"""

    def __init__(
        self,
        serializer: Serializer,
        num_files_per_iteration: int,
        load_paths: Optional[List[Path]] = None,
    ) -> None:
        self.serializer = serializer
        self.num_files_per_iteration = num_files_per_iteration
        self._load_paths = load_paths
        self._current_iteration = None

    @property
    def load_paths(self) -> Optional[List[Path]]:
        return self._load_paths

    @load_paths.setter
    def load_paths(self, load_paths: List[Path]) -> None:
        self._load_paths = load_paths

    def __iter__(self):
        if self._current_iteration is None:
            self._current_iteration = 0
        return self

    def __next__(self) -> List[Dict]:
        if self._did_load_all_batches():
            raise StopIteration
        data_batch = self._load_data_batch()
        self._current_iteration += 1
        return data_batch

    def set_current_iteration(self, iteration: int) -> None:
        """Set the current iteration for the loader."""
        self._current_iteration = iteration

    def write_current_iteration(self, file_path: str) -> None:
        """Write the current iteration to a file."""
        with open(file_path, "w") as f:
            f.write(str(self._current_iteration))

    def _did_load_all_batches(self) -> bool:
        if (
            self._current_iteration
            >= len(self._load_paths) / self.num_files_per_iteration
        ):
            return True
        return False

    def _load_data_batch(self) -> List[Dict]:
        start_index = self._current_iteration * self.num_files_per_iteration
        stop_index = start_index + self.num_files_per_iteration
        batch = []
        process_midi_files = []
        for load_path in self._load_paths[start_index:stop_index]:
            if load_path.exists():
                try:
                    data = self.serializer.load(load_path)
                    batch.append(data)
                    process_midi_files.append(str(load_path))
                except Exception as e:
                    print(f"Failed to load data from {load_path}: {e}")
                    if "The_Real_Thing.2_20" in load_path.name:
                        print()
        save_filenames(process_midi_files)
        return batch
