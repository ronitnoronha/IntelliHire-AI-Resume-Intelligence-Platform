import fitz


def extract_name(source):
    """
    Extract the largest text near the top of page 1.
    """

    if isinstance(source, (bytes, bytearray)):
        doc = fitz.open(stream=source, filetype="pdf")
    else:
        doc = fitz.open(source)
    page = doc[0]

    data = page.get_text("dict")

    candidates = []

    for block in data["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            text = ""

            max_size = 0

            for span in line["spans"]:
                text += span["text"]

                max_size = max(max_size, span["size"])

            text = text.strip()

            if len(text) < 3:
                continue

            candidates.append({"text": text, "size": max_size, "y": line["bbox"][1]})

    doc.close()

    # Highest font size first
    candidates.sort(key=lambda x: (-x["size"], x["y"]))

    return candidates[0]["text"] if candidates else "Name Not Found"
