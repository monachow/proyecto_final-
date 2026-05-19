# Guía de Interfaces Gráficas con Streamlit
## Lógica Computacional · Ingeniería de Datos e Inteligencia Artificial
### Unidad 4 — Aplicación al Proyecto Final

---

> **¿Para qué sirve este documento?**
> Cubre todo lo relacionado con la construcción de la interfaz gráfica usando Streamlit: configuración de la app, widgets, layout, navegación por tabs, métricas, gráficos y exportación. El código de lógica de negocio (cálculos, lectura de archivos, integración) está en el documento complementario.

---

## Prerrequisitos

```bash
pip install streamlit pandas openpyxl plotly
```

Verificar instalación:
```bash
streamlit hello
```

Ejecutar la aplicación del proyecto:
```bash
streamlit run app.py
```

Estructura de archivos relacionados con la interfaz:
```
proyecto_final/
├── app.py          # ← Todo lo de esta guía vive aquí
└── utils/
    └── ...         # Módulos de lógica (ver guía de lógica de negocio)
```

---

## ¿Qué es Streamlit y cómo funciona?

Streamlit es una librería de Python que permite crear aplicaciones web interactivas **sin escribir HTML ni JavaScript**. Cada vez que el usuario interactúa con un elemento (sube un archivo, selecciona un filtro, hace clic en un botón), el script completo se vuelve a ejecutar de arriba a abajo.

**Flujo de ejecución:**
```
Usuario interactúa → Streamlit re-ejecuta app.py → Actualiza la pantalla
```

Esto significa que el orden en que escribes el código define el orden visual de la pantalla. Lo que esté primero en el script aparece primero en la app.

---

## Parte 1 — Configuración y estructura base

### Configuración de la página

Siempre debe ser la **primera línea** del script, antes de cualquier otro elemento de Streamlit:

```python
import streamlit as st
import pandas as pd

# ── Configuración de la página ──────────────────────────────────────
st.set_page_config(
    page_title="Panel Académico IDIA",   # Título en la pestaña del navegador
    page_icon="🎓",                       # Ícono de la pestaña
    layout="wide"                         # "wide" aprovecha todo el ancho
)
```

### Encabezado principal

```python
# ── Encabezado ───────────────────────────────────────────────────────
st.title("🎓 Panel de Análisis Académico")
st.markdown("**Ingeniería de Datos e Inteligencia Artificial · Lógica Computacional**")
st.divider()   # Línea separadora horizontal
```

### Sidebar (panel lateral)

El sidebar agrupa los controles de configuración y carga, dejando el área principal para los resultados:

```python
# ── Sidebar ──────────────────────────────────────────────────────────
st.sidebar.title("📂 Carga de archivos")
st.sidebar.info("Sube los 4 archivos del sistema académico para comenzar el análisis.")

# Cualquier widget con st.sidebar.xxx aparece en el panel lateral
```

### Tabla de widgets básicos

| Función Streamlit              | ¿Qué hace?                                        |
|-------------------------------|---------------------------------------------------|
| `st.title("texto")`           | Título grande (H1)                                |
| `st.header("texto")`          | Subtítulo (H2)                                    |
| `st.subheader("texto")`       | Subtítulo menor (H3)                              |
| `st.markdown("texto")`        | Texto con formato Markdown                        |
| `st.write(valor)`             | Muestra texto, DataFrames, gráficos, listas       |
| `st.divider()`                | Línea separadora horizontal                       |
| `st.dataframe(df)`            | Tabla interactiva (ordenable, buscable)           |
| `st.metric("label", valor)`   | Tarjeta numérica con etiqueta                     |
| `st.success("msg")`           | Mensaje verde de éxito                            |
| `st.warning("msg")`           | Mensaje amarillo de advertencia                   |
| `st.error("msg")`             | Mensaje rojo de error                             |
| `st.info("msg")`              | Mensaje azul informativo                          |
| `st.expander("título")`       | Sección plegable/expandible                       |

