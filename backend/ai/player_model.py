class PlayerModel:

    def classify(self, summary):

        aggression = summary["aggression"]
        defense = summary["defense"]
        panic = summary["panic"]

        move_counts = summary["move_counts"]

        bluff_count = move_counts.get("bluff", 0)

        # Aggressive
        if aggression >= 0.7:
            return "Aggressive"

        # Defensive
        if defense >= 0.5:
            return "Defensive"

        # Panic Player
        if panic >= 0.3:
            return "Panic"

        # Trickster
        if bluff_count >= 3:
            return "Trickster"

        # Balanced
        return "Balanced"