import json
import os


class MemoryEngine:

    def __init__(self):

        # Get the absolute path of the directory this file is in
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Go up one level to the backend directory, then into memory
        self.MEMORY_FILE = os.path.join(
            base_path,
            "..",
            "memory",
            "player_memory.json"
        )


    def load_memory(self):
        if not os.path.exists(self.MEMORY_FILE):
            return {}

        try:
            with open(self.MEMORY_FILE, "r") as file:
                content = file.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return {}


    def save_memory(
        self,
        player_id,
        memory
    ):

        memories = self.load_memory()

        memories[player_id] = memory

        with open(self.MEMORY_FILE, "w") as file:

            json.dump(
                memories,
                file,
                indent=4
            )


    def get_player_memory(
        self,
        player_id
    ):

        memories = self.load_memory()

        return memories.get(player_id)