import re

import fitz


def extract_text_from_pdf(source):

    if isinstance(source, (bytes, bytearray)):
        doc = fitz.open(stream=source, filetype="pdf")
    else:
        doc = fitz.open(source)

    text = ""

    for page in doc:
        blocks = page.get_text("blocks")

        # Sort blocks by vertical position then horizontal position
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

        for block in blocks:
            text += block[4] + "\n"

    doc.close()

    return text


def clean_resume_text(text):
    # Join only genuinely letter-spaced text (for example, "J o h n").
    # Removing every space between letters turns normal phrases such as
    # "Data Scientist" into "DataScientist" and hurts matching.
    def join_letter_spaced_word(match):
        joined = re.sub(r"\s+", "", match.group())
        # A capital letter after lowercase letters marks the next name-like
        # word in text such as "J o h n D o e".
        return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", joined)

    text = re.sub(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b", join_letter_spaced_word, text)

    # Apply the equivalent repair to digit-spaced identifiers, without
    # changing normal numbers or line formatting.
    text = re.sub(
        r"\b(?:\d\s+){2,}\d\b", lambda match: re.sub(r"\s+", "", match.group()), text
    )

    # Fix emails
    text = re.sub(r"\s*@\s*", "@", text)
    text = re.sub(r"([A-Za-z0-9._%+-])\s+([A-Za-z0-9._%+-]+@)", r"\1\2", text)

    text = re.sub(r"\s*\.\s*", ".", text)

    return text
