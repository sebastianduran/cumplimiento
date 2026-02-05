import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
from core.models import PostResult, ComplianceStatus


def generate_compliance_pie(posts: list[PostResult]) -> plt.Figure:
    """Grafico de torta: distribucion de cumplimiento."""
    counts = Counter(p.status.value for p in posts)
    labels = []
    sizes = []
    colors_map = {
        "cumple": "#22c55e",
        "no-cumple": "#ef4444",
        "error": "#6b7280",
        "pendiente": "#f59e0b",
    }
    label_map = {
        "cumple": "Cumple",
        "no-cumple": "No Cumple",
        "error": "Error",
        "pendiente": "Pendiente",
    }
    colors = []

    for status, count in counts.items():
        labels.append(label_map.get(status, status))
        sizes.append(count)
        colors.append(colors_map.get(status, "#999"))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
    ax.set_title("Distribucion de Cumplimiento")
    fig.tight_layout()
    return fig


def generate_error_bar_chart(posts: list[PostResult]) -> plt.Figure:
    """Grafico de barras horizontales: errores mas comunes."""
    all_errors = []
    for p in posts:
        if p.analysis:
            all_errors.extend(p.analysis.common_errors)
            all_errors.extend(p.analysis.design_errors)

    if not all_errors:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, "No se detectaron errores", ha="center", va="center", fontsize=14)
        ax.axis("off")
        return fig

    error_counts = Counter(all_errors)
    top_errors = error_counts.most_common(10)

    labels = [e[0][:50] for e in top_errors]
    values = [e[1] for e in top_errors]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.5)))
    bars = ax.barh(range(len(labels)), values, color="#ef4444", alpha=0.8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Frecuencia")
    ax.set_title("Errores Mas Comunes")
    ax.invert_yaxis()

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9)

    fig.tight_layout()
    return fig


def generate_hashtag_usage_chart(
    posts: list[PostResult], required_hashtags: list[str]
) -> plt.Figure:
    """Grafico de barras: tasa de uso de cada hashtag obligatorio."""
    if not required_hashtags:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No hay hashtags obligatorios configurados",
                ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    total_posts = len([p for p in posts if p.analysis])
    if total_posts == 0:
        total_posts = 1

    usage = {}
    for hashtag in required_hashtags:
        count = sum(
            1 for p in posts
            if p.analysis and hashtag.lower() in [h.lower() for h in p.analysis.hashtags_present]
        )
        usage[hashtag] = count

    hashtags = list(usage.keys())
    counts = list(usage.values())
    percentages = [c / total_posts * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(8, max(3, len(hashtags) * 0.5)))
    bars = ax.barh(range(len(hashtags)), percentages, color="#3b82f6", alpha=0.8)
    ax.set_yticks(range(len(hashtags)))
    ax.set_yticklabels(hashtags, fontsize=10)
    ax.set_xlabel("% de publicaciones que lo usan")
    ax.set_title("Uso de Hashtags Obligatorios")
    ax.set_xlim(0, 105)
    ax.invert_yaxis()

    for bar, pct, cnt in zip(bars, percentages, counts):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{pct:.0f}% ({cnt}/{total_posts})", va="center", fontsize=9)

    fig.tight_layout()
    return fig


def generate_platform_breakdown(posts: list[PostResult]) -> plt.Figure:
    """Grafico de barras agrupadas por plataforma."""
    platforms = {}
    for p in posts:
        plat = p.platform.value
        if plat not in platforms:
            platforms[plat] = {"cumple": 0, "no-cumple": 0, "error": 0}
        if p.status.value in platforms[plat]:
            platforms[plat][p.status.value] += 1

    if not platforms:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        ax.axis("off")
        return fig

    plat_names = list(platforms.keys())
    cumple_vals = [platforms[p]["cumple"] for p in plat_names]
    no_cumple_vals = [platforms[p]["no-cumple"] for p in plat_names]
    error_vals = [platforms[p]["error"] for p in plat_names]

    x = range(len(plat_names))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([i - width for i in x], cumple_vals, width, label="Cumple", color="#22c55e")
    ax.bar(x, no_cumple_vals, width, label="No Cumple", color="#ef4444")
    ax.bar([i + width for i in x], error_vals, width, label="Error", color="#6b7280")

    ax.set_xticks(x)
    ax.set_xticklabels([n.capitalize() for n in plat_names])
    ax.set_ylabel("Cantidad")
    ax.set_title("Cumplimiento por Plataforma")
    ax.legend()
    fig.tight_layout()
    return fig
