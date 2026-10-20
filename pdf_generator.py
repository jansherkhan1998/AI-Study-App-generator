"""
PDF Generation Engine for Master Study Planner.
Handles styling, document flow, and multi-page table exports.
"""

from datetime import date
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_roadmap_pdf(
    exam_name: str,
    days_left: int,
    daily_hours: int,
    prep_level: str,
    phases: list,
) -> bytes:
    """Generates a professional multi-page PDF Master Study Planner from roadmap phases."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
    )
    cell_bold_style = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
    )

    story = []

    # 1. Document Header
    story.append(Paragraph(f"🎓 Master Study Planner: {exam_name}", title_style))
    story.append(
        Paragraph(
            f"<b>Target Date Horizon:</b> {days_left} Days | "
            f"<b>Daily Budget:</b> {daily_hours} Hours/Day | "
            f"<b>Student Level:</b> {prep_level} | "
            f"<b>Generated On:</b> {date.today().strftime('%B %d, %Y')}",
            subtitle_style,
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#2563EB"),
            spaceAfter=15,
        )
    )

    # 2. Executive Guidelines
    story.append(
        Paragraph("📌 Execution Guidelines & Path to Glory", section_heading)
    )
    guidelines_text = (
        "<b>1. Daily Consistency:</b> Complete allotted subject reading and MCQ volume targets before ending each session.<br/>"
        "<b>2. Benchmark Compliance:</b> Attempt each Block's designated assessment test. Do not advance to the next block without reaching the target score.<br/>"
        "<b>3. Revision Loops:</b> Record every incorrect MCQ in an error log and review prior to full mock exams in Phase 3."
    )
    story.append(Paragraph(guidelines_text, cell_style))
    story.append(Spacer(1, 12))

    # 3. Master Timetable Construction
    story.append(
        Paragraph("📅 Master Subject-Wise Day-by-Day Schedule", section_heading)
    )

    # Table Header Row
    table_data = [[
        Paragraph("Phase / Block", header_cell_style),
        Paragraph("Days", header_cell_style),
        Paragraph("Subject-Wise Specific Topics", header_cell_style),
        Paragraph("Daily MCQ Target", header_cell_style),
        Paragraph("Hours Split", header_cell_style),
        Paragraph("Required Test Benchmark", header_cell_style),
    ]]

    for p in phases:
        phase_name = p.get("phase_name", "Phase")
        for b in p.get("blocks", []):
            block_title = b.get("block_title", "Block")
            test_target = (
                f"{b.get('block_testing_target', 'Quiz')}<br/>"
                f"<b>Target:</b> {b.get('target_pass_score', '75%')}"
            )

            for sched in b.get("daily_schedule", []):
                day_label = sched.get("day_label", "-")

                topics_str = "<br/>".join(
                    [f"• {top}" for top in sched.get("subject_topics", [])]
                )
                mcq_str = "<br/>".join(
                    [f"• {mcq}" for mcq in sched.get("daily_mcq_target", [])]
                )
                time_str = "<br/>".join([
                    f"• {act}: {hrs}"
                    for act, hrs in sched.get("daily_hours_breakdown", {}).items()
                ])

                table_data.append([
                    Paragraph(
                        f"<b>{phase_name}</b><br/>{block_title}", cell_bold_style
                    ),
                    Paragraph(day_label, cell_bold_style),
                    Paragraph(topics_str, cell_style),
                    Paragraph(mcq_str, cell_style),
                    Paragraph(time_str, cell_style),
                    Paragraph(test_target, cell_style),
                ])

    # Build Table
    col_widths = [100, 50, 180, 80, 70, 80]
    roadmap_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    roadmap_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#F8FAFC")],
            ),
        ])
    )

    story.append(roadmap_table)
    doc.build(story)
    return buffer.getvalue()
