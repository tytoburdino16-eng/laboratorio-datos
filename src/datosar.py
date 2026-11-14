"""
datosar.py — Funciones para buscar y descargar series de la
API de Series de Tiempo de Argentina (apis.datos.gob.ar/series).

Uso rápido:
    from datosar import buscar_series, traer_series
    buscar_series("tipo de cambio")
    df = traer_series(["168.1_T_CAMBIOR_D_0_0_26"], frecuencia="month")
"""

import io
import requests
import pandas as pd

BASE = "https://apis.datos.gob.ar/series/api"


def buscar_series(texto: str, limite: int = 20) -> pd.DataFrame:
    """Busca series por palabras clave y devuelve una tabla con id, descripción y datos útiles."""
    r = requests.get(f"{BASE}/search/", params={"q": texto, "limit": limite}, timeout=30)
    r.raise_for_status()
    filas = []
    for item in r.json().get("data", []):
        campo = item.get("field", {})
        dataset = item.get("dataset", {})
        filas.append({
            "id": campo.get("id"),
            "descripcion": campo.get("description"),
            "unidades": campo.get("units"),
            "frecuencia": campo.get("frequency"),
            "desde": campo.get("time_index_start"),
            "hasta": campo.get("time_index_end"),
            "dataset": dataset.get("title"),
            "fuente": dataset.get("source"),
        })
    return pd.DataFrame(filas)


def traer_series(ids, frecuencia: str | None = None, agregacion: str = "avg",
                 modo: str | None = None, desde: str | None = None) -> pd.DataFrame:
    """
    Descarga una o más series y las devuelve en un DataFrame con la fecha como índice.

    frecuencia: None (original), "month", "quarter" o "year"
    agregacion: cómo agrupar al cambiar la frecuencia ("avg", "sum", "end_of_period", ...)
    modo:       None (valores), "percent_change" (var. % vs. período anterior)
                o "percent_change_a_year_ago" (var. % interanual)
    desde:      fecha inicial, ej. "2017-01-01"
    """
    if isinstance(ids, str):
        ids = [ids]
    params = {"ids": ",".join(ids), "format": "csv", "limit": 5000}
    if frecuencia:
        params["collapse"] = frecuencia
        params["collapse_aggregation"] = agregacion
    if modo:
        params["representation_mode"] = modo
    if desde:
        params["start_date"] = desde
    r = requests.get(f"{BASE}/series/", params=params, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"])
    return df.set_index("indice_tiempo")


# Series de ejemplo (si alguna dejara de actualizarse, buscá su reemplazo con buscar_series)
IPC_NACIONAL = "148.3_INIVELNAL_DICI_M_26"       # IPC nivel general, total nacional
DOLAR_BNA = "168.1_T_CAMBIOR_D_0_0_26"           # Tipo de cambio BNA, vendedor, diario
