"""Generate the FICTIONAL carrier firm quote (PDF) used by Stage 6.

    uv run python scripts/make_mock_quote.py

Writes wiki/raw/sloanslake/quotes/*.pdf. Run once; the PDF is a raw source and is committed.
The carrier, people and reference numbers are invented. The story it tells: the signed application
showed phishing training isn't in place and MFA on email is only partly rolled out, so the firm premium is
higher than the indication and the carrier adds conditions (two before binding, one within 60 days after).
reportlab is a dev dependency only: the pipeline reads PDFs with pypdf."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "wiki" / "raw" / "sloanslake" / "quotes"

QUOTE = {
    "file": "2026-12-03_northwind_firm_quote.pdf",
    "carrier": "Northwind Specialty",
    "color": "#1d3557",
    "tagline": "Northwind Specialty Insurance Company · Cyber & Technology Practice",
    "date": "December 3, 2026",
    "ref": "NWS-QTE-26-11982",
    "indication_ref": "NWS-IND-26-04417",
    "underwriter": "Hannah Whitcombe, Senior Cyber Underwriter",
    "agency": "Front Range Independent Insurance Group",
    "attn": "Jordan Pike, Account Manager",
    "insured": "Sage Dentistry, PLLC d/b/a Sloan's Lake Dental",
    "address": "2750 W 29th Ave, Denver, CO 80211",
    "row": ["$1,000,000", "$10,000", "$3,410", "$100,000", "Full limit"],
    "period": "January 15, 2027 to January 15, 2028 (12:01 a.m. local time)",
    "terms": [
        "Business interruption waiting period: 8 hours",
        "Policy form: NWS-CY-100 (06/25)",
        "Quote valid through January 14, 2027",
    ],
    "why": "Premium reflects the signed application dated December 1, 2026: phishing awareness training is not "
           "currently in place, and multi-factor authentication on email is partially deployed.",
    "before": [
        "Before binding: written confirmation that MFA is enforced on all email accounts",
        "Before binding: written confirmation that backups are offline or immutable and were restore-tested in the last 12 months",
    ],
    "after": [
        "Within 60 days of binding: phishing awareness training completed by all staff, with evidence provided",
    ],
}


def build(q: dict):
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14)
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#555555"))
    head = ParagraphStyle("h", parent=ss["Title"], fontSize=18, alignment=0,
                          textColor=colors.HexColor(q["color"]), spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=ss["Heading3"], fontSize=11, spaceBefore=10, spaceAfter=4)

    story = [
        Paragraph(q["carrier"].upper(), head),
        Paragraph(q["tagline"], small),
        Spacer(1, 14),
        Paragraph("<b>CYBER LIABILITY FIRM QUOTE</b>", ParagraphStyle("t", parent=body, fontSize=13)),
        Spacer(1, 6),
        Paragraph(f"Date: {q['date']}<br/>Quote reference: {q['ref']}<br/>Follows indication: {q['indication_ref']}"
                  f"<br/>To: {q['attn']}, {q['agency']}", body),
        Spacer(1, 6),
        Paragraph(f"Named insured: <b>{q['insured']}</b><br/>{q['address']}", body),
        Spacer(1, 8),
        Paragraph("Thank you for the signed application. We are pleased to offer the following firm quote, bindable "
                  "on the terms and subjectivities below.", body),
        Paragraph("Quoted option", h2),
    ]
    table = Table([["Aggregate limit", "Retention", "Annual premium", "Social engineering", "Ransomware"], q["row"]],
                  colWidths=[1.25 * inch, 1.0 * inch, 1.25 * inch, 1.35 * inch, 1.15 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(q["color"])),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [table, Spacer(1, 6), Paragraph(q["why"], body),
              Paragraph("Policy period", h2), Paragraph(q["period"], body),
              Paragraph("Terms", h2)] + [Paragraph(f"• {t}", body) for t in q["terms"]]
    story += [Paragraph("Subjectivities", h2)] + [Paragraph(f"• {c}", body) for c in q["before"] + q["after"]]
    story += [
        Spacer(1, 12),
        Paragraph("Coverage is not in force until bound in writing by the company. Premium excludes taxes and fees. "
                  "Failure to satisfy post-binding subjectivities may result in cancellation.", small),
        Spacer(1, 10),
        Paragraph(q["underwriter"], body),
        Spacer(1, 18),
        Paragraph("FICTIONAL SAMPLE generated for a prototype. Carrier, people and reference numbers are invented.", small),
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(OUT / q["file"]), pagesize=letter, title=f"{q['carrier']} firm quote {q['ref']}",
                      author=q["carrier"], leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch).build(story)
    print("wrote", OUT / q["file"])


if __name__ == "__main__":
    build(QUOTE)
