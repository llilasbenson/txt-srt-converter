import difflib
import re
from dataclasses import dataclass
from typing import List, Tuple

import streamlit as st


# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="TXT → SRT Aligner",
    page_icon="📝",
    layout="wide",
)


# -----------------------------
# Interface translations
# -----------------------------
TRANSLATIONS = {
    "English": {
        "app_title": "Corrected TXT → Timestamped SRT",
        "app_description": (
            "Upload a corrected plain-text transcript and the uncorrected SRT transcript "
            "from the same audio. The app compares the two texts, keeps the timing structure "
            "from the SRT, and fills those subtitle intervals only with text from the corrected TXT."
        ),
        "language": "Interface language",
        "txt_upload": "Upload corrected TXT transcript",
        "srt_upload": "Upload uncorrected SRT transcript",
        "txt_help": "The corrected transcript should correspond to the same audio as the SRT file.",
        "srt_help": "The subtitle text is used only for alignment. It is not copied into the output.",
        "process": "Generate corrected SRT",
        "missing_files": "Please upload both a TXT file and an SRT file.",
        "processing": "Comparing transcripts and restructuring the corrected text…",
        "success": "Corrected SRT generated successfully.",
        "download": "Download corrected SRT",
        "preview": "Output preview",
        "sequence": "Sequence",
        "timestamp": "Timestamp",
        "corrected_text": "Corrected subtitle text",
        "alignment": "Text alignment similarity",
        "alignment_help": (
            "This score compares normalized words in the original SRT text with the corrected TXT. "
            "A lower score can indicate that the files contain different audio, missing sections, "
            "or major changes in wording."
        ),
        "low_alignment": (
            "The alignment score is low. Review the output carefully because the two files may not "
            "represent the same complete recording or may differ substantially."
        ),
        "stats": "Processing summary",
        "srt_blocks": "SRT subtitle intervals",
        "source_words": "Words used from original SRT for alignment",
        "corrected_words": "Words found in corrected TXT",
        "output_words": "Corrected TXT words placed in output",
        "empty_blocks": "Subtitle intervals with no corrected text",
        "error_title": "Could not process the files",
        "no_srt_blocks": "No valid SRT subtitle blocks with timestamps were found.",
        "empty_txt": "The corrected TXT file does not contain usable text.",
        "empty_srt_text": (
            "The SRT contains timestamps but no usable subtitle text for alignment. "
            "The app cannot reliably map the corrected transcript to the timestamps."
        ),
        "privacy_note": (
            "The original SRT subtitle wording is used only inside the alignment process. "
            "The generated SRT is built from the corrected TXT text and the original SRT sequence/timestamps."
        ),
        "filename_suffix": "_corrected.srt",
    },
    "Español": {
        "app_title": "TXT corregido → SRT con marcas de tiempo",
        "app_description": (
            "Suba una transcripción corregida en texto plano y la transcripción SRT sin corregir "
            "del mismo audio. La aplicación compara ambos textos, conserva la estructura temporal "
            "del SRT y rellena esos intervalos únicamente con texto del TXT corregido."
        ),
        "language": "Idioma de la interfaz",
        "txt_upload": "Subir transcripción TXT corregida",
        "srt_upload": "Subir transcripción SRT sin corregir",
        "txt_help": "La transcripción corregida debe corresponder al mismo audio que el archivo SRT.",
        "srt_help": "El texto de los subtítulos se usa solo para la alineación. No se copia al resultado.",
        "process": "Generar SRT corregido",
        "missing_files": "Suba un archivo TXT y un archivo SRT.",
        "processing": "Comparando las transcripciones y reestructurando el texto corregido…",
        "success": "El SRT corregido se generó correctamente.",
        "download": "Descargar SRT corregido",
        "preview": "Vista previa del resultado",
        "sequence": "Secuencia",
        "timestamp": "Marca de tiempo",
        "corrected_text": "Texto corregido del subtítulo",
        "alignment": "Similitud de alineación textual",
        "alignment_help": (
            "Esta puntuación compara las palabras normalizadas del SRT original con el TXT corregido. "
            "Una puntuación baja puede indicar que los archivos contienen audios diferentes, secciones "
            "faltantes o cambios importantes en la redacción."
        ),
        "low_alignment": (
            "La puntuación de alineación es baja. Revise cuidadosamente el resultado porque los dos "
            "archivos podrían no corresponder a la misma grabación completa o diferir considerablemente."
        ),
        "stats": "Resumen del procesamiento",
        "srt_blocks": "Intervalos de subtítulos SRT",
        "source_words": "Palabras del SRT original usadas para la alineación",
        "corrected_words": "Palabras encontradas en el TXT corregido",
        "output_words": "Palabras del TXT corregido colocadas en el resultado",
        "empty_blocks": "Intervalos de subtítulos sin texto corregido",
        "error_title": "No se pudieron procesar los archivos",
        "no_srt_blocks": "No se encontraron bloques SRT válidos con marcas de tiempo.",
        "empty_txt": "El archivo TXT corregido no contiene texto utilizable.",
        "empty_srt_text": (
            "El SRT contiene marcas de tiempo, pero no texto de subtítulos utilizable para la alineación. "
            "La aplicación no puede asignar de forma fiable la transcripción corregida a las marcas de tiempo."
        ),
        "privacy_note": (
            "La redacción del SRT original se usa únicamente dentro del proceso de alineación. "
            "El SRT generado se construye con el texto del TXT corregido y las secuencias/marcas de tiempo del SRT original."
        ),
        "filename_suffix": "_corregido.srt",
    },
    "Português": {
        "app_title": "TXT corrigido → SRT com marcações de tempo",
        "app_description": (
            "Envie uma transcrição corrigida em texto simples e a transcrição SRT não corrigida "
            "do mesmo áudio. O aplicativo compara os dois textos, mantém a estrutura temporal "
            "do SRT e preenche esses intervalos somente com texto do TXT corrigido."
        ),
        "language": "Idioma da interface",
        "txt_upload": "Enviar transcrição TXT corrigida",
        "srt_upload": "Enviar transcrição SRT não corrigida",
        "txt_help": "A transcrição corrigida deve corresponder ao mesmo áudio do arquivo SRT.",
        "srt_help": "O texto das legendas é usado apenas para alinhamento. Ele não é copiado para o resultado.",
        "process": "Gerar SRT corrigido",
        "missing_files": "Envie um arquivo TXT e um arquivo SRT.",
        "processing": "Comparando as transcrições e reestruturando o texto corrigido…",
        "success": "O SRT corrigido foi gerado com sucesso.",
        "download": "Baixar SRT corrigido",
        "preview": "Prévia do resultado",
        "sequence": "Sequência",
        "timestamp": "Marcação de tempo",
        "corrected_text": "Texto corrigido da legenda",
        "alignment": "Similaridade do alinhamento textual",
        "alignment_help": (
            "Esta pontuação compara as palavras normalizadas do SRT original com o TXT corrigido. "
            "Uma pontuação baixa pode indicar que os arquivos contêm áudios diferentes, seções ausentes "
            "ou mudanças importantes na redação."
        ),
        "low_alignment": (
            "A pontuação de alinhamento é baixa. Revise o resultado com cuidado, pois os dois arquivos "
            "podem não representar a mesma gravação completa ou podem diferir consideravelmente."
        ),
        "stats": "Resumo do processamento",
        "srt_blocks": "Intervalos de legendas SRT",
        "source_words": "Palavras do SRT original usadas para alinhamento",
        "corrected_words": "Palavras encontradas no TXT corrigido",
        "output_words": "Palavras do TXT corrigido colocadas no resultado",
        "empty_blocks": "Intervalos de legendas sem texto corrigido",
        "error_title": "Não foi possível processar os arquivos",
        "no_srt_blocks": "Nenhum bloco SRT válido com marcações de tempo foi encontrado.",
        "empty_txt": "O arquivo TXT corrigido não contém texto utilizável.",
        "empty_srt_text": (
            "O SRT contém marcações de tempo, mas não contém texto de legenda utilizável para alinhamento. "
            "O aplicativo não pode mapear com segurança a transcrição corrigida para as marcações de tempo."
        ),
        "privacy_note": (
            "A redação do SRT original é usada somente dentro do processo de alinhamento. "
            "O SRT gerado é construído com o texto do TXT corrigido e as sequências/marcações de tempo do SRT original."
        ),
        "filename_suffix": "_corrigido.srt",
    },
}


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class SRTBlock:
    sequence: str
    timestamp: str
    text: str