---

## Parte 2 — Carga de archivos con st.file_uploader

`st.file_uploader` muestra un botón para que el usuario suba un archivo desde su computador. El archivo queda disponible como un objeto en memoria (no se guarda en disco).

### Patrón general de carga

```python
archivo = st.sidebar.file_uploader(
    "Etiqueta visible para el usuario",
    type=["xlsx"]          # Extensiones permitidas
)

if archivo is not None:
    # El usuario ya subió el archivo — procesar aquí
    st.sidebar.success("✅ Archivo recibido")
```

### Carga del Excel de estudiantes

```python
archivo_excel = st.sidebar.file_uploader(
    "1️⃣ Datos de estudiantes (Excel)",
    type=["xlsx", "xls"]
)

if archivo_excel is not None:
    try:
        df_estudiantes = cargar_estudiantes(archivo_excel)   # Función de lógica
        st.sidebar.success(f"✅ {len(df_estudiantes)} estudiantes cargados")
        st.session_state["df_estudiantes"] = df_estudiantes

        with st.expander("👥 Vista previa — Estudiantes"):
            st.dataframe(df_estudiantes, use_container_width=True)

    except ValueError as e:
        st.sidebar.error(f"❌ Error: {e}")
```

### Carga del CSV de asignaturas

```python
archivo_csv = st.sidebar.file_uploader(
    "2️⃣ Espacios académicos (CSV)",
    type=["csv"]
)

if archivo_csv is not None:
    try:
        df_asignaturas = cargar_asignaturas(archivo_csv)     # Función de lógica
        st.sidebar.success(f"✅ {len(df_asignaturas)} asignaturas cargadas")
        st.session_state["df_asignaturas"] = df_asignaturas

        with st.expander("📚 Vista previa — Asignaturas"):
            st.dataframe(df_asignaturas, use_container_width=True)

    except ValueError as e:
        st.sidebar.error(f"❌ Error: {e}")
```

### Carga del JSON de notas y PRN de asistencias

```python
archivo_json = st.sidebar.file_uploader("3️⃣ Notas (JSON)", type=["json"])
archivo_prn  = st.sidebar.file_uploader("4️⃣ Asistencias (PRN)", type=["prn", "txt"])

if archivo_json is not None:
    try:
        df_notas = cargar_notas(archivo_json)
        st.sidebar.success(f"✅ {len(df_notas)} registros de notas")
        st.session_state["df_notas"] = df_notas
    except ValueError as e:
        st.sidebar.error(f"❌ Error en notas: {e}")

if archivo_prn is not None:
    try:
        df_asistencias = cargar_asistencias(archivo_prn)
        st.sidebar.success(f"✅ {len(df_asistencias)} registros de asistencia")
        st.session_state["df_asistencias"] = df_asistencias
    except ValueError as e:
        st.sidebar.error(f"❌ Error en asistencias: {e}")
```

### Patrón robusto con función de envolvente

Para no repetir el bloque try/except en cada carga, se puede encapsular:

```python
def intentar_carga(funcion_carga, archivo, nombre_archivo):
    """
    Envuelve la carga de un archivo con manejo de errores.
    Retorna el DataFrame o None si hay error.
    """
    try:
        df = funcion_carga(archivo)
        return df
    except ValueError as e:
        st.sidebar.error(f"❌ {nombre_archivo}: {e}")
        return None
    except Exception as e:
        st.sidebar.error(f"❌ Error inesperado en {nombre_archivo}: {type(e).__name__}")
        return None

# Uso simplificado:
if archivo_excel is not None:
    df = intentar_carga(cargar_estudiantes, archivo_excel, "Estudiantes")
    if df is not None:
        st.session_state["df_estudiantes"] = df
        st.sidebar.success(f"✅ {len(df)} estudiantes")
```

---

## Parte 3 — session_state: persistencia entre interacciones

