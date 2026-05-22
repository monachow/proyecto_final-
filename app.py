<<<<<<< HEAD
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.calculos import (
    calcular_porcentaje_asistencia,
    calcular_promedio,
    calcular_todos_indicadores,
    clasificar_riesgo,
)
from utils.carga_datos import (
    cargar_asignaturas,
    cargar_asistencias,
    cargar_estudiantes,
    cargar_notas,
)
from utils.integracion import integrar_datos


# ══════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════════════

def intentar_carga(funcion_carga, archivo, nombre_archivo):
    """Ejecuta una función de carga y captura sus errores mostrándolos en el sidebar.

    Envuelve cualquier función de carga de datos para que los errores de
    validación y los errores inesperados se muestren como mensajes en el
    sidebar de Streamlit en lugar de detener la aplicación.

    Args:
        funcion_carga (callable): Función que recibe un objeto de archivo y
            retorna un DataFrame (p. ej. cargar_estudiantes).
        archivo: Objeto de archivo proveniente de st.file_uploader.
        nombre_archivo (str): Nombre descriptivo del archivo, usado en los
            mensajes de error del sidebar.

    Returns:
        pd.DataFrame: DataFrame retornado por funcion_carga si la carga fue
            exitosa, o None si ocurrió algún error.
    """
    try:
        return funcion_carga(archivo)
=======
import streamlit as st
import pandas as pd

from utils.calculos import calcular_promedio, calcular_porcentaje_asistencia, calcular_todos_indicadores, clasificar_riesgo
from utils.carga_datos import cargar_asignaturas, cargar_asistencias, cargar_estudiantes, cargar_notas
from utils.integracion import integrar_datos


# ── Configuración de la página ──────────────────────────────────────
st.set_page_config(
    page_title="Panel Académico IDIA",   # Título en la pestaña del navegador
    page_icon="🎓",                       # Ícono de la pestaña
    layout="wide"                         # "wide" aprovecha todo el ancho
)


### Encabezado principal

# ── Encabezado ───────────────────────────────────────────────────────
st.title("🎓 Panel de Análisis Académico")
st.markdown("**Ingeniería de Datos e Inteligencia Artificial · Lógica Computacional**")
st.divider()   # Línea separadora horizontal
# ── Sidebar ──────────────────────────────────────────────────────────
st.sidebar.title("📂 Carga de archivos")
st.sidebar.info("Sube los 4 archivos del sistema académico para comenzar el análisis.")

##carga archivo excel  de estudiantes
archivo = st.sidebar.file_uploader(
    "Etiqueta visible para el usuario",
    type=["xlsx"]          # Extensiones permitidas
)

if archivo is not None:
    # El usuario ya subió el archivo — procesar aquí
    st.sidebar.success("✅ Archivo recibido")

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


### Carga del CSV de asignaturas

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

### Carga del JSON de notas y PRN de asistencias

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

### Patrón robusto con función de envolvente

def intentar_carga(funcion_carga, archivo, nombre_archivo):
    """
    Envuelve la carga de un archivo con manejo de errores.
    Retorna el DataFrame o None si hay error.
    """
    try:
        df = funcion_carga(archivo)
        return df
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
    except ValueError as e:
        st.sidebar.error(f"❌ {nombre_archivo}: {e}")
        return None
    except Exception as e:
        st.sidebar.error(f"❌ Error inesperado en {nombre_archivo}: {type(e).__name__}")
        return None

<<<<<<< HEAD

# ══════════════════════════════════════════════════════════════════════
# FUNCIONES DE GRÁFICOS
# ══════════════════════════════════════════════════════════════════════

def grafico_dispersion_riesgo(df):
    """Genera un gráfico de dispersión de promedio vs porcentaje de asistencia.

    Cada punto representa un registro (estudiante × asignatura) y se colorea
    según su estado de riesgo. Se añaden líneas de referencia horizontales y
    verticales que marcan los umbrales mínimos de nota (3.0) y asistencia (75 %).

    Args:
        df (pd.DataFrame): DataFrame integrado con las columnas
            ``pct_asistencia``, ``promedio``, ``estado_riesgo``,
            ``nombre_completo``, ``nombre_asignatura`` y ``num_documento``.

    Returns:
        plotly.graph_objs.Figure: Figura de Plotly lista para renderizar con
            ``st.plotly_chart``.
    """
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
            "estado_riesgo":  "Estado",
        },
        color_discrete_map={
            "🟢 Sin riesgo":        "green",
            "🟡 En riesgo parcial": "orange",
            "🔴 En riesgo crítico": "red",
        },
    )
    fig.add_hline(y=3.0,  line_dash="dash", line_color="gray",
                  annotation_text="Nota mínima: 3.0")
    fig.add_vline(x=75.0, line_dash="dash", line_color="gray",
                  annotation_text="Asistencia mínima: 75%")
    return fig


