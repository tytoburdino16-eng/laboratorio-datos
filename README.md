# 📊 Laboratorio de datos

Mi espacio personal para buscar, analizar y visualizar datos durante la carrera de Análisis de Datos.

## Qué hay acá

| Carpeta / archivo | Para qué sirve |
|---|---|
| `notebooks/` | Análisis paso a paso (se abren en Google Colab) |
| `app/app.py` | App web en Streamlit para buscar y graficar series argentinas |
| `src/datosar.py` | Funciones reutilizables para la API de Series de Tiempo |
| `datos/` | Archivos CSV que vaya guardando |
| `requirements.txt` | Librerías que necesita el proyecto |

El **catálogo de fuentes** (dónde buscar datos) está en una planilla aparte.

## Cómo usarlo

### 1. Abrir un notebook en Google Colab
1. Entrar a https://colab.research.google.com
2. *Archivo → Abrir notebook → GitHub*, pegar `tytoburdino16-eng/laboratorio-datos` y elegir `notebooks/01_inflacion_vs_dolar.ipynb`.
3. *Entorno de ejecución → Ejecutar todas*.

### 2. Publicar la app gratis (Streamlit Community Cloud)
1. Entrar a https://share.streamlit.io con la cuenta de GitHub.
2. *Create app* → elegir el repo `laboratorio-datos`, rama `main`, archivo `app/app.py`.
3. *Deploy*. En unos minutos queda una dirección web propia para compartir.

### Correr la app en la compu (opcional)
```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Cómo sumar un análisis nuevo
1. Duplicar un notebook y renombrarlo `02_tema.ipynb`, `03_tema.ipynb`…
2. Buscar series con `buscar_series("palabras clave")` y descargarlas con `traer_series([...])`.
3. Terminar siempre con una sección de **Conclusiones** escrita con mis palabras.
4. Subirlo a `notebooks/` en GitHub.

## Fuentes
- API de Series de Tiempo de la República Argentina — https://datos.gob.ar/series