**¿Por qué es necesario?** Streamlit re-ejecuta el script completo en cada interacción. Si el usuario sube el archivo Excel y luego selecciona un filtro, el script vuelve a correr desde cero y el DataFrame desaparece... a menos que se guarde en `st.session_state`.

`st.session_state` es un diccionario especial que sobrevive a las re-ejecuciones del script dentro de la misma sesión del usuario.

```python
# Guardar un valor en session_state
st.session_state["df_estudiantes"] = df_estudiantes

# Leer un valor de session_state
if "df_estudiantes" in st.session_state:
    df = st.session_state["df_estudiantes"]

# Verificar si todos los datos están listos
todos_listos = all([
    "df_estudiantes" in st.session_state,
    "df_asignaturas" in st.session_state,
    "df_notas"       in st.session_state,
    "df_asistencias" in st.session_state
])

if todos_listos:
    st.success("✅ Los 4 archivos están cargados. Puedes ver el análisis.")
else:
    st.info("ℹ️ Carga los 4 archivos en el panel lateral para comenzar.")
```

---

## Parte 4 — Layout: columnas, tabs y expanders

### Columnas

Permiten organizar elementos lado a lado horizontalmente:

```python
# Dos columnas de igual ancho
col1, col2 = st.columns(2)
col1.write("Contenido izquierda")
col2.write("Contenido derecha")

# Tres columnas con proporciones personalizadas
col1, col2, col3 = st.columns([1, 2, 1])   # La del medio es el doble

# Mostrar métricas en columnas
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Estudiantes",         25)
col2.metric("📚 Asignaturas",          6)
col3.metric("📈 Promedio global",    "3.87")
col4.metric("✅ Asistencia promedio", "82.3%")
```

### Tabs (pestañas de navegación)

Organizan secciones grandes en pestañas sin recargar la página:

```python
tab1, tab2, tab3 = st.tabs([
    "📊 Resumen general",
    "🔍 Búsqueda por estudiante",
    "📚 Por asignatura"
])

with tab1:
    st.write("Contenido del resumen general...")

with tab2:
    st.write("Contenido de búsqueda por estudiante...")

with tab3:
    st.write("Contenido por asignatura...")
```

### Expanders (secciones plegables)

Útiles para vistas previas y contenido secundario que no necesita estar siempre visible:

```python
with st.expander("👥 Ver datos completos de estudiantes"):
    st.dataframe(df_estudiantes, use_container_width=True)

# Expander abierto por defecto
with st.expander("📋 Instrucciones de uso", expanded=True):
    st.markdown("1. Sube los 4 archivos en el panel lateral.")
    st.markdown("2. Navega por las pestañas para ver el análisis.")
```

---

## Parte 5 — Métricas y tablas

### st.metric — tarjetas de indicadores

```python
# Básico
st.metric("Promedio general", "3.87")

# Con delta (comparación con un valor anterior)
st.metric("Promedio general", "3.87", delta="+0.12 vs semestre anterior")

# Delta negativo (aparece en rojo automáticamente)
st.metric("% Asistencia", "71.2%", delta="-3.8%")
```

### st.dataframe — tablas interactivas

```python
# Tabla básica interactiva
st.dataframe(df, use_container_width=True)

# Tabla sin índice de fila
st.dataframe(df, use_container_width=True, hide_index=True)

# Tabla con altura fija (scroll interno)
st.dataframe(df, use_container_width=True, height=300)
```

---

## Parte 6 — Filtros interactivos

### selectbox — lista desplegable de una opción

```python
opciones = df["nombre_asignatura"].dropna().unique().tolist()

asignatura_sel = st.selectbox(
    "Selecciona una asignatura:",
    options=sorted(opciones)
)

# Filtrar el DataFrame con la selección
datos_filtrados = df[df["nombre_asignatura"] == asignatura_sel]
```

### Selector de estudiante con nombre y documento

