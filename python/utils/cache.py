import logging
import pickle
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "python"


def cache_object(object, filename):
    cache_file = CACHE_DIR / filename
    Path(cache_file).parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump(object, f)
    logging.info(f"{object} has been cached to {cache_file}")


def retrieve_object_from_cache(filename):
    cache_file = CACHE_DIR / filename
    if cache_file.exists():
        with open(cache_file, "rb") as f:
            object = pickle.load(f)
            logging.info(f"{object} has been retrieved from {cache_file}")
            return object
    return None
