import pandas as pd
import json

def cargar_estudiantes(archivo):
    """
    Lee el archivo Excel de estudiantes y retorna un DataFrame.
    Valida que existan las columnas requeridas.

    Parámetros:
        archivo: objeto de archivo (de st.file_uploader o open())

    Retorna:
        pd.DataFrame con los datos de estudiantes, limpiados.

    Lanza:
        ValueError si faltan columnas obligatorias.
    """
    columnas_requeridas = [
        "nombre_completo", "tipo_documento", "num_documento",
        "genero", "fecha_nacimiento", "eps", "direccion",
        "telefono", "email"
    ]

    df = pd.read_excel(archivo, dtype={"num_documento": str})

    # Validación de estructura: ciclo for sobre la lista de columnas requeridas
    columnas_faltantes = []
    for col in columnas_requeridas:
        if col not in df.columns:
            columnas_faltantes.append(col)

    if len(columnas_faltantes) > 0:
        raise ValueError(f"Faltan columnas en el archivo: {columnas_faltantes}")

    # Limpieza básica
    df["num_documento"]   = df["num_documento"].str.strip()
    df["nombre_completo"] = df["nombre_completo"].str.strip().str.title()

    return df

def cargar_asignaturas(archivo):
    """
    Lee el archivo CSV de espacios académicos.
    Detecta automáticamente el separador (punto y coma o coma).

    Parámetros:
        archivo: objeto de archivo (de st.file_uploader o open())

    Retorna:
        pd.DataFrame con los datos de asignaturas, limpiados.

    Lanza:
        ValueError si faltan columnas obligatorias.
    """
    # Intentar con punto y coma primero; si falla, probar con coma
    try:
        df = pd.read_csv(archivo, sep=";", dtype={"codigo": str})
    except Exception:
        archivo.seek(0)   # Resetear cursor del archivo al inicio
        df = pd.read_csv(archivo, sep=",", dtype={"codigo": str})

    columnas_requeridas = ["codigo", "nombre", "creditos", "facultad"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Columna requerida no encontrada: '{col}'")

    df["codigo"] = df["codigo"].str.strip().str.upper()
    df["nombre"] = df["nombre"].str.strip().str.title()

    return df

def cargar_notas(archivo):
    """
    Lee el archivo JSON de notas.
    Retorna un DataFrame con una fila por (estudiante, asignatura).
    La columna 'notas' contiene la lista de calificaciones original.

    Parámetros:
        archivo: objeto de archivo (de st.file_uploader o open())

    Retorna:
        pd.DataFrame con columnas: codigo_asignatura, num_documento, notas.

    Lanza:
        ValueError si falta algún campo requerido o el formato es incorrecto.
    """
    contenido = archivo.read()
    datos = json.loads(contenido)

    registros = []
    for entrada in datos:
        # Validar que cada entrada tenga los tres campos obligatorios
        if "codigo_asignatura" not in entrada:
            raise ValueError("Falta campo 'codigo_asignatura' en el JSON")
        if "num_documento" not in entrada:
            raise ValueError("Falta campo 'num_documento' en el JSON")
        if "notas" not in entrada:
            raise ValueError("Falta campo 'notas' en el JSON")

        # Validar que 'notas' sea una lista
        if not isinstance(entrada["notas"], list):
            raise ValueError("El campo 'notas' debe ser una lista de números")

        registros.append({
            "codigo_asignatura": str(entrada["codigo_asignatura"]).strip().upper(),
            "num_documento":     str(entrada["num_documento"]).strip(),
            "notas":             entrada["notas"]
        })

    return pd.DataFrame(registros)

def cargar_asistencias(archivo):
    """
    Lee el archivo PRN de ancho fijo (fixed-width).
    Interpreta cada columna según su posición exacta en la línea.

    Parámetros:
        archivo: objeto de archivo (de st.file_uploader o open())

    Retorna:
        pd.DataFrame con columnas:
            codigo_asignatura, num_documento,
            asistencias_hechas, asistencias_total.

    Lanza:
        ValueError si hay valores no numéricos en las columnas de asistencia.
    """
    # read_fwf: pandas lee archivos de ancho fijo por rango de posición
    df = pd.read_fwf(
        archivo,
        colspecs=[
            (0,  10),   # codigo_asignatura
            (10, 22),   # num_documento
            (22, 26),   # asistencias_hechas
            (26, 30),   # asistencias_total
        ],
        names=[
            "codigo_asignatura", "num_documento",
            "asistencias_hechas", "asistencias_total"
        ],
        dtype={"num_documento": str, "codigo_asignatura": str}
    )

    # Limpiar espacios en blanco en columnas de texto
    df["codigo_asignatura"] = df["codigo_asignatura"].str.strip().str.upper()
    df["num_documento"]     = df["num_documento"].str.strip()

    # Convertir a entero con validación
    df["asistencias_hechas"] = pd.to_numeric(df["asistencias_hechas"], errors="coerce")
    df["asistencias_total"]  = pd.to_numeric(df["asistencias_total"],  errors="coerce")

    if df["asistencias_hechas"].isna().any():
        raise ValueError("El archivo PRN contiene valores no numéricos en asistencias_hechas")

    return df