# -----------------------------
# Text and file helpers
# -----------------------------
def decode_uploaded_file(file_bytes: bytes) -> str:
    """Decode common text-file encodings without adding external dependencies."""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_word(token: str) -> str:
    """
    Normalize a whitespace-delimited token for alignment.

    Keeps Unicode letters/numbers and internal apostrophes while ignoring
    capitalization and surrounding punctuation.
    """
    token = token.casefold()
    token = token.replace("’", "'").replace("`", "'")
    token = re.sub(r"[^\w']+", "", token, flags=re.UNICODE)
    token = token.strip("_'")
    return token


def lexical_units(text: str) -> Tuple[List[str], List[str], List[int]]:
    """
    Return:
      raw_tokens: all whitespace-delimited tokens in original wording
      normalized_words: normalized lexical tokens used for alignment
      raw_indexes: raw-token index corresponding to each normalized word
    """
    raw_tokens = text.split()
    normalized_words: List[str] = []
    raw_indexes: List[int] = []

    for raw_index, token in enumerate(raw_tokens):
        normalized = normalize_word(token)
        if normalized:
            normalized_words.append(normalized)
            raw_indexes.append(raw_index)

    return raw_tokens, normalized_words, raw_indexes


# -----------------------------
# SRT parsing
# -----------------------------
TIMESTAMP_RE = re.compile(
    r"^\s*\d{1,2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*"
    r"\d{1,2}:\d{2}:\d{2}[,.]\d{3}(?:\s+.*)?$"
)


