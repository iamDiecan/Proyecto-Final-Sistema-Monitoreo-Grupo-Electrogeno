import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from typing import List, Dict, Any

def generate_trend_plot(param_name: str, data: List[Dict[str, Any]]) -> bytes:
    """
    Genera un gráfico de línea para el parámetro solicitado y devuelve los bytes de la imagen.
    data debe ser una lista de diccionarios con 'timestamp' (str) y 'value' (float/int).
    """
    if not data:
        return b""

    # Extraer X e Y
    times = []
    values = []
    for d in data[-50:]:  # Últimos 50 puntos
        ts = d.get("timestamp", "")
        if "T" in ts:
            ts = ts.split("T")[1][:5]  # Solo HH:MM
        times.append(ts)
        values.append(d.get("value", 0.0))

    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Estilo SIGEGEN Ion
    fig.patch.set_facecolor('#070B1A')
    ax.set_facecolor('#11162C')
    ax.tick_params(colors='#8892B0')
    for spine in ax.spines.values():
        spine.set_color('#8892B0')

    # Color según parámetro
    color = '#00E5FF' # Default cyan
    if param_name.lower() in ['combustible', 'fuel']:
        color = '#B000FF'
    elif param_name.lower() in ['temperatura', 'temp']:
        color = '#FF007F'
    elif param_name.lower() in ['presion', 'oil']:
        color = '#FF6B35'

    ax.plot(times, values, color=color, linewidth=2, marker='o', markersize=4)
    ax.set_title(f"Tendencia: {param_name.capitalize()}", color='#EFF3FF', pad=15)
    ax.grid(True, color='#8892B0', alpha=0.2)
    
    # Rotar labels si hay muchos
    if len(times) > 10:
        plt.xticks(rotation=45)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    
    buf.seek(0)
    return buf.read()
