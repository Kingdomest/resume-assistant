from io import BytesIO

import pytest
from docx import Document
from pypdf import PdfWriter

from backend.react_resume.parsers import UnsupportedFileTypeError, parse_resume_file


def build_docx_bytes(text: str) -> bytes:
    document = Document()
    document.add_paragraph(text)
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


def build_empty_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    stream = BytesIO()
    writer.write(stream)
    return stream.getvalue()


def test_parse_docx_extracts_paragraph_text():
    content = build_docx_bytes("负责 Java 后端系统，使用 Redis 和 MySQL。")

    parsed = parse_resume_file("resume.docx", content)

    assert parsed.file_name == "resume.docx"
    assert parsed.file_type == "docx"
    assert "Java 后端系统" in parsed.raw_text


def test_parse_file_rejects_legacy_doc():
    with pytest.raises(UnsupportedFileTypeError) as error:
        parse_resume_file("resume.doc", b"legacy")

    assert "暂不支持 .doc" in str(error.value)


def test_parse_file_rejects_unknown_extension():
    with pytest.raises(UnsupportedFileTypeError) as error:
        parse_resume_file("resume.txt", b"text")

    assert "仅支持 PDF 和 DOCX" in str(error.value)


def test_parse_file_rejects_empty_text_docx():
    content = build_docx_bytes("")

    with pytest.raises(ValueError) as error:
        parse_resume_file("resume.docx", content)

    assert "没有提取到有效文本" in str(error.value)


def test_parse_pdf_rejects_empty_text_pdf():
    with pytest.raises(ValueError) as error:
        parse_resume_file("resume.pdf", build_empty_pdf_bytes())

    assert "PDF 没有提取到有效文本" in str(error.value)