def parse_srt(srt_text: str) -> List[SRTBlock]:
    """
    Parse standard SRT blocks while preserving the original timestamp line.

    The first line before a timestamp is treated as the sequence identifier.
    Additional lines after the timestamp are treated as subtitle text.
    """
    text = normalize_newlines(srt_text).strip()
    if not text:
        return []

    raw_blocks = re.split(r"\n[ \t]*\n+", text)
    parsed: List[SRTBlock] = []
    fallback_sequence = 1

    for raw_block in raw_blocks:
        lines = [line.rstrip() for line in raw_block.split("\n")]
        lines = [line for line in lines if line.strip()]

        if not lines:
            continue

        timestamp_index = next(
            (i for i, line in enumerate(lines) if TIMESTAMP_RE.match(line)),
            None,
        )
        if timestamp_index is None:
            continue

        if timestamp_index > 0:
            sequence = lines[timestamp_index - 1].strip()
        else:
            sequence = str(fallback_sequence)

        timestamp = lines[timestamp_index].strip()
        subtitle_lines = lines[timestamp_index + 1 :]
        subtitle_text = " ".join(line.strip() for line in subtitle_lines if line.strip())

        parsed.append(
            SRTBlock(
                sequence=sequence,
                timestamp=timestamp,
                text=subtitle_text,
            )
        )
        fallback_sequence += 1

    return parsed


# -----------------------------
# Alignment
# -----------------------------
def build_source_words(blocks: List[SRTBlock]) -> Tuple[List[str], List[int]]:
    """
    Build one normalized source-word sequence and the cumulative source-word
    boundary after each SRT block.
    """
    source_words: List[str] = []
    cumulative_boundaries: List[int] = [0]

    for block in blocks:
        _, block_words, _ = lexical_units(block.text)
        source_words.extend(block_words)
        cumulative_boundaries.append(len(source_words))

    return source_words, cumulative_boundaries


def build_anchor_points(
    source_words: List[str],
    corrected_words: List[str],
) -> Tuple[List[Tuple[int, float]], float]:
    """
    Compare source and corrected word sequences and produce monotonic anchor
    points that map source-word positions to corrected-word positions.

    The original SRT text is used only to establish these positions.
    """
    # Disable SequenceMatcher's "autojunk" heuristic for ordinary transcripts
    # because repeated short words can still be useful. Re-enable it only for
    # very large transcripts to avoid excessive runtime/memory use.
    use_autojunk = max(len(source_words), len(corrected_words)) > 30000

    matcher = difflib.SequenceMatcher(
        None,
        source_words,
        corrected_words,
        autojunk=use_autojunk,
    )

    similarity = matcher.ratio()

    points_by_source = {}

    for match in matcher.get_matching_blocks():
        if match.size == 0:
            continue

        start_source = match.a
        start_corrected = match.b
        end_source = match.a + match.size
        end_corrected = match.b + match.size

        # Internal anchors. Endpoints are forced separately so all corrected
        # text, including insertions before/after matching material, is kept.
        if 0 < start_source < len(source_words):
            points_by_source.setdefault(start_source, []).append(float(start_corrected))
        if 0 < end_source < len(source_words):
            points_by_source.setdefault(end_source, []).append(float(end_corrected))

    anchors: List[Tuple[int, float]] = [(0, 0.0)]

    for source_pos in sorted(points_by_source):
        corrected_positions = points_by_source[source_pos]
        # If an insertion occurs exactly between two matching regions, averaging
        # the two corrected positions splits that inserted material near the
        # surrounding timestamp boundary rather than dropping it.
        corrected_pos = sum(corrected_positions) / len(corrected_positions)
        anchors.append((source_pos, corrected_pos))

    anchors.append((len(source_words), float(len(corrected_words))))
    return anchors, similarity


