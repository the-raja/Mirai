import ollama

from llm.prompts import SYSTEM_PROMPT


class DialogueEngine:

    def generate_dialogue(

        self,

        player_type,
        summary,
        familiarity,
        predicted_move
    ):

        prompt = f"""

    Player Type:
    {player_type}

    Aggression:
    {summary['aggression']}

    Defense:
    {summary['defense']}

    Panic:
    {summary['panic']}

    First Move:
    {summary['first_move']}

    Predicted Move:
    {predicted_move}

    Familiarity:
    {familiarity}

    Generate one short psychological line.
    """

        try:

            response = ollama.chat(

                model="llama3.2:latest",

                messages=[  

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception as e:

            print(f"Ollama Error: {e}")

            return "I am watching your every move. Do not think you can hide your patterns from MIRAI."