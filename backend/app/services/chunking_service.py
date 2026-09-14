import re
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DialogueTurn:
    speaker: str
    timestamp: Optional[str]
    text: str


@dataclass
class ChunkData:
    chunk_index: int
    content: str
    timestamp: Optional[str]
    token_count: int


class ChunkingService:
    """
    Dialogue-aware transcript chunking service.
    Preserves speaker attribution, conversational context, and timestamps.
    """

    # Regex matching speaker lines:
    # e.g.: **Casey Winters** (14:20): or Lenny (01:23:45): or **Lenny Rachitsky**:
    TURN_PATTERN = re.compile(
        r'(?:^|\n)(?:\*\*(?P<bold_speaker>[^*]+)\*\*|(?P<plain_speaker>[A-Z][A-Za-z0-9\s.-]{1,40}))'
        r'(?:\s*\((?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\))?:\s*',
        re.MULTILINE,
    )

    @classmethod
    def parse_turns(cls, text: str) -> List[DialogueTurn]:
        """Parses transcript text into individual speaker turns."""
        turns: List[DialogueTurn] = []
        matches = list(cls.TURN_PATTERN.finditer(text))

        if not matches:
            # Fallback: split by double newline paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for p in paragraphs:
                turns.append(DialogueTurn(speaker="Unknown", timestamp=None, text=p))
            return turns

        for i, match in enumerate(matches):
            speaker = (match.group("bold_speaker") or match.group("plain_speaker") or "Speaker").strip()
            timestamp = match.group("timestamp")
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            turn_text = text[start_pos:end_pos].strip()

            if turn_text:
                turns.append(DialogueTurn(speaker=speaker, timestamp=timestamp, text=turn_text))

        return turns

    @classmethod
    def chunk_transcript(
        cls,
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> List[ChunkData]:
        """
        Splits dialogue turns into overlapping semantic passages.
        Preserves speaker attribution and earliest timestamp per chunk.
        """
        turns = cls.parse_turns(text)
        if not turns:
            return []

        chunks: List[ChunkData] = []
        current_turns: List[DialogueTurn] = []
        current_char_count = 0
        chunk_index = 0

        i = 0
        while i < len(turns):
            turn = turns[i]
            turn_repr = f"**{turn.speaker}**" + (f" ({turn.timestamp}): " if turn.timestamp else ": ") + turn.text
            turn_len = len(turn_repr)

            # If a single turn is larger than 1.5 * chunk_size, split by sentences
            if turn_len > chunk_size * 1.5 and not current_turns:
                sub_chunks = cls._split_large_turn(turn, chunk_size, chunk_overlap)
                for sub in sub_chunks:
                    chunks.append(
                        ChunkData(
                            chunk_index=chunk_index,
                            content=sub.text,
                            timestamp=sub.timestamp or turn.timestamp,
                            token_count=len(sub.text.split()),
                        )
                    )
                    chunk_index += 1
                i += 1
                continue

            current_turns.append(turn)
            current_char_count += turn_len + 2  # +2 for \n\n

            # Check if threshold reached
            if current_char_count >= chunk_size or i == len(turns) - 1:
                # Build chunk content
                chunk_text = "\n\n".join(
                    f"**{t.speaker}**" + (f" ({t.timestamp}): " if t.timestamp else ": ") + t.text
                    for t in current_turns
                ).strip()

                earliest_ts = next((t.timestamp for t in current_turns if t.timestamp), None)
                chunks.append(
                    ChunkData(
                        chunk_index=chunk_index,
                        content=chunk_text,
                        timestamp=earliest_ts,
                        token_count=len(chunk_text.split()),
                    )
                )
                chunk_index += 1

                # Calculate overlap: retain tail turns that fit within chunk_overlap
                if i < len(turns) - 1:
                    overlap_turns: List[DialogueTurn] = []
                    accum_overlap = 0
                    for t in reversed(current_turns):
                        t_len = len(t.text)
                        if accum_overlap + t_len <= chunk_overlap or not overlap_turns:
                            overlap_turns.insert(0, t)
                            accum_overlap += t_len
                        else:
                            break
                    current_turns = overlap_turns
                    current_char_count = sum(len(t.text) + 20 for t in current_turns)
                else:
                    current_turns = []
                    current_char_count = 0

            i += 1

        logger.info(f"Chunked transcript into {len(chunks)} chunks (target size={chunk_size}, overlap={chunk_overlap}).")
        return chunks

    @classmethod
    def _split_large_turn(cls, turn: DialogueTurn, chunk_size: int, chunk_overlap: int) -> List[DialogueTurn]:
        """Splits an oversized monologue turn into smaller chunks with speaker preserved."""
        sentences = re.split(r'(?<=[.?!])\s+', turn.text)
        sub_turns: List[DialogueTurn] = []
        cur_sentences: List[str] = []
        cur_len = 0

        header = f"**{turn.speaker}**" + (f" ({turn.timestamp}): " if turn.timestamp else ": ")

        for s in sentences:
            cur_sentences.append(s)
            cur_len += len(s) + 1
            if cur_len >= chunk_size:
                body = " ".join(cur_sentences).strip()
                sub_turns.append(DialogueTurn(speaker=turn.speaker, timestamp=turn.timestamp, text=f"{header}{body}"))
                # Retain last sentence for overlap
                cur_sentences = [cur_sentences[-1]] if cur_sentences else []
                cur_len = len(cur_sentences[0]) if cur_sentences else 0

        if cur_sentences:
            body = " ".join(cur_sentences).strip()
            sub_turns.append(DialogueTurn(speaker=turn.speaker, timestamp=turn.timestamp, text=f"{header}{body}"))

        return sub_turns