def map_source_boundary(
    source_boundary: int,
    anchors: List[Tuple[int, float]],
    corrected_word_count: int,
) -> int:
    """Map a source-word boundary to a corrected-word boundary by interpolation."""
    if source_boundary <= anchors[0][0]:
        return 0
    if source_boundary >= anchors[-1][0]:
        return corrected_word_count

    for (x1, y1), (x2, y2) in zip(anchors, anchors[1:]):
        if x1 <= source_boundary <= x2:
            if x2 == x1:
                mapped = y2
            else:
                fraction = (source_boundary - x1) / (x2 - x1)
                mapped = y1 + fraction * (y2 - y1)

            return max(0, min(corrected_word_count, int(round(mapped))))

    return corrected_word_count


def corrected_word_boundary_to_raw_token_boundary(
    corrected_word_boundary: int,
    corrected_raw_tokens: List[str],
    corrected_word_raw_indexes: List[int],
) -> int:
    """
    Convert a corrected lexical-word boundary into a raw-token boundary so
    punctuation and original token spelling from the corrected TXT are retained.
    """
    if corrected_word_boundary <= 0:
        return 0
    if corrected_word_boundary >= len(corrected_word_raw_indexes):
        return len(corrected_raw_tokens)

    return corrected_word_raw_indexes[corrected_word_boundary]


def align_corrected_text_to_srt(
    corrected_text: str,
    blocks: List[SRTBlock],
) -> Tuple[List[str], float, int, int]:
    """
    Return corrected subtitle text for each SRT block.

    No original SRT subtitle wording is returned. It is used only as the
    comparison sequence that guides where corrected TXT words should be split.
    """
    source_words, source_boundaries = build_source_words(blocks)
    corrected_raw_tokens, corrected_words, corrected_word_raw_indexes = lexical_units(
        corrected_text
    )

    if not source_words:
        raise ValueError("SRT_HAS_NO_ALIGNMENT_TEXT")
    if not corrected_words:
        raise ValueError("TXT_HAS_NO_TEXT")

    anchors, similarity = build_anchor_points(source_words, corrected_words)

    corrected_boundaries = [
        map_source_boundary(boundary, anchors, len(corrected_words))
        for boundary in source_boundaries
    ]

    # Enforce a monotonic sequence after rounding/interpolation.
    corrected_boundaries[0] = 0
    corrected_boundaries[-1] = len(corrected_words)

    for i in range(1, len(corrected_boundaries)):
        corrected_boundaries[i] = max(
            corrected_boundaries[i],
            corrected_boundaries[i - 1],
        )

    for i in range(len(corrected_boundaries) - 2, -1, -1):
        corrected_boundaries[i] = min(
            corrected_boundaries[i],
            corrected_boundaries[i + 1],
        )

    raw_boundaries = [
        corrected_word_boundary_to_raw_token_boundary(
            boundary,
            corrected_raw_tokens,
            corrected_word_raw_indexes,
        )
        for boundary in corrected_boundaries
    ]

    output_segments: List[str] = []

    for start_raw, end_raw in zip(raw_boundaries, raw_boundaries[1:]):
        segment_tokens = corrected_raw_tokens[start_raw:end_raw]
        output_segments.append(" ".join(segment_tokens).strip())

    return output_segments, similarity, len(source_words), len(corrected_words)


# -----------------------------
# SRT generation
# -----------------------------
def generate_srt(blocks: List[SRTBlock], corrected_segments: List[str]) -> str:
    """
    Create the final SRT from:
      - sequence identifiers from the uploaded SRT
      - timestamp lines from the uploaded SRT
      - subtitle text exclusively from the corrected TXT
    """
    output_blocks: List[str] = []

    for block, corrected_text in zip(blocks, corrected_segments):
        output_blocks.append(
            f"{block.sequence}\n{block.timestamp}\n{corrected_text}".rstrip()
        )

    return "\n\n".join(output_blocks) + "\n"