def grafico_riesgo_por_asignatura(df):
    """Genera un gráfico de barras apiladas con la distribución de riesgo por asignatura.

    Agrupa los registros por asignatura y estado de riesgo, y muestra la
    cantidad de estudiantes en cada categoría como barras apiladas coloreadas
    por nivel de riesgo.

    Args:
        df (pd.DataFrame): DataFrame integrado con las columnas
            ``nombre_asignatura`` y ``estado_riesgo``.

    Returns:
        plotly.graph_objs.Figure: Figura de Plotly lista para renderizar con
            ``st.plotly_chart``.
    """
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
            "🟢 Sin riesgo":        "green",
            "🟡 En riesgo parcial": "orange",
            "🔴 En riesgo crítico": "red",
        },
        barmode="stack",
    )
    return fig


# ══════════════════════════════════════════════════════════════════════
# VISTAS DE CADA PESTAÑA
# ══════════════════════════════════════════════════════════════════════

def mostrar_resumen_general(df):
    """Renderiza la pestaña de resumen general del semestre.

    Muestra cuatro métricas globales (estudiantes, asignaturas, promedio y
    asistencia), la tabla de distribución de riesgo académico, la lista de
    registros en riesgo crítico, los gráficos de dispersión y barras apiladas,
    el gráfico de barras de promedio por asignatura y un expander con la tabla
    completa de datos.

    Args:
        df (pd.DataFrame): DataFrame integrado y con indicadores calculados.
            Debe contener las columnas ``num_documento``, ``codigo_asignatura``,
            ``promedio``, ``pct_asistencia``, ``estado_riesgo``,
            ``nombre_completo`` y ``nombre_asignatura``.

    Returns:
        None
    """
=======
# Uso simplificado:
if archivo_excel is not None:
    df = intentar_carga(cargar_estudiantes, archivo_excel, "Estudiantes")
    if df is not None:
        st.session_state["df_estudiantes"] = df
        st.sidebar.success(f"✅ {len(df)} estudiantes")



st.session_state["df_estudiantes"] = df_estudiantes

if "df_estudiantes" in st.session_state:
    df = st.session_state["df_estudiantes"]


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


# Dos columnas de igual ancho
col1, col2 = st.columns(2)
col1.write("Contenido izquierda")
col2.write("Contenido derecha")

col1, col2, col3 = st.columns([1, 2, 1])   # La del medio es el doble

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Estudiantes",         25)
col2.metric("📚 Asignaturas",          6)
col3.metric("📈 Promedio global",    "3.87")
col4.metric("✅ Asistencia promedio", "82.3%")

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


with st.expander("👥 Ver datos completos de estudiantes"):
    st.dataframe(df_estudiantes, use_container_width=True)


with st.expander("📋 Instrucciones de uso", expanded=True):
    st.markdown("1. Sube los 4 archivos en el panel lateral.")
    st.markdown("2. Navega por las pestañas para ver el análisis.")



st.metric("Promedio general", "3.87")

st.metric("Promedio general", "3.87", delta="+0.12 vs semestre anterior")

st.metric("% Asistencia", "71.2%", delta="-3.8%")


st.dataframe(df, use_container_width=True)

st.dataframe(df, use_container_width=True, hide_index=True)

st.dataframe(df, use_container_width=True, height=300)


opciones = df["nombre_asignatura"].dropna().unique().tolist()

asignatura_sel = st.selectbox(
    "Selecciona una asignatura:",
    options=sorted(opciones)
)

# Filtrar el DataFrame con la selección
datos_filtrados = df[df["nombre_asignatura"] == asignatura_sel]


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


nivel_riesgo = st.radio(
    "Filtrar por estado de riesgo:",
    options=["Todos", "🔴 En riesgo crítico", "🟡 En riesgo parcial", "🟢 Sin riesgo"],
    horizontal=True
)

if nivel_riesgo != "Todos":
    df_filtrado = df[df["estado_riesgo"] == nivel_riesgo]
else:
    df_filtrado = df


