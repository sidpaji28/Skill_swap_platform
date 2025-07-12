from detoxify import Detoxify

def is_spammy(description: str) -> bool:
    results = Detoxify('original').predict(description)
    return results['toxicity'] > 0.7 or results['insult'] > 0.5