def output_filename(original_txt_name: str, suffix: str) -> str:
    stem = re.sub(r"\.[^.]+$", "", original_txt_name)
    return f"{stem}{suffix}"


# -----------------------------
# User interface
# -----------------------------
with st.sidebar:
    language = st.selectbox(
        "Language / Idioma",
        options=["English", "Español", "Português"],
        index=0,
    )

t = TRANSLATIONS[language]

st.title(t["app_title"])
st.write(t["app_description"])
st.info(t["privacy_note"])

col1, col2 = st.columns(2)

with col1:
    txt_file = st.file_uploader(
        t["txt_upload"],
        type=["txt"],
        help=t["txt_help"],
        key="corrected_txt",
    )

with col2:
    srt_file = st.file_uploader(
        t["srt_upload"],
        type=["srt"],
        help=t["srt_help"],
        key="uncorrected_srt",
    )

if st.button(t["process"], type="primary", use_container_width=True):
    if txt_file is None or srt_file is None:
        st.warning(t["missing_files"])
    else:
        try:
            with st.spinner(t["processing"]):
                corrected_text = decode_uploaded_file(txt_file.getvalue())
                original_srt_text = decode_uploaded_file(srt_file.getvalue())

                blocks = parse_srt(original_srt_text)

                if not blocks:
                    raise ValueError("NO_VALID_SRT_BLOCKS")

                corrected_segments, similarity, source_word_count, corrected_word_count = (
                    align_corrected_text_to_srt(corrected_text, blocks)
                )

                final_srt = generate_srt(blocks, corrected_segments)
                empty_block_count = sum(not segment for segment in corrected_segments)

                # Save results in session state so changing nothing else does not
                # require reprocessing before download.
                st.session_state["final_srt"] = final_srt
                st.session_state["output_name"] = output_filename(
                    txt_file.name,
                    t["filename_suffix"],
                )
                st.session_state["preview_rows"] = [
                    {
                        t["sequence"]: block.sequence,
                        t["timestamp"]: block.timestamp,
                        t["corrected_text"]: segment,
                    }
                    for block, segment in zip(blocks[:20], corrected_segments[:20])
                ]
                st.session_state["stats"] = {
                    "similarity": similarity,
                    "blocks": len(blocks),
                    "source_words": source_word_count,
                    "corrected_words": corrected_word_count,
                    "output_words": sum(len(segment.split()) for segment in corrected_segments),
                    "empty_blocks": empty_block_count,
                }

            st.success(t["success"])

        except ValueError as exc:
            st.error(t["error_title"])
            if str(exc) == "NO_VALID_SRT_BLOCKS":
                st.write(t["no_srt_blocks"])
            elif str(exc) == "TXT_HAS_NO_TEXT":
                st.write(t["empty_txt"])
            elif str(exc) == "SRT_HAS_NO_ALIGNMENT_TEXT":
                st.write(t["empty_srt_text"])
            else:
                st.exception(exc)

        except Exception as exc:
            st.error(t["error_title"])
            st.exception(exc)


# -----------------------------
# Results area
# -----------------------------
if "final_srt" in st.session_state and "stats" in st.session_state:
    stats = st.session_state["stats"]
    similarity_percent = stats["similarity"] * 100

    st.subheader(t["alignment"])
    st.progress(min(max(stats["similarity"], 0.0), 1.0))
    st.write(f"**{similarity_percent:.1f}%**")
    st.caption(t["alignment_help"])

    if similarity_percent < 50:
        st.warning(t["low_alignment"])

    st.subheader(t["stats"])
    metric_cols = st.columns(5)
    metric_cols[0].metric(t["srt_blocks"], stats["blocks"])
    metric_cols[1].metric(t["source_words"], stats["source_words"])
    metric_cols[2].metric(t["corrected_words"], stats["corrected_words"])
    metric_cols[3].metric(t["output_words"], stats["output_words"])
    metric_cols[4].metric(t["empty_blocks"], stats["empty_blocks"])

    st.subheader(t["preview"])
    st.dataframe(
        st.session_state["preview_rows"],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label=t["download"],
        data=st.session_state["final_srt"].encode("utf-8-sig"),
        file_name=st.session_state["output_name"],
        mime="application/x-subrip",
        use_container_width=True,
    )
