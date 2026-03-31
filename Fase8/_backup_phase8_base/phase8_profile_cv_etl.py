"""Deterministic ETL helpers for CV normalization and structuring."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Iterable
import unicodedata
from uuid import UUID

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
_URL_RE = re.compile(r"(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?")
_WORD_RE = re.compile(r"\w+", re.UNICODE)
_MULTI_SPACE_RE = re.compile(r"[ \t]+")

_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "contact": ("contacto", "datos de contacto", "contact"),
    "summary": ("perfil", "resumen", "about me", "sobre mi", "presentacion"),
    "experience": ("experiencia", "experiencia laboral", "work experience"),
    "education": ("formacion", "educacion", "education", "studies"),
    "skills": ("habilidades", "herramientas", "skills", "tecnologias", "stack"),
    "languages": ("idiomas", "languages"),
    "certifications": ("certificaciones", "certificados", "certifications"),
}


def _dedupe(values: Iterable[str]) -> list[str]:
    """Return values preserving order and removing duplicates."""

    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _normalize_heading(value: str) -> str:
    """Normalize potential section headings for comparison."""

    ascii_like = unicodedata.normalize("NFKD", value)
    ascii_like = "".join(ch for ch in ascii_like if not unicodedata.combining(ch))
    ascii_like = ascii_like.lower().replace(":", " ")
    ascii_like = re.sub(r"[^a-z0-9 ]+", " ", ascii_like)
    return " ".join(ascii_like.split())


def normalize_cv_text(raw_text: str) -> str:
    """Normalize OCR/raw text keeping semantic line breaks."""

    normalized = unicodedata.normalize("NFKC", raw_text)
    lines: list[str] = []

    for raw_line in normalized.splitlines():
        line = _MULTI_SPACE_RE.sub(" ", raw_line).strip()
        if not line:
            lines.append("")
            continue

        for symbol in ("•", "·", "●", "«", "»", "◦", "▪"):
            line = line.replace(symbol, "-")

        if re.match(r"^[eE]\s+", line):
            line = "- " + line[2:].strip()
        elif line.startswith("-") and not line.startswith("- "):
            line = "- " + line[1:].strip()

        lines.append(line)

    compact = "\n".join(lines)
    compact = re.sub(r"\n{3,}", "\n\n", compact)
    return compact.strip()


def split_cv_sections(normalized_text: str) -> dict[str, str]:
    """Split a normalized CV text into canonical sections."""

    buckets: dict[str, list[str]] = {key: [] for key in _SECTION_ALIASES}
    buckets["other"] = []

    current_section = "other"
    for line in normalized_text.splitlines():
        stripped = line.strip()
        heading = _normalize_heading(stripped)

        found_section = None
        for key, aliases in _SECTION_ALIASES.items():
            if heading in aliases:
                found_section = key
                break

        if found_section is not None:
            current_section = found_section
            continue

        buckets[current_section].append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in buckets.items()
        if "\n".join(value).strip()
    }


def extract_entities(normalized_text: str) -> dict[str, list[str]]:
    """Extract deterministic entities from normalized CV text."""

    emails = _dedupe(email.lower() for email in _EMAIL_RE.findall(normalized_text))

    phones_raw = _PHONE_RE.findall(normalized_text)
    phones = _dedupe(re.sub(r"\D", "", value) for value in phones_raw)
    phones = [phone for phone in phones if len(phone) >= 9]

    urls_raw = _URL_RE.findall(normalized_text)
    urls = []
    for url in urls_raw:
        clean_url = url.rstrip(".,);]")
        if clean_url.startswith("www."):
            clean_url = "https://" + clean_url
        elif not clean_url.startswith("http"):
            clean_url = "https://" + clean_url
        urls.append(clean_url.lower())
    urls = _dedupe(urls)

    linkedin = [url for url in urls if "linkedin.com" in url]
    github = [url for url in urls if "github.com" in url]

    return {
        "emails": emails,
        "phones": phones,
        "urls": urls,
        "linkedin": linkedin,
        "github": github,
    }


def build_quality_report(
    normalized_text: str,
    sections: dict[str, str],
    entities: dict[str, list[str]],
) -> dict[str, int | float | bool | list[str]]:
    """Compute simple quality metrics for downstream review."""

    total_chars = len(normalized_text)
    total_words = len(_WORD_RE.findall(normalized_text))

    unusual_chars = {"�", "¤", "§", "¬", "|", "~"}
    unusual_count = sum(1 for ch in normalized_text if ch in unusual_chars)
    noise_ratio = round((unusual_count / total_chars), 4) if total_chars else 1.0

    non_empty_sections = sorted(key for key, value in sections.items() if value.strip())

    score = 100
    if total_chars < 600:
        score -= 20
    if len(non_empty_sections) < 3:
        score -= 20
    if not entities.get("emails") and not entities.get("phones"):
        score -= 20
    if noise_ratio > 0.03:
        score -= 10
    if "experience" not in sections:
        score -= 10
    if "education" not in sections:
        score -= 10

    score = max(0, min(100, score))
    needs_manual_review = score < 60

    return {
        "quality_score": score,
        "total_chars": total_chars,
        "total_words": total_words,
        "noise_ratio": noise_ratio,
        "section_count": len(non_empty_sections),
        "sections_detected": non_empty_sections,
        "needs_manual_review": needs_manual_review,
    }


def build_profile_etl_payload(
    user_id: UUID,
    cv_filename: str,
    raw_text: str,
    normalized_text: str,
    extraction_method: str,
    uploaded_at: datetime,
    desired_role: str | None = None,
    transition_summary: str | None = None,
) -> dict[str, object]:
    """Build an ETL-oriented payload to persist in MinIO."""

    sections = split_cv_sections(normalized_text)
    entities = extract_entities(normalized_text)
    quality = build_quality_report(normalized_text, sections, entities)

    return {
        "version": "phase2-etl-v1",
        "user_id": str(user_id),
        "cv_filename": cv_filename,
        "uploaded_at": uploaded_at.isoformat(),
        "career_goal": {
            "desired_role": desired_role,
            "transition_summary": transition_summary,
        },
        "extraction": {
            "method": extraction_method,
            "raw_text_length": len(raw_text),
            "normalized_text_length": len(normalized_text),
        },
        "raw": {
            "cv_text": raw_text,
        },
        "normalized": {
            "cv_text": normalized_text,
            "sections": sections,
            "entities": entities,
        },
        "quality": quality,
    }
