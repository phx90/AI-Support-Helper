import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    page: int | None
    chunk_index: int
    section: str | None


class TechnicalTextChunker:
    def __init__(self, size: int, overlap: int):
        if overlap >= size:
            raise ValueError("chunk overlap must be smaller than chunk size")
        self.size, self.overlap = size, overlap

    def split(self, pages: list[tuple[int | None, str]]) -> list[TextChunk]:
        result = []
        index = 0
        for page, text in pages:
            clean = re.sub(r"[ \t]+", " ", text)
            clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
            start = 0
            while start < len(clean):
                end = min(start + self.size, len(clean))
                if end < len(clean):
                    boundary = max(clean.rfind("\n", start, end), clean.rfind(". ", start, end))
                    end = boundary + 1 if boundary > start + self.size // 2 else end
                body = clean[start:end].strip()
                if body:
                    heading = next(
                        (x.lstrip("# ") for x in body.splitlines() if x.startswith("#")), None
                    )
                    result.append(TextChunk(body, page, index, heading))
                    index += 1
                if end >= len(clean):
                    break
                start = max(start + 1, end - self.overlap)
        return result
