import random

class BiasedRandomChoice:
    def __init__(self, items, bias_factor=0.5, recovery_rate=0.1):
        """
        Initialize the biased random choice object.
        
        :param items: List of all possible items to choose from.
        :param bias_factor: Factor to reduce the weight of recently chosen items.
                            (0 < bias_factor < 1, smaller values reduce weight more).
        :param recovery_rate: Rate at which weights recover (0 < recovery_rate <= 1).
                              Higher values lead to faster recovery.
        """
        self.items = items
        self.weights = {item: 1 for item in items}
        self.bias_factor = bias_factor
        self.recovery_rate = recovery_rate
        self.last_chosen = None

    def choose(self, subset):
        """
        Choose an item from the provided subset with a weighted random probability.
        Reduce weight for the chosen item and gradually recover weights for others.

        :param subset: List of items to choose from (must be a subset of all items).
        :return: The chosen item.
        """
        if not subset:
            raise ValueError("Subset cannot be empty.")
        if not all(item in self.items for item in subset):
            raise ValueError("Subset contains items not in the original list.")

        # Normalize weights for the subset
        subset_weights = [self.weights[item] for item in subset]
        total_weight = sum(subset_weights)
        normalized_weights = [w / total_weight for w in subset_weights]

        # Choose an item
        chosen_index = random.choices(range(len(subset)), weights=normalized_weights, k=1)[0]
        chosen_item = subset[chosen_index]

        # Update weights
        for item in self.weights:
            if item == chosen_item:
                self.weights[item] *= self.bias_factor  # Reduce weight for the chosen item
            else:
                # Gradually recover weights for all other items
                self.weights[item] = min(1, self.weights[item] + self.recovery_rate * (1 - self.weights[item]))

        self.last_chosen = chosen_item
        return chosen_item
