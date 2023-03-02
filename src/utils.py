import string


def normalise_tag(tag: str):
    """We want to:
    1. lowercase
    2. remove all punctuation and replace with a space
    3. remove all excess whitespace
    4. replace all spaces with hyphen
    """
    normalised_tag = tag.lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    normalised_tag = ' '.join(normalised_tag.strip().split())
    normalised_tag = normalised_tag.replace(' ', '-')
    return normalised_tag


def normalise_tags(*tags: str):
    return [normalise_tag(tag) for tag in tags]