facultades = df["facultad"].dropna().unique().tolist()

seleccionadas = st.multiselect(
    "Filtrar por facultad:",
    options=facultades,
    default=facultades   # Todas seleccionadas por defecto
)

df_filtrado = df[df["facultad"].isin(seleccionadas)]

def mostrar_resumen_general(df):
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
    st.subheader("📊 Indicadores globales del semestre")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Estudiantes",         df["num_documento"].nunique())
    col2.metric("📚 Asignaturas",         df["codigo_asignatura"].nunique())
    col3.metric("📈 Promedio global",     f"{df['promedio'].mean():.2f}")
    col4.metric("✅ Asistencia promedio", f"{df['pct_asistencia'].mean():.1f}%")

    st.divider()
<<<<<<< HEAD
=======

    # Distribución de riesgo
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
    st.subheader("🚨 Distribución de riesgo académico")
    conteo = (
        df.groupby("estado_riesgo")["num_documento"]
        .nunique()
        .reset_index()
        .rename(columns={"num_documento": "Estudiantes", "estado_riesgo": "Estado"})
    )
    st.dataframe(conteo, use_container_width=True, hide_index=True)

<<<<<<< HEAD
    criticos = (
        df[df["estado_riesgo"] == "🔴 En riesgo crítico"][[
            "nombre_completo", "codigo_asignatura", "nombre_asignatura",
            "promedio", "pct_asistencia",
        ]]
        .drop_duplicates()
        .sort_values("promedio")
    )
=======
    # Alerta de riesgo crítico
    criticos = df[df["estado_riesgo"] == "🔴 En riesgo crítico"][
        ["nombre_completo", "codigo_asignatura", "nombre_asignatura",
         "promedio", "pct_asistencia"]
    ].drop_duplicates().sort_values("promedio")

