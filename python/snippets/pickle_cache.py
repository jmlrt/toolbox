import os.path
import pickle


class Person:
    def __init__(self, first_name, last_name, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date

        cache_file = self.get_cache_file(first_name, last_name)
        print(f"Dumping {self} to {cache_file}")
        with open(cache_file, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def get_person(cls, first_name, last_name, birth_date):
        cache_file = cls.get_cache_file(first_name, last_name)
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        return Person(first_name, last_name, birth_date)

    @classmethod
    def get_cache_file(cls, first_name, last_name):
        return f".cache/persons/{first_name}_{last_name}.pickle"
