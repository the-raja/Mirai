class EmbeddingEngine:

    def create_behavior_vector(
        self,
        summary
    ):

        aggression = summary["aggression"]

        defense = summary["defense"]

        panic = summary["panic"]

        move_counts = summary["move_counts"]

        total_moves = sum(
            move_counts.values()
        )

        predictability = 0

        if total_moves > 0:

            most_used = max(
                move_counts.values()
            )

            predictability = round(
                most_used / total_moves,
                2
            )

        vector = [

            aggression,
            defense,
            panic,
            predictability
        ]

        return vector