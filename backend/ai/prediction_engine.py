from collections import Counter

class PredictionEngine:
    def predict_next_move(self, move_history):
        if len(move_history) < 3:
            return None

        # Look for the last 2 moves (the 'context')
        context = tuple(move_history[-2:])
        
        # Search history for what usually follows this context
        patterns = []
        for i in range(len(move_history) - 2):
            if tuple(move_history[i:i+2]) == context:
                if i + 2 < len(move_history):
                    patterns.append(move_history[i+2])
        
        if not patterns:
            # Fallback to simple repetition if no sequence is found
            if move_history[-1] == move_history[-2]:
                return move_history[-1]
            return None
            
        # Return the most frequent following move
        return Counter(patterns).most_common(1)[0][0]
