import pandas as pd

def integrar_datos(df_estudiantes, df_asignaturas, df_notas, df_asistencias):
    """
    Une los cuatro DataFrames en uno solo usando claves comunes.

    La tabla central es df_notas. Se le van uniendo los datos de
    estudiantes, asignaturas y asistencias mediante merge (similar a JOIN en SQL).

    Parámetros:
        df_estudiantes  (pd.DataFrame): datos personales de estudiantes
        df_asignaturas  (pd.DataFrame): datos de espacios académicos
        df_notas        (pd.DataFrame): calificaciones por (estudiante, asignatura)
        df_asistencias  (pd.DataFrame): asistencias por (estudiante, asignatura)

    Retorna:
        tuple:
            - pd.DataFrame integrado (una fila por estudiante × asignatura)
            - list de strings con advertencias (registros sin cruce)
    """

    # Paso 1: Partir de notas como tabla central
    df = df_notas.copy()

    # Paso 2: Unir datos del estudiante (por num_documento)
    df = df.merge(
        df_estudiantes[[
            "num_documento", "nombre_completo", "genero",
            "fecha_nacimiento", "eps", "email"
        ]],
        on="num_documento",
        how="left"    # left join: mantener todos los registros de notas
    )

    # Paso 3: Unir datos de la asignatura (por codigo_asignatura)
    df = df.merge(
        df_asignaturas[["codigo", "nombre", "creditos", "facultad"]],
        left_on="codigo_asignatura",
        right_on="codigo",
        how="left"
    )
    df = df.drop(columns=["codigo"])         # Eliminar columna duplicada
    df = df.rename(columns={"nombre": "nombre_asignatura"})

    # Paso 4: Unir asistencias (por num_documento + codigo_asignatura)
    df = df.merge(
        df_asistencias,
        on=["codigo_asignatura", "num_documento"],
        how="left"
    )

    # Paso 5: Detectar registros sin cruce y generar advertencias
    advertencias = []

    sin_estudiante = df["nombre_completo"].isna().sum()
    sin_asignatura = df["nombre_asignatura"].isna().sum()
    sin_asistencia = df["asistencias_total"].isna().sum()

    if sin_estudiante > 0:
        advertencias.append(
            f"⚠️ {sin_estudiante} registros de notas sin estudiante coincidente. "
            f"Verifica que los números de documento en notas.json coincidan con estudiantes.xlsx."
        )
    if sin_asignatura > 0:
        advertencias.append(
            f"⚠️ {sin_asignatura} registros sin asignatura coincidente. "
            f"Verifica que los códigos en notas.json coincidan con asignaturas.csv."
        )
    if sin_asistencia > 0:
        advertencias.append(
            f"⚠️ {sin_asistencia} registros sin datos de asistencia. "
            f"Verifica que asistencias.prn tenga todos los pares (estudiante, asignatura)."
        )

    return df, advertencias