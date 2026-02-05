from io import BytesIO
from fpdf import FPDF
from datetime import datetime
from core.models import PostResult, ComplianceConfig, ComplianceStatus


def generate_pdf_report(
    posts: list[PostResult],
    config: ComplianceConfig,
) -> bytes:
    """Genera un reporte PDF con resumen y detalle de cumplimiento."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Pagina de titulo ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 40, "", ln=True)
    pdf.cell(0, 15, "Reporte de Cumplimiento Social", ln=True, align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.cell(0, 10, f"Total de publicaciones: {len(posts)}", ln=True, align="C")

    # --- Resumen ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Resumen General", ln=True)
    pdf.set_font("Helvetica", "", 11)

    total = len(posts)
    cumple = sum(1 for p in posts if p.status == ComplianceStatus.CUMPLE)
    no_cumple = sum(1 for p in posts if p.status == ComplianceStatus.NO_CUMPLE)
    errores = sum(1 for p in posts if p.status == ComplianceStatus.ERROR)

    pdf.cell(0, 8, f"Publicaciones que cumplen: {cumple} ({cumple/total*100:.0f}%)" if total > 0 else "Sin datos", ln=True)
    pdf.cell(0, 8, f"Publicaciones que no cumplen: {no_cumple} ({no_cumple/total*100:.0f}%)" if total > 0 else "", ln=True)
    pdf.cell(0, 8, f"Publicaciones con error: {errores}", ln=True)
    pdf.ln(5)

    # Hashtags configurados
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Hashtags Obligatorios:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for h in config.required_hashtags:
        pdf.cell(0, 7, f"  - {h}", ln=True)
    pdf.ln(5)

    # Errores mas comunes
    from collections import Counter
    all_errors = []
    for p in posts:
        if p.analysis:
            all_errors.extend(p.analysis.common_errors)
            all_errors.extend(p.analysis.design_errors)

    if all_errors:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Errores Mas Comunes:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for error, count in Counter(all_errors).most_common(10):
            pct = count / total * 100 if total > 0 else 0
            pdf.cell(0, 7, f"  - {error[:70]} ({count} veces, {pct:.0f}%)", ln=True)
        pdf.ln(5)

    # --- Detalle por publicacion ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Detalle por Publicacion", ln=True)

    for i, post in enumerate(posts):
        if pdf.get_y() > 240:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 11)
        status_label = "CUMPLE" if post.status == ComplianceStatus.CUMPLE else "NO CUMPLE" if post.status == ComplianceStatus.NO_CUMPLE else post.status.value.upper()
        pdf.cell(0, 8, f"{i+1}. [{status_label}] {post.platform.value.capitalize()}", ln=True)

        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"URL: {post.url[:80]}", ln=True)

        if post.extracted_text:
            text_preview = post.extracted_text[:200].replace("\n", " ")
            pdf.multi_cell(0, 5, f"Texto: {text_preview}")

        if post.analysis:
            a = post.analysis
            if a.hashtags_missing:
                pdf.cell(0, 6, f"Hashtags faltantes: {', '.join(a.hashtags_missing)}", ln=True)
            pdf.cell(0, 6, f"Logo oficial: {'Si' if a.brand_identity else 'No'} | Tono: {a.tone_label} ({a.emotional_score*100:.0f}%)", ln=True)
            if a.design_errors:
                for err in a.design_errors[:3]:
                    pdf.cell(0, 5, f"  Error: {err[:70]}", ln=True)
            if a.suggested_corrections:
                for corr in a.suggested_corrections[:3]:
                    pdf.cell(0, 5, f"  Correccion: {corr[:70]}", ln=True)

        if post.error_message:
            pdf.cell(0, 6, f"Error: {post.error_message[:80]}", ln=True)

        pdf.ln(3)

    # Retornar como bytes
    output = BytesIO()
    pdf.output(output)
    return output.getvalue()
