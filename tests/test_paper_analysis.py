from pathlib import Path

from paper_agent.paper_analysis import PaperAnalyzer, PaperReader
from paper_agent.schemas import PaperAnalysisResult, PaperInput


def write_minimal_pdf(path: Path, text: str) -> None:
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 24 Tf 72 720 Td ({escaped}) Tj ET".encode("ascii")
    objects.append(
        b"5 0 obj\n<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"\nendstream\nendobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(pdf))


def test_reader_extracts_text_from_pdf(tmp_path: Path) -> None:
    paper = tmp_path / "paper.pdf"
    write_minimal_pdf(paper, "PDF Method with accuracy evaluation")

    result = PaperReader().read(paper)

    assert "PDF Method" in result.text
    assert "accuracy evaluation" in result.text


class FakeLLMClient:
    def analyze(self, paper: PaperInput) -> PaperAnalysisResult:
        return PaperAnalysisResult(
            title="LLM Parsed Paper",
            summary=f"LLM saw {paper.path.name}",
            key_contributions=["LLM contribution"],
            implementation_targets=["LLM target"],
            required_input_data=["LLM input"],
            required_output_format=["LLM output"],
            required_models_or_libraries=["LLM library"],
            evaluation_methods=["LLM evaluation"],
            equations_or_pseudocode=["LLM equation"],
            unspecified_parts=["LLM gap"],
            mvp_scope=["LLM MVP scope"],
            excluded_scope=["LLM excluded scope"],
        )


def test_analyzer_uses_configured_llm_client(tmp_path: Path) -> None:
    paper = PaperInput(path=tmp_path / "paper.md", text="# Local Title")

    result = PaperAnalyzer(llm_client=FakeLLMClient()).analyze(paper)

    assert result.title == "LLM Parsed Paper"
    assert result.implementation_targets == ["LLM target"]
