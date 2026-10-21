
import json
from pathlib import Path


def save_beam_data(file_path, beam_data):
    """Save beam input data to a JSON file."""

    path = Path(file_path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(beam_data, file, indent=4)


def load_beam_data(file_path):
    """Load beam input data from a JSON file."""

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        beam_data = json.load(file)

    if not isinstance(beam_data, dict):
        raise ValueError("The JSON file must contain an object.")

    return beam_data
