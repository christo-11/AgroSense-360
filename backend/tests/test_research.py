import sys
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app import research


def _register_and_login(client, test_emails):
    email = f"research-{uuid4().hex}@example.com"
    test_emails.append(email)
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "research-test-password"},
    )
    assert registered.status_code == 201
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "research-test-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_document_upload_search_citations_and_delete_are_owner_scoped(client, test_emails, monkeypatch, tmp_path):
    monkeypatch.setattr(research, "document_root", lambda: tmp_path)
    owner_headers = _register_and_login(client, test_emails)
    other_headers = _register_and_login(client, test_emails)
    uploaded = client.post(
        "/api/v1/research/documents",
        headers=owner_headers,
        files={"file": ("rainfall-notes.md", b"Rainfall controls soil moisture during the growing season.", "text/markdown")},
    )

    assert uploaded.status_code == 201
    document = uploaded.json()
    assert client.get("/api/v1/research/documents", headers=owner_headers).json()["total"] == 1
    assert client.get("/api/v1/research/documents", headers=other_headers).json()["total"] == 0

    result = client.post(
        "/api/v1/research/answer",
        headers=owner_headers,
        json={"query": "rainfall soil moisture"},
    )
    assert result.status_code == 200
    assert result.json()["mode"] == "retrieved_excerpts"
    assert "soil moisture" in result.json()["answer"]
    assert result.json()["citations"][0]["filename"] == "rainfall-notes.md"
    assert "not a generated synthesis" in result.json()["warning"]

    assert client.get(
        "/api/v1/research/search",
        headers=other_headers,
        params={"q": "rainfall"},
    ).json()["total"] == 0
    assert client.delete(
        f"/api/v1/research/documents/{document['id']}",
        headers=other_headers,
    ).status_code == 404
    assert client.delete(
        f"/api/v1/research/documents/{document['id']}",
        headers=owner_headers,
    ).status_code == 204
    assert client.get(
        "/api/v1/research/search",
        headers=owner_headers,
        params={"q": "rainfall"},
    ).json()["total"] == 0


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("dataset.csv", b"a,b\n1,2\n", "415"),
        ("empty.md", b"", "422"),
        ("bad.txt", b"\xff", "422"),
    ],
)
def test_document_upload_rejects_unsupported_or_invalid_content(
    client, test_emails, monkeypatch, tmp_path, filename, content, expected_status
):
    monkeypatch.setattr(research, "document_root", lambda: tmp_path)
    headers = _register_and_login(client, test_emails)
    response = client.post(
        "/api/v1/research/documents",
        headers=headers,
        files={"file": (filename, content, "application/octet-stream")},
    )
    assert response.status_code == int(expected_status)


def test_pdf_upload_extracts_text_when_pypdf_is_available(client, test_emails, monkeypatch, tmp_path):
    pypdf = pytest.importorskip("pypdf")
    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    monkeypatch.setattr(research, "document_root", lambda: tmp_path)
    headers = _register_and_login(client, test_emails)
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 12 Tf 30 200 Td (Rainfall supports crop growth.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    pdf_buffer = __import__("io").BytesIO()
    writer.write(pdf_buffer)
    response = client.post(
        "/api/v1/research/documents",
        headers=headers,
        files={"file": ("study.pdf", pdf_buffer.getvalue(), "application/pdf")},
    )

    assert response.status_code == 201
    answer = client.post(
        "/api/v1/research/answer",
        headers=headers,
        json={"query": "crop growth rainfall"},
    )
    assert answer.status_code == 200
    assert "study.pdf, page 1" in answer.json()["answer"]


def test_optional_ocr_extracts_scanned_pdf_pages_only_when_enabled(monkeypatch):
    pytest.importorskip("pypdf")
    from pypdf import PdfWriter

    class FakeImage:
        def close(self):
            pass

    class FakeBitmap:
        def to_pil(self):
            return FakeImage()

        def close(self):
            pass

    class FakePage:
        def get_size(self):
            return 100, 100

        def render(self, scale):
            assert scale == 1.5
            return FakeBitmap()

        def close(self):
            pass

    class FakePdf:
        def __init__(self, raw):
            assert raw.startswith(b"%PDF")

        def __getitem__(self, index):
            assert index == 0
            return FakePage()

        def close(self):
            pass

    ocr_calls = []
    fake_pytesseract = SimpleNamespace(
        TesseractNotFoundError=type("TesseractNotFoundError", (Exception,), {}),
        TesseractError=type("TesseractError", (Exception,), {}),
        image_to_string=lambda image, timeout: (
            ocr_calls.append(timeout) or "Scanned pepper research"
        ),
    )
    monkeypatch.setitem(sys.modules, "pypdfium2", SimpleNamespace(PdfDocument=FakePdf))
    monkeypatch.setitem(sys.modules, "pytesseract", fake_pytesseract)

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buffer = __import__("io").BytesIO()
    writer.write(buffer)
    pages, extraction_method = research._extract(buffer.getvalue(), ".pdf", enable_ocr=True)

    assert pages == ["Scanned pepper research"]
    assert extraction_method == "text+ocr"
    assert ocr_calls == [research.OCR_PAGE_TIMEOUT_SECONDS]


def test_optional_ocr_does_not_load_dependencies_for_text_pages(monkeypatch):
    monkeypatch.setattr(research, "import_module", lambda *_: pytest.fail("OCR dependencies should not load"))

    pages, extracted_count = research._ocr_scanned_pages(b"not rendered", ["Already extracted text"])

    assert pages == ["Already extracted text"]
    assert extracted_count == 0
