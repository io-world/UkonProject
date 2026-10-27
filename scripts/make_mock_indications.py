"""Generate the FICTIONAL carrier indication letters (PDF) used by the demo.

    uv run python scripts/make_mock_indications.py

Writes wiki/raw/sloanslake/indications/*.pdf. Run once; the PDFs are raw sources and are
committed. Carriers, people and reference numbers are invented; premiums are calibrated to
published SMB cyber benchmarks (wiki/raw/benchmarks/cyber_premium_benchmarks.md).
reportlab is a dev dependency only: the pipeline reads PDFs with pypdf."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "wiki" / "raw" / "sloanslake" / "indications"

AGENCY = "Front Range Independent Insurance Group"
ATTN = "Jordan Pike, Account Manager"
INSURED = "Sage Dentistry, PLLC d/b/a Sloan's Lake Dental"
ADDRESS = "2750 W 29th Ave, Denver, CO 80211"

LETTERS = [
    {
        "file": "2026-10-27_northwind_indication.pdf",
        "carrier": "Northwind Specialty",
        "color": "#1d3557",
        "tagline": "Northwind Specialty Insurance Company · Cyber & Technology Practice",
        "date": "October 27, 2026",
        "ref": "NWS-IND-26-04417",
        "underwriter": "Hannah Whitcombe, Senior Cyber Underwriter",
        "intro": "Thank you for your submission. Based on the information provided, we are pleased to offer the "
                 "following non-binding indication.",
        "basis": "Annual revenue $2,350,000 · NAICS 621210 · sloanslakedental.com · Colorado",
        "rows": [
            ["$1,000,000", "$10,000", "$2,980", "$100,000", "Full limit"],
            ["$2,000,000", "$25,000", "$4,720", "$250,000", "Full limit"],
        ],
        "terms": [
            "Business interruption waiting period: 8 hours",
            "Policy form: NWS-CY-100 (06/25)",
            "Indication valid through December 11, 2026",
        ],
        "conditions": [
            "Multi-factor authentication (MFA) required on email and remote access",
            "Offline or immutable backups",
        ],
    },
    {
        "file": "2026-10-30_ridgeline_indication.pdf",
        "carrier": "Ridgeline Mutual",
        "color": "#6a4c93",
        "tagline": "Ridgeline Mutual Insurance · Small Commercial Cyber",
        "date": "October 30, 2026",
        "ref": "RM-Q-118204",
        "underwriter": "Dale Kirkpatrick, Underwriter",
        "intro": "Following our call on October 28, please find our written indication below.",
        "basis": "Annual revenue $2,350,000 · NAICS 621210 · sloanslakedental.com · Colorado",
        "rows": [
            ["$1,000,000", "$10,000", "$2,590", "$100,000", "$500,000"],
            ["$2,000,000", "$25,000", "Declined", "—", "—"],
        ],
        "decline": "$2,000,000 option declined: Ridgeline does not offer limits above $1,000,000 for dental "
                   "offices with fewer than 20 employees.",
        "terms": [
            "Business interruption waiting period: 10 hours",
            "Policy form: RM-CYB-4 (01/26)",
            "Indication valid through December 14, 2026",
        ],
        "conditions": [
            "MFA required on email",
            "Endpoint detection and response (EDR) on all devices",
        ],
    },
    {
        "file": "2026-11-06_northwind_indication_revised.pdf",
        "carrier": "Northwind Specialty",
        "color": "#1d3557",
        "tagline": "Northwind Specialty Insurance Company · Cyber & Technology Practice",
        "date": "November 6, 2026",
        "ref": "NWS-IND-26-04417-R1",
        "underwriter": "Hannah Whitcombe, Senior Cyber Underwriter",
        "intro": "REVISED INDICATION. This letter supersedes our indication dated October 27, 2026 "
                 "(NWS-IND-26-04417). Reason: updated healthcare underwriting guidelines effective "
                 "November 1, 2026.",
        "basis": "Annual revenue $2,350,000 · NAICS 621210 · sloanslakedental.com · Colorado",
        "rows": [
            ["$1,000,000", "$10,000", "$3,280", "$100,000", "Full limit"],
            ["$2,000,000", "$25,000", "$5,190", "$250,000", "Full limit"],
        ],
        "terms": [
            "Business interruption waiting period: 8 hours",
            "Policy form: NWS-CY-100 (06/25)",
            "Indication valid through December 21, 2026",
        ],
        "conditions": [
            "Multi-factor authentication (MFA) required on email and remote access",
            "Offline or immutable backups",
            "Endpoint detection and response (EDR) on all endpoints",
        ],
    },
]


def build(spec: dict):
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14)
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#555555"))
    head = ParagraphStyle("h", parent=ss["Title"], fontSize=18, alignment=0,
                          textColor=colors.HexColor(spec["color"]), spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=ss["Heading3"], fontSize=11, spaceBefore=10, spaceAfter=4)

    story = [
        Paragraph(spec["carrier"].upper(), head),
        Paragraph(spec["tagline"], small),
        Spacer(1, 14),
        Paragraph("<b>CYBER LIABILITY INDICATION</b>", ParagraphStyle("t", parent=body, fontSize=13)),
        Spacer(1, 6),
        Paragraph(f"Date: {spec['date']}<br/>Reference: {spec['ref']}<br/>To: {ATTN}, {AGENCY}", body),
        Spacer(1, 6),
        Paragraph(f"Insured: <b>{INSURED}</b><br/>{ADDRESS}", body),
        Spacer(1, 8),
        Paragraph(spec["intro"], body),
        Paragraph("Rating basis", h2),
        Paragraph(spec["basis"], body),
        Paragraph("Indicated options", h2),
    ]
    table = Table([["Aggregate limit", "Retention", "Annual premium", "Social engineering", "Ransomware"]]
                  + spec["rows"], colWidths=[1.25 * inch, 1.0 * inch, 1.25 * inch, 1.35 * inch, 1.15 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(spec["color"])),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f4")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    if spec.get("decline"):
        story += [Spacer(1, 6), Paragraph(spec["decline"], body)]
    story += [Paragraph("Terms", h2)] + [Paragraph(f"• {t}", body) for t in spec["terms"]]
    story += [Paragraph("Subjectivities (must be met to bind)", h2)] + \
             [Paragraph(f"• {c}", body) for c in spec["conditions"]]
    story += [
        Spacer(1, 12),
        Paragraph("This is a non-binding indication, not a quote or a binder. Final terms are subject to a completed, "
                  "signed application and underwriting review. Premium excludes taxes and fees.", small),
        Spacer(1, 10),
        Paragraph(spec["underwriter"], body),
        Spacer(1, 18),
        Paragraph("FICTIONAL SAMPLE generated for a prototype. Carrier, people, figures and reference numbers are invented; the insured is a real business used for an interview demo, and this is not a real offer.",
                  small),
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(OUT / spec["file"]), pagesize=letter, title=f"{spec['carrier']} indication {spec['ref']}",
                      author=spec["carrier"], leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch).build(story)
    print("wrote", OUT / spec["file"])


if __name__ == "__main__":
    for s in LETTERS:
        build(s)