>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
    if len(criticos) > 0:
        st.warning(f"🔴 {len(criticos)} registros en riesgo crítico")
        st.dataframe(criticos, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Ningún estudiante en riesgo crítico")
<<<<<<< HEAD

    st.divider()
    st.subheader("📈 Gráficos")
    st.plotly_chart(grafico_dispersion_riesgo(df), use_container_width=True)
    st.plotly_chart(grafico_riesgo_por_asignatura(df), use_container_width=True)

    st.subheader("📊 Promedio por asignatura")
    promedios = (
        df.groupby("nombre_asignatura")["promedio"]
        .mean()
        .reset_index()
        .set_index("nombre_asignatura")
    )
    st.bar_chart(promedios)

    with st.expander("👥 Ver datos completos"):
        st.dataframe(df, use_container_width=True, hide_index=True)


def mostrar_vista_estudiante(df):
    """Renderiza la pestaña de búsqueda y detalle por estudiante.

    Presenta un selectbox con todos los estudiantes disponibles. Al seleccionar
    uno, muestra sus datos personales, una tabla con su rendimiento en cada
    asignatura (promedio, porcentaje de asistencia y estado de riesgo) y tres
    métricas de resumen: promedio general, asistencia promedio y número de
    asignaturas cursadas.

    Args:
        df (pd.DataFrame): DataFrame integrado y con indicadores calculados.
            Debe contener las columnas ``num_documento``, ``nombre_completo``,
            ``genero``, ``email``, ``nombre_asignatura``, ``creditos``,
            ``promedio``, ``pct_asistencia`` y ``estado_riesgo``.

    Returns:
        None
    """
    opciones = df[["num_documento", "nombre_completo"]].drop_duplicates().copy()
    opciones["etiqueta"] = (
        opciones["nombre_completo"] + " (" + opciones["num_documento"] + ")"
    )
=======
        
def mostrar_vista_estudiante(df):
    opciones = df[["num_documento", "nombre_completo"]].drop_duplicates()
    opciones["etiqueta"] = opciones["nombre_completo"] + " (" + opciones["num_documento"] + ")"
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b

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
<<<<<<< HEAD
    tabla = datos[[
        "nombre_asignatura", "creditos", "promedio", "pct_asistencia", "estado_riesgo",
=======

    tabla = datos[[
        "nombre_asignatura", "creditos", "promedio", "pct_asistencia", "estado_riesgo"
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
    ]].copy()
    tabla.columns = ["Asignatura", "Créditos", "Promedio", "% Asistencia", "Estado"]
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Promedio general",     f"{datos['promedio'].mean():.2f}")
    col2.metric("Asistencia promedio",  f"{datos['pct_asistencia'].mean():.1f}%")
    col3.metric("Asignaturas cursadas", len(datos))


def mostrar_vista_asignatura(df):
<<<<<<< HEAD
    """Renderiza la pestaña de análisis por asignatura.

    Presenta un selectbox con todas las asignaturas disponibles. Al seleccionar
    una, muestra su código y facultad, la tabla de estudiantes inscritos
    ordenada por promedio descendente y tres métricas del grupo: promedio,
    asistencia promedio y total de estudiantes.

    Args:
        df (pd.DataFrame): DataFrame integrado y con indicadores calculados.
            Debe contener las columnas ``nombre_asignatura``,
            ``codigo_asignatura``, ``facultad``, ``nombre_completo``,
            ``num_documento``, ``promedio``, ``pct_asistencia`` y
            ``estado_riesgo``.

    Returns:
        None
    """
=======
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
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
<<<<<<< HEAD
        "promedio", "pct_asistencia", "estado_riesgo",
    ]].copy()
    tabla.columns = ["Nombre", "Documento", "Promedio", "% Asistencia", "Estado"]
    st.dataframe(
        tabla.sort_values("Promedio", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Promedio del grupo",   f"{datos['promedio'].mean():.2f}")
    col2.metric("Asistencia del grupo", f"{datos['pct_asistencia'].mean():.1f}%")
    col3.metric("Estudiantes",          len(datos))


# ══════════════════════════════════════════════════════════════════════
# FUNCIÓN DE EXPORTACIÓN
# ══════════════════════════════════════════════════════════════════════

def generar_reporte_csv(df):
    """Genera el contenido de un reporte académico completo en formato CSV.

    Selecciona y renombra las columnas relevantes del DataFrame integrado para
    producir un CSV legible que el usuario puede descargar. El resultado se
    codifica en UTF-8 para compatibilidad con Excel y editores de texto.

    Args:
        df (pd.DataFrame): DataFrame integrado y con indicadores calculados.
            Debe contener las columnas ``nombre_completo``, ``num_documento``,
            ``nombre_asignatura``, ``creditos``, ``facultad``, ``promedio``,
            ``pct_asistencia`` y ``estado_riesgo``.

    Returns:
        bytes: Contenido del archivo CSV codificado en UTF-8, listo para
            pasarse a ``st.download_button``.
    """
    columnas = [
        "nombre_completo", "num_documento", "nombre_asignatura",
        "creditos", "facultad", "promedio", "pct_asistencia", "estado_riesgo",
    ]
    df_reporte = df[columnas].copy()
    df_reporte.columns = [
        "Nombre", "Documento", "Asignatura",
        "Créditos", "Facultad", "Promedio", "% Asistencia", "Estado de riesgo",
    ]
    return df_reporte.to_csv(index=False).encode("utf-8")


# ══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE LA PÁGINA
# ══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Panel Académico IDIA",
    page_icon="🎓",
    layout="wide",
)

# ── Encabezado ───────────────────────────────────────────────────────
st.title("🎓 Panel de Análisis Académico")
st.markdown("**Ingeniería de Datos e Inteligencia Artificial · Lógica Computacional**")
st.divider()

# ── Sidebar: carga de archivos ────────────────────────────────────────
st.sidebar.title("📂 Carga de archivos")
st.sidebar.info("Sube los 4 archivos del sistema académico para comenzar el análisis.")

archivo_excel = st.sidebar.file_uploader(
    "1️⃣ Datos de estudiantes (Excel)",
    type=["xlsx", "xls"],
)
archivo_csv = st.sidebar.file_uploader(
    "2️⃣ Espacios académicos (CSV)",
    type=["csv"],
)
archivo_json = st.sidebar.file_uploader("3️⃣ Notas (JSON)", type=["json"])
archivo_prn  = st.sidebar.file_uploader("4️⃣ Asistencias (PRN)", type=["prn", "txt"])

# ── Cargar y guardar en session_state cuando hay archivo nuevo ────────
if archivo_excel is not None:
    df = intentar_carga(cargar_estudiantes, archivo_excel, "Estudiantes")
    if df is not None:
        st.session_state["df_estudiantes"] = df
        st.session_state.pop("df_final", None)  # invalidar integración previa
        st.sidebar.success(f"✅ {len(df)} estudiantes cargados")

if archivo_csv is not None:
    df = intentar_carga(cargar_asignaturas, archivo_csv, "Asignaturas")
    if df is not None:
        st.session_state["df_asignaturas"] = df
        st.session_state.pop("df_final", None)
        st.sidebar.success(f"✅ {len(df)} asignaturas cargadas")

if archivo_json is not None:
    df = intentar_carga(cargar_notas, archivo_json, "Notas")
    if df is not None:
        st.session_state["df_notas"] = df
        st.session_state.pop("df_final", None)
        st.sidebar.success(f"✅ {len(df)} registros de notas cargados")

if archivo_prn is not None:
    df = intentar_carga(cargar_asistencias, archivo_prn, "Asistencias")
    if df is not None:
        st.session_state["df_asistencias"] = df
        st.session_state.pop("df_final", None)
        st.sidebar.success(f"✅ {len(df)} registros de asistencia cargados")

# ── Verificar si todos los datos están listos ─────────────────────────
todos_listos = all(
    k in st.session_state
    for k in ("df_estudiantes", "df_asignaturas", "df_notas", "df_asistencias")
)

if not todos_listos: 
    st.info("ℹ️ Carga los 4 archivos en el panel lateral para comenzar.")
    with st.expander("📋 Instrucciones de uso", expanded=True):
        st.markdown("1. Sube los 4 archivos en el panel lateral.")
        st.markdown("2. Navega por las pestañas para ver el análisis.")
    st.stop()

# ── Integración y cálculo de indicadores ─────────────────────────────
if "df_final" not in st.session_state:
    try:
        df_integrado, advertencias = integrar_datos(
            st.session_state["df_estudiantes"],
            st.session_state["df_asignaturas"],
            st.session_state["df_notas"],
            st.session_state["df_asistencias"],
        )
        df_final = calcular_todos_indicadores(df_integrado)
        st.session_state["df_final"]     = df_final
        st.session_state["advertencias"] = advertencias
    except Exception as e:
        st.error(f"❌ Error al integrar los datos: {e}")
        st.stop()

df_final = st.session_state["df_final"]

for adv in st.session_state.get("advertencias", []):
    st.warning(adv)

st.success("✅ Los 4 archivos están cargados. Puedes ver el análisis.")

# ── Pestañas principales ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Resumen general",
    "🔍 Búsqueda por estudiante",
    "📚 Por asignatura",
])