```python
opciones_est = df[["num_documento", "nombre_completo"]].drop_duplicates()
opciones_est["etiqueta"] = (
    opciones_est["nombre_completo"] + " (" + opciones_est["num_documento"] + ")"
)

seleccion = st.selectbox(
    "Selecciona un estudiante:",
    options=opciones_est["etiqueta"].tolist()
)

# Extraer el número de documento de la etiqueta
doc = seleccion.split("(")[-1].replace(")", "").strip()
datos_est = df[df["num_documento"] == doc]
```

### radio — opciones excluyentes visibles

```python
nivel_riesgo = st.radio(
    "Filtrar por estado de riesgo:",
    options=["Todos", "🔴 En riesgo crítico", "🟡 En riesgo parcial", "🟢 Sin riesgo"],
    horizontal=True
)

if nivel_riesgo != "Todos":
    df_filtrado = df[df["estado_riesgo"] == nivel_riesgo]
else:
    df_filtrado = df
```

### multiselect — selección múltiple

```python
facultades = df["facultad"].dropna().unique().tolist()

seleccionadas = st.multiselect(
    "Filtrar por facultad:",
    options=facultades,
    default=facultades   # Todas seleccionadas por defecto
)

df_filtrado = df[df["facultad"].isin(seleccionadas)]
```

---

## Parte 7 — Sección de vistas completas

### Tab 1 — Resumen general

```python
def mostrar_resumen_general(df):
    st.subheader("📊 Indicadores globales del semestre")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Estudiantes",         df["num_documento"].nunique())
    col2.metric("📚 Asignaturas",         df["codigo_asignatura"].nunique())
    col3.metric("📈 Promedio global",     f"{df['promedio'].mean():.2f}")
    col4.metric("✅ Asistencia promedio", f"{df['pct_asistencia'].mean():.1f}%")

    st.divider()

    # Distribución de riesgo
    st.subheader("🚨 Distribución de riesgo académico")
    conteo = (
        df.groupby("estado_riesgo")["num_documento"]
        .nunique()
        .reset_index()
        .rename(columns={"num_documento": "Estudiantes", "estado_riesgo": "Estado"})
    )
    st.dataframe(conteo, use_container_width=True, hide_index=True)

    # Alerta de riesgo crítico
    criticos = df[df["estado_riesgo"] == "🔴 En riesgo crítico"][
        ["nombre_completo", "codigo_asignatura", "nombre_asignatura",
         "promedio", "pct_asistencia"]
    ].drop_duplicates().sort_values("promedio")

    if len(criticos) > 0:
        st.warning(f"🔴 {len(criticos)} registros en riesgo crítico")
        st.dataframe(criticos, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Ningún estudiante en riesgo crítico")
```

### Tab 2 — Vista por estudiante

```python
def mostrar_vista_estudiante(df):
    opciones = df[["num_documento", "nombre_completo"]].drop_duplicates()
    opciones["etiqueta"] = opciones["nombre_completo"] + " (" + opciones["num_documento"] + ")"

    seleccion = st.selectbox("Selecciona un estudiante:", opciones["etiqueta"].tolist())
    doc = seleccion.split("(")[-1].replace(")", "").strip()

    datos = df[df["num_documento"] == doc]
    if datos.empty:
        st.info("No se encontraron datos para este estudiante.")
        return

    fila = datos.iloc[0]
    st.subheader(f"👤 {fila['nombre_completo']}")

    col1, col2, col3 = st.columns(3)
    col1.info(f"📄 Documento: {fila['num_documento']}")
    col2.info(f"⚧ Género: {fila.get('genero', 'N/D')}")
    col3.info(f"📧 Email: {fila.get('email', 'N/D')}")

    st.divider()
    st.subheader("📚 Rendimiento por asignatura")

    tabla = datos[[
        "nombre_asignatura", "creditos", "promedio", "pct_asistencia", "estado_riesgo"
    ]].copy()
    tabla.columns = ["Asignatura", "Créditos", "Promedio", "% Asistencia", "Estado"]
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Promedio general",     f"{datos['promedio'].mean():.2f}")
    col2.metric("Asistencia promedio",  f"{datos['pct_asistencia'].mean():.1f}%")
    col3.metric("Asignaturas cursadas", len(datos))
```

