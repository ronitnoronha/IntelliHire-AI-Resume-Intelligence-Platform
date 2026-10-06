import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Keep the application usable after a normal pip install, where the
    # optional spaCy language model may not yet have been downloaded.
    nlp = spacy.blank("en")


def preprocess_text(text):
    """
    Tokenize, remove stopwords and lemmatize text.
    """

    doc = nlp(text.lower())

    tokens = []

    for token in doc:
        if token.is_stop:
            continue

        if token.is_punct:
            continue

        if token.is_space:
            continue

        tokens.append(token.lemma_ or token.text)

    return " ".join(tokens)