with tab1:
    mostrar_resumen_general(df_final)

with tab2:
    mostrar_vista_estudiante(df_final)

with tab3:
    mostrar_vista_asignatura(df_final)

# ── Probador de funciones de cálculo ─────────────────────────────────
=======
        "promedio", "pct_asistencia", "estado_riesgo"
    ]].copy()
    tabla.columns = ["Nombre", "Documento", "Promedio", "% Asistencia", "Estado"]
    st.dataframe(tabla.sort_values("Promedio", ascending=False),
                 use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Promedio del grupo",    f"{datos['promedio'].mean():.2f}")
    col2.metric("Asistencia del grupo",  f"{datos['pct_asistencia'].mean():.1f}%")
    col3.metric("Estudiantes",           len(datos))


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


>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
with st.expander("🛠️ Probador de funciones de cálculo"):
    col1, col2 = st.columns(2)

    with col1:
        notas_txt = st.text_input("Notas separadas por coma", value="3.5, 4.0, 4.2, 3.8")
        hechas    = st.number_input("Asistencias realizadas", value=28, min_value=0)
        total     = st.number_input("Total asistencias",      value=32, min_value=1)

    with col2:
<<<<<<< HEAD
        lista  = [float(n.strip()) for n in notas_txt.split(",") if n.strip()]
=======
        lista  = [float(n.strip()) for n in notas_txt.split(",")]
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
        prom   = calcular_promedio(lista)
        pct    = calcular_porcentaje_asistencia(hechas, total)
        riesgo = clasificar_riesgo(prom, pct)

        st.metric("Promedio calculado", f"{prom:.2f} / 5.0")
        st.metric("% Asistencia",       f"{pct:.1f}%")
        st.metric("Estado de riesgo",   riesgo)

<<<<<<< HEAD
# ── Descarga de reporte ───────────────────────────────────────────────
st.download_button(
    label="⬇️ Descargar reporte completo (CSV)",
    data=generar_reporte_csv(df_final),
    file_name="reporte_academico.csv",
    mime="text/csv",
)
=======

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
>>>>>>> e36c8e955e63c27ccdcda68f16175b9db8bab49b