### Tab 3 — Vista por asignatura

```python
def mostrar_vista_asignatura(df):
    opciones = df["nombre_asignatura"].dropna().unique().tolist()
    asignatura_sel = st.selectbox("Selecciona una asignatura:", sorted(opciones))

    datos = df[df["nombre_asignatura"] == asignatura_sel]

    if not datos.empty:
        fila = datos.iloc[0]
        col1, col2 = st.columns(2)
        col1.write(f"**Código:** {fila['codigo_asignatura']}")
        col2.write(f"**Facultad:** {fila.get('facultad', 'N/D')}")

    st.subheader(f"Estudiantes en {asignatura_sel}")
    tabla = datos[[
        "nombre_completo", "num_documento",
        "promedio", "pct_asistencia", "estado_riesgo"
    ]].copy()
    tabla.columns = ["Nombre", "Documento", "Promedio", "% Asistencia", "Estado"]
    st.dataframe(tabla.sort_values("Promedio", ascending=False),
                 use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Promedio del grupo",    f"{datos['promedio'].mean():.2f}")
    col2.metric("Asistencia del grupo",  f"{datos['pct_asistencia'].mean():.1f}%")
    col3.metric("Estudiantes",           len(datos))
```

---

## Parte 8 — Gráficos

### Gráficos nativos de Streamlit (simples y rápidos)

```python
# Barras por asignatura
promedios = (
    df.groupby("nombre_asignatura")["promedio"]
    .mean()
    .reset_index()
    .set_index("nombre_asignatura")
)
st.bar_chart(promedios)

# Línea de promedios por estudiante
promedios_est = df.groupby("num_documento")["promedio"].mean().sort_values()
st.line_chart(promedios_est)
```

### Gráficos avanzados con Plotly

```python
import plotly.express as px

# ── Mapa de dispersión: promedio vs asistencia ───────────────────────
def grafico_dispersion_riesgo(df):
    fig = px.scatter(
        df,
        x="pct_asistencia",
        y="promedio",
        color="estado_riesgo",
        hover_name="nombre_completo",
        hover_data=["nombre_asignatura", "num_documento"],
        title="Mapa de riesgo: Promedio vs Asistencia",
        labels={
            "pct_asistencia": "% Asistencia",
            "promedio":       "Promedio de notas",
            "estado_riesgo":  "Estado"
        },
        color_discrete_map={
            "🟢 Sin riesgo":         "green",
            "🟡 En riesgo parcial":  "orange",
            "🔴 En riesgo crítico":  "red"
        }
    )
    # Líneas de umbral visual
    fig.add_hline(y=3.0,  line_dash="dash", line_color="gray",
                  annotation_text="Nota mínima: 3.0")
    fig.add_vline(x=75.0, line_dash="dash", line_color="gray",
                  annotation_text="Asistencia mínima: 75%")
    return fig

# ── Barras apiladas: riesgo por asignatura ───────────────────────────
def grafico_riesgo_por_asignatura(df):
    conteo = (
        df.groupby(["nombre_asignatura", "estado_riesgo"])
        .size()
        .reset_index(name="cantidad")
    )
    fig = px.bar(
        conteo,
        x="nombre_asignatura",
        y="cantidad",
        color="estado_riesgo",
        title="Distribución de riesgo por asignatura",
        labels={"nombre_asignatura": "Asignatura", "cantidad": "Estudiantes"},
        color_discrete_map={
            "🟢 Sin riesgo":         "green",
            "🟡 En riesgo parcial":  "orange",
            "🔴 En riesgo crítico":  "red"
        },
        barmode="stack"
    )
    return fig

# ── Uso en app.py ─────────────────────────────────────────────────────
st.plotly_chart(grafico_dispersion_riesgo(df), use_container_width=True)
st.plotly_chart(grafico_riesgo_por_asignatura(df), use_container_width=True)
```

