import os
import os.path as op
import re
import joblib
from spacy import displacy
from pythainlp import tokenize
from .utils import (
    preprocess,
    is_stopword,
    merge_tokens,
    merge_labels,
    get_digit,
)
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# read model from models path, define colors for output classes
MODULE_PATH = os.path.dirname(__file__)
CRF_MODEL = joblib.load(op.join(MODULE_PATH, "models", "model.joblib"))
COLORS = {
    "NAME": "#fbd46d",
    "ADDR": "#ff847c",
    "LOC": "#87d4c5",
    "POST": "#def4f0",
    "PHONE": "#ffbffe",
    "EMAIL": "#91a6b8",
}


def display_entities(tokens: list, labels: list):
    """
    Display tokens and labels

    References
    ----------
    Spacy, https://spacy.io/usage/visualizers
    """
    options = {"ents": list(COLORS.keys()), "colors": COLORS}

    ents = []
    text = ""
    s = 0
    for token, label in zip(tokens, labels):
        text += token
        if label != "O":
            ents.append({"start": s, "end": s + len(token), "label": label})
        s += len(token)

    text_display = {"text": text, "ents": ents, "title": None}
    displacy.render(
        text_display, style="ent", options=options, manual=True, jupyter=True
    )


def tokens_to_features(tokens: list, i: int) -> dict:
    """
    List of tokens to features for inputting to CRF suite
    """
    if len(tokens[i]) == 2:
        word, _ = tokens[i]  # unpack word and class
    else:
        word = tokens[i]

    # Features from current word
    features = {
        "bias": 1.0,
        "word.word": word,
        "word.isspace()": word.isspace(),
        "word.is_stopword()": is_stopword(word),
        "word.isdigit()": word.isdigit(),
    }
    if word.strip().isdigit() and len(word) == 5:
        features["word.islen5"] = True

    # Features from previous word
    if i > 0:
        prevword = tokens[i - 1][0]
        features.update(
            {
                "-1.word.prevword": prevword,
                "-1.word.isspace()": prevword.isspace(),
                "-1.word.is_stopword()": is_stopword(prevword),
                "-1.word.isdigit()": prevword.isdigit(),
            }
        )
    else:
        features["BOS"] = True  # Special "Beginning of Sequence" tag

    # Features from next word
    if i < len(tokens) - 1:
        nextword = tokens[i + 1][0]
        features.update(
            {
                "+1.word.nextword": nextword,
                "+1.word.isspace()": nextword.isspace(),
                "+1.word.is_stopword()": is_stopword(nextword),
                "+1.word.isdigit()": nextword.isdigit(),
            }
        )
    else:
        features["EOS"] = True  # Special "End of Sequence" tag

    return features


def parse(text: str, display: bool = False, tokenize_engine="deepcut") -> dict:
    """
    Parse a given address text and give a dictionary of
    parsed address out

    Parameters
    ----------
    text: str, input Thai address text to be parsed
    display: bool, if True, we will display parsed output
    tokenize_engine: str, pythainlp tokenization engines default is deepcut

    Output
    ------
    address: dict, parsed output 
    """
    text = preprocess(text)

    tokens = tokenize.word_tokenize(text, engine=tokenize_engine)
    features = [tokens_to_features(tokens, i) for i in range(len(tokens))]
    preds = CRF_MODEL.predict([features])[0]

    preds_ = list(zip(tokens, preds))
    name = "".join([token for token, c in preds_ if c == "NAME"]).strip()
    address = "".join([token for token, c in preds_ if c == "ADDR"]).strip()
    location = "".join([token for token, c in preds_ if c == "LOC"]).strip()
    postal_code = " ".join([token for token, c in preds_ if c == "POST"]).strip()
    postal_code = "".join([p for p in postal_code if p.isdigit()])
    phone_number = " ".join([get_digit(token) for token, c in preds_
                            if c == "PHONE" and len(token) > 1]).strip()
    phone_number = "".join([p for p in phone_number if p.isdigit()])

    email = "".join([token for token, c in preds_ if c == "EMAIL"]).strip()
    if email == "":
        emails = re.findall(r"\b[\w.-]+?@\w+?\.\w+?\b", text)
        if len(emails) > 0:
            email = emails[0]

    # display parsed entities
    if display:
        merge, labels = merge_labels(preds)
        tokens = merge_tokens(tokens, merge)
        display_entities(tokens, labels)

    return {
        "text": text,
        "name": name,
        "address": address,
        "location": location,
        "postal_code": postal_code,
        "phone_number": phone_number,
        "email": email,
    }
