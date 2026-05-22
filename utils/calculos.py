# ── Constantes del modelo de riesgo ─────────────────────────────────
UMBRAL_NOTA_MINIMA    = 3.0   # Nota mínima para aprobar (escala colombiana 0-5)
UMBRAL_ASISTENCIA_MIN = 75.0  # % mínimo de asistencia requerido


def calcular_promedio(lista_notas):
    """
    Calcula el promedio aritmético de una lista de notas.

    Ignora valores no numéricos o fuera del rango 0.0–5.0.
    Retorna 0.0 si la lista está vacía o todos los valores son inválidos.

    Parámetros:
        lista_notas (list): lista de calificaciones numéricas

    Retorna:
        float: promedio redondeado a 2 decimales

    Ejemplos:
        calcular_promedio([3.5, 4.0, 4.5]) → 4.0
        calcular_promedio([])              → 0.0
        calcular_promedio(["a", 3.0])      → 3.0  (ignora "a")
    """
    if not isinstance(lista_notas, list) or len(lista_notas) == 0:
        return 0.0

    suma     = 0.0
    cantidad = 0

    for nota in lista_notas:          # Ciclo for sobre la lista de notas
        try:
            valor = float(nota)
            if 0.0 <= valor <= 5.0:   # Condicional: validar rango
                suma     += valor
                cantidad += 1
        except (ValueError, TypeError):
            pass                      # Ignorar valores no convertibles

    if cantidad == 0:
        return 0.0

    return round(suma / cantidad, 2)


def agregar_promedio(df):
    """
    Agrega la columna 'promedio' al DataFrame integrado.
    Aplica calcular_promedio() a cada fila de la columna 'notas'.
    """
    df = df.copy()
    df["promedio"] = df["notas"].apply(calcular_promedio)
    return df

def calcular_porcentaje_asistencia(hechas, total):
    """
    Calcula el porcentaje de asistencia de un estudiante en una asignatura.

    Parámetros:
        hechas (int o float): número de clases a las que asistió
        total  (int o float): número total de clases programadas

    Retorna:
        float: porcentaje entre 0.0 y 100.0, redondeado a 1 decimal.

    Ejemplos:
        calcular_porcentaje_asistencia(28, 32) → 87.5
        calcular_porcentaje_asistencia(0, 30)  → 0.0
        calcular_porcentaje_asistencia(28, 0)  → 0.0  (evita división por cero)
    """
    try:
        hechas = float(hechas)
        total  = float(total)
    except (ValueError, TypeError):
        return 0.0

    if total <= 0:                     # Condicional: prevenir división por cero
        return 0.0

    porcentaje = (hechas / total) * 100
    return round(porcentaje, 1)


def agregar_porcentaje_asistencia(df):
    """
    Agrega la columna 'pct_asistencia' al DataFrame integrado.
    """
    df = df.copy()
    df["pct_asistencia"] = df.apply(
        lambda fila: calcular_porcentaje_asistencia(
            fila["asistencias_hechas"],
            fila["asistencias_total"]
        ),
        axis=1   # axis=1 → aplicar función por fila (no por columna)
    )
    return df

def clasificar_riesgo(promedio, pct_asistencia,
                      umbral_nota=UMBRAL_NOTA_MINIMA,
                      umbral_asistencia=UMBRAL_ASISTENCIA_MIN):
    """
    Clasifica el estado de riesgo académico de un estudiante en una asignatura.

    Niveles de riesgo:
        "🔴 En riesgo crítico" → nota baja Y asistencia baja (ambos criterios fallan)
        "🟡 En riesgo parcial" → solo uno de los dos criterios falla
        "🟢 Sin riesgo"        → cumple ambos criterios

    Parámetros:
        promedio          (float): promedio de notas del estudiante
        pct_asistencia    (float): porcentaje de asistencia
        umbral_nota       (float): nota mínima para no estar en riesgo (default 3.0)
        umbral_asistencia (float): % mínimo de asistencia (default 75.0)

    Retorna:
        str: etiqueta del nivel de riesgo

    Ejemplos:
        clasificar_riesgo(2.5, 60.0) → "🔴 En riesgo crítico"
        clasificar_riesgo(3.5, 60.0) → "🟡 En riesgo parcial"
        clasificar_riesgo(2.5, 85.0) → "🟡 En riesgo parcial"
        clasificar_riesgo(3.8, 85.0) → "🟢 Sin riesgo"
    """
    nota_baja       = promedio       < umbral_nota          # True o False
    asistencia_baja = pct_asistencia < umbral_asistencia    # True o False

    if nota_baja and asistencia_baja:       # Ambos criterios fallan
        return "🔴 En riesgo crítico"
    elif nota_baja or asistencia_baja:      # Solo uno falla
        return "🟡 En riesgo parcial"
    else:                                   # Ninguno falla
        return "🟢 Sin riesgo"


def agregar_riesgo(df):
    """
    Agrega la columna 'estado_riesgo' al DataFrame integrado.
    """
    df = df.copy()
    df["estado_riesgo"] = df.apply(
        lambda fila: clasificar_riesgo(
            fila["promedio"],
            fila["pct_asistencia"]
        ),
        axis=1
    )
    return df

def calcular_todos_indicadores(df):
    """
    Aplica todas las funciones de cálculo en secuencia al DataFrame integrado.

    Orden de aplicación:
        1. agregar_promedio        → columna 'promedio'
        2. agregar_porcentaje_asistencia → columna 'pct_asistencia'
        3. agregar_riesgo          → columna 'estado_riesgo'

    Parámetros:
        df (pd.DataFrame): DataFrame integrado de los cuatro archivos

    Retorna:
        pd.DataFrame: mismo DataFrame con las tres columnas nuevas agregadas
    """
    df = agregar_promedio(df)
    df = agregar_porcentaje_asistencia(df)
    df = agregar_riesgo(df)
    return df