### Probador interactivo de cálculos (herramienta de depuración)

```python
with st.expander("🛠️ Probador de funciones de cálculo"):
    col1, col2 = st.columns(2)

    with col1:
        notas_txt = st.text_input("Notas separadas por coma", value="3.5, 4.0, 4.2, 3.8")
        hechas    = st.number_input("Asistencias realizadas", value=28, min_value=0)
        total     = st.number_input("Total asistencias",      value=32, min_value=1)

    with col2:
        lista  = [float(n.strip()) for n in notas_txt.split(",")]
        prom   = calcular_promedio(lista)
        pct    = calcular_porcentaje_asistencia(hechas, total)
        riesgo = clasificar_riesgo(prom, pct)

        st.metric("Promedio calculado", f"{prom:.2f} / 5.0")
        st.metric("% Asistencia",       f"{pct:.1f}%")
        st.metric("Estado de riesgo",   riesgo)
```

---

## Parte 9 — Exportación de datos

### Botón de descarga de CSV

```python
import io

def generar_reporte_csv(df):
    """Genera un CSV con las columnas clave del informe académico."""
    columnas = [
        "nombre_completo", "num_documento", "nombre_asignatura",
        "creditos", "facultad", "promedio", "pct_asistencia", "estado_riesgo"
    ]
    df_reporte = df[columnas].copy()
    df_reporte.columns = [
        "Nombre", "Documento", "Asignatura",
        "Créditos", "Facultad", "Promedio", "% Asistencia", "Estado de riesgo"
    ]
    return df_reporte.to_csv(index=False).encode("utf-8")


# En la interfaz:
if "df_final" in st.session_state:
    csv_bytes = generar_reporte_csv(st.session_state["df_final"])

    st.download_button(
        label="⬇️ Descargar reporte completo (CSV)",
        data=csv_bytes,
        file_name="reporte_academico.csv",
        mime="text/csv"
    )
```

---

## Parte 10 — Lista de verificación de calidad de la interfaz

Antes de la sustentación, verificar:

**✅ Estructura y navegación**
- [ ] La app corre con `streamlit run app.py` sin errores en consola
- [ ] El sidebar tiene los 4 cargadores de archivo
- [ ] La pantalla muestra mensaje claro si no se han cargado todos los archivos
- [ ] Las 3 tabs están presentes y funcionan

**✅ Widgets y filtros**
- [ ] El filtro por estudiante muestra nombre + documento
- [ ] El filtro por asignatura lista todas las asignaturas disponibles
- [ ] Los filtros actualizan la tabla automáticamente

**✅ Visualización**
- [ ] Las métricas globales aparecen con `st.metric`
- [ ] Hay al menos 2 gráficos Plotly renderizados
- [ ] El botón de descarga genera un CSV válido
- [ ] Los mensajes de error son claros cuando se sube un archivo incorrecto

---

## Resumen: qué va en app.py vs en utils/

| Elemento | Archivo |
|----------|---------|
| `st.set_page_config` | `app.py` |
| `st.title`, `st.tabs`, `st.columns` | `app.py` |
| `st.file_uploader`, `st.selectbox` | `app.py` |
| `st.metric`, `st.dataframe` | `app.py` |
| `st.plotly_chart`, `st.download_button` | `app.py` |
| `st.session_state` (guardar/leer) | `app.py` |
| Lectura de Excel, CSV, JSON, PRN | `utils/carga_datos.py` |
| Cálculo de promedios, asistencia, riesgo | `utils/calculos.py` |
| Integración de DataFrames | `utils/integracion.py` |

---

*Guía de Streamlit — Lógica Computacional · IDIA · Universidad Santo Tomás · Semestre I*
