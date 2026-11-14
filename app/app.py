"""
Laboratorio de datos — app en Streamlit para buscar y graficar series argentinas.

Para correrla en tu compu:
    pip install -r requirements.txt
    streamlit run app/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import importlib  # noqa: E402
import datosar  # noqa: E402
importlib.reload(datosar)  # toma siempre la última versión de src/datosar.py
from datosar import buscar_series, traer_series, traer_dolares, DOLARES, IPC_NACIONAL, DOLAR_BNA  # noqa: E402

FRECUENCIAS = {"R/P1D": "diaria", "R/P1M": "mensual", "R/P3M": "trimestral",
               "R/P6M": "semestral", "R/P1Y": "anual"}

st.set_page_config(page_title="Laboratorio de datos", page_icon="📊", layout="wide")
st.title("📊 Laboratorio de datos")
st.caption("Buscá, compará y descargá series de la API de Series de Tiempo de Argentina.")


@st.cache_data(ttl=3600, show_spinner="Buscando series…")
def buscar(texto):
    return buscar_series(texto, limite=25)


@st.cache_data(ttl=3600, show_spinner="Descargando datos…")
def traer(ids, frecuencia, modo, desde):
    return traer_series(list(ids), frecuencia=frecuencia, modo=modo, desde=desde)


@st.cache_data(ttl=3600, show_spinner="Descargando cotizaciones del dólar…")
def traer_dol(casas, frecuencia, modo, desde):
    return traer_dolares(list(casas), frecuencia=frecuencia, modo=modo, desde=desde)


# ---------- Barra lateral: búsqueda ----------
with st.sidebar:
    st.header("1. Buscar")
    texto = st.text_input("Palabras clave", value="tipo de cambio")
    resultados = buscar(texto) if texto else pd.DataFrame()

    if "elegidas" not in st.session_state:
        st.session_state.elegidas = {IPC_NACIONAL: "IPC nacional", DOLAR_BNA: "Dólar BNA"}

    solo_mensuales = st.checkbox("Solo series mensuales", value=True)
    if not resultados.empty and solo_mensuales:
        resultados = resultados[resultados["frecuencia"] == "R/P1M"]

    if not resultados.empty:
        st.write(f"{len(resultados)} resultados")
        for _, fila in resultados.iterrows():
            freq = FRECUENCIAS.get(fila["frecuencia"], fila["frecuencia"])
            hasta = str(fila["hasta"] or "")[:7]
            if st.button(f"➕ {fila['descripcion']}", key=fila["id"], width="stretch",
                         help=f"ID: {fila['id']}"):
                st.session_state.elegidas[fila["id"]] = fila["descripcion"]
            st.caption(f"{fila['dataset']} · {fila['unidades']} · {freq} · hasta {hasta}")

    with st.expander("Agregar por ID"):
        nuevo_id = st.text_input("ID de la serie", placeholder="ej. 143.3_NO_PR_2004_A_21")
        if st.button("Agregar") and nuevo_id.strip():
            st.session_state.elegidas[nuevo_id.strip()] = nuevo_id.strip()

    st.header("2. Dólares")
    dolares = st.multiselect("Cotizaciones (ArgentinaDatos)", list(DOLARES.keys()),
                             format_func=DOLARES.get, placeholder="Elegí uno o más dólares")
    st.caption("Promedio de la cotización de venta en cada período.")

    st.header("3. Series elegidas")
    for sid, nombre in list(st.session_state.elegidas.items()):
        c1, c2 = st.columns([5, 1])
        c1.write(nombre)
        if c2.button("✕", key=f"quitar_{sid}"):
            del st.session_state.elegidas[sid]
            st.rerun()

# ---------- Opciones del gráfico ----------
c1, c2, c3 = st.columns(3)
frec = c1.selectbox("Frecuencia", ["month", "quarter", "year"],
                    format_func={"month": "Mensual", "quarter": "Trimestral", "year": "Anual"}.get)
modo = c2.selectbox("Mostrar", [None, "percent_change", "percent_change_a_year_ago"],
                    format_func={None: "Valores", "percent_change": "Variación % vs. período anterior",
                                 "percent_change_a_year_ago": "Variación % interanual"}.get)
desde = c3.date_input("Desde", value=pd.Timestamp("2017-01-01"))

ids = tuple(st.session_state.elegidas.keys())
if not ids and not dolares:
    st.info("Elegí al menos una serie o un dólar en la barra lateral.")
    st.stop()

partes = []
try:
    if ids:
        partes.append(traer(ids, frec, modo, str(desde)))
    if dolares:
        partes.append(traer_dol(tuple(dolares), frec, modo, str(desde)))
except Exception as e:
    st.error(f"No se pudieron traer los datos: {e}")
    st.stop()
df = pd.concat(partes, axis=1).sort_index()

df_largo = df.reset_index().melt(id_vars="indice_tiempo", var_name="serie", value_name="valor")
if modo:
    df_largo["valor"] = df_largo["valor"] * 100

normalizar = st.checkbox("Normalizar (primer valor = 100) para comparar series de distinta escala",
                         value=(modo is None and df.shape[1] > 1))
if normalizar and modo is None:
    # Base común: la primera fecha en la que todas las series tienen dato
    inicio = max(df[c].first_valid_index() for c in df.columns if df[c].notna().any())
    df_largo = df_largo[df_largo["indice_tiempo"] >= inicio]
    df_largo["valor"] = df_largo.groupby("serie")["valor"].transform(
        lambda s: s / s.dropna().iloc[0] * 100 if s.notna().any() else s)
    st.caption(f"Base 100 = {inicio:%m/%Y}, el primer período con datos para todas las series.")

fig = px.line(df_largo, x="indice_tiempo", y="valor", color="serie",
              labels={"indice_tiempo": "Fecha", "valor": "%" if modo else "Valor", "serie": "Serie"})
fig.update_layout(legend=dict(orientation="h", y=-0.2), hovermode="x unified")
st.plotly_chart(fig, width="stretch")

# ---------- Tabla y descarga ----------
with st.expander("Ver tabla de datos"):
    st.dataframe(df, width="stretch")
st.download_button("⬇️ Descargar CSV", df.to_csv().encode("utf-8"),
                   file_name="series.csv", mime="text/csv")
st.caption("Fuentes: API de Series de Tiempo de la República Argentina (apis.datos.gob.ar)"
           + (" · Cotizaciones del dólar: ArgentinaDatos (api.argentinadatos.com)." if dolares else "."))
