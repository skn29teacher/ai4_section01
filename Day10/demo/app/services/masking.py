import re


def mask_text(text, expressions):
    """Union all literal matching spans, including overlapping occurrences."""
    masked = bytearray(len(text))
    for expression in expressions:
        for match in re.finditer("(?=" + re.escape(expression) + ")", text, flags=re.IGNORECASE):
            start = match.start()
            masked[start:start + len(expression)] = b"\x01" * len(expression)
    return "".join("*" if masked[i] else character for i, character in enumerate(text))
