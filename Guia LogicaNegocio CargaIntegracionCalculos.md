# Guía de Lógica de Negocio — Carga, Integración y Cálculo de Indicadores

## Lógica Computacional · Ingeniería de Datos e Inteligencia Artificial

### Unidad 4 — Aplicación al Proyecto Final

-----

> **¿Para qué sirve este documento?**
> Cubre toda la lógica interna del proyecto: lectura de los cuatro formatos de archivo, integración de datos mediante claves comunes y cálculo de indicadores académicos (promedios, asistencia y riesgo). Todo este código vive en los módulos `utils/` y **no depende de Streamlit**. La construcción de la interfaz está en el documento complementario.

-----

## Estructura de módulos

```
utils/
├── carga_datos.py    # Lectura de Excel, CSV, JSON y PRN
├── integracion.py    # Unión de los cuatro DataFrames
└── calculos.py       # Promedio, asistencia y clasificación de riesgo
```

Principio clave: **separación de responsabilidades**. Ninguna función de estos módulos debe importar `streamlit`. La interfaz llama a las funciones; las funciones no saben nada de la interfaz.

-----

## Módulo 1 — `utils/carga_datos.py`

### Función 1: Lectura del Excel de estudiantes

**Columnas esperadas:**
`nombre_completo | tipo_documento | num_documento | genero | fecha_nacimiento | eps | direccion | telefono | email`

```python
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
```

**Diagrama de flujo — `cargar_estudiantes`:**

```
INICIO
  │
  ▼
Leer archivo Excel → df
  │
  ▼
Para cada columna requerida:
  ¿Está en df.columns?
  │ NO → Agregar a columnas_faltantes
  │ SÍ → Continuar
  │
  ▼
¿columnas_faltantes no está vacía?
  │ SÍ → Lanzar ValueError
  │ NO → Limpiar y retornar df
  │
FIN
```

-----

### Función 2: Lectura del CSV de asignaturas

**Columnas esperadas:**
`codigo | nombre | creditos | facultad`

```python
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
```

-----

### Función 3: Lectura del JSON de notas

**Estructura esperada del JSON:**

```json
[
  {
    "codigo_asignatura": "LC001",
    "num_documento": "1020345678",
    "notas": [3.5, 4.2, 3.8, 4.5, 3.9]
  },
  {
    "codigo_asignatura": "MA001",
    "num_documento": "1020345678",
    "notas": [2.8, 3.5, 4.0, 3.2]
  }
]
```

Cada elemento de la lista es una entrada **estudiante × asignatura**. La clave `notas` contiene una lista de calificaciones (una por evaluación del semestre).

```python
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
```

-----

### Función 4: Lectura del PRN de asistencias (ancho fijo)

Un archivo PRN tiene columnas definidas **por posición de caracteres**, no por delimitadores. Ejemplo del archivo:

```
LC001     10203456780280  32
MA001     10203456781225  30
LC001     10198765430282  32
```

Especificación de columnas:

```
Caracteres  0 – 9  → codigo_asignatura   (10 chars)
Caracteres 10 – 21 → num_documento       (12 chars)
Caracteres 22 – 25 → asistencias_hechas   (4 chars)
Caracteres 26 – 29 → asistencias_total    (4 chars)
```

```python
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
```

**¿Por qué `read_fwf` y no `split()`?**
`read_fwf` maneja automáticamente archivos grandes, valores nulos y la conversión de tipos. Es la forma robusta y profesional de leer archivos de ancho fijo, sin necesidad de cortar manualmente cada línea.

-----

### Datos de prueba para practicar

Si aún no tienen los archivos reales, crear estos archivos manualmente:

**`estudiantes.xlsx`** (5 registros mínimo):

```
nombre_completo         | tipo_documento | num_documento | genero | fecha_nacimiento | eps       | direccion           | telefono   | email
Laura Gómez Rodríguez   | CC             | 1020345678    | F      | 2004-03-15       | Sura      | Cra 7 #45-20 Bogotá | 3001234567 | lgomez@correo.edu
Carlos Pérez Mora        | CC             | 1019876543    | M      | 2003-11-22       | Compensar | Av 68 #12-34 Bogotá | 3109876543 | cperez@correo.edu
María Fernanda Torres    | CC             | 1021456789    | F      | 2004-07-08       | Nueva EPS | Cll 100 #15-60      | 3205551234 | mftorres@correo.edu
Andrés Felipe Ruiz       | CC             | 1018234567    | M      | 2003-09-30       | Sanitas   | Dg 40 Sur #22-11    | 3153339876 | afruiz@correo.edu
```

**`asignaturas.csv`**:

```
codigo;nombre;creditos;facultad
LC001;Lógica Computacional;3;Ingeniería de Datos
MA001;Matemáticas Fundamentales;4;Ciencias Básicas
FI001;Física General;3;Ciencias Básicas
IN001;Inglés Técnico;2;Humanidades
```

**`notas.json`** (mínimo 8 registros — 4 estudiantes × 2 asignaturas):

```json
[
  {"codigo_asignatura": "LC001", "num_documento": "1020345678", "notas": [3.5, 4.2, 3.8]},
  {"codigo_asignatura": "MA001", "num_documento": "1020345678", "notas": [2.8, 3.5, 4.0]},
  {"codigo_asignatura": "LC001", "num_documento": "1019876543", "notas": [4.5, 4.8, 4.2]},
  {"codigo_asignatura": "MA001", "num_documento": "1019876543", "notas": [2.5, 2.8, 3.0]},
  {"codigo_asignatura": "LC001", "num_documento": "1021456789", "notas": [3.0, 2.8, 3.2]},
  {"codigo_asignatura": "MA001", "num_documento": "1021456789", "notas": [4.0, 4.2, 4.5]},
  {"codigo_asignatura": "LC001", "num_documento": "1018234567", "notas": [2.0, 2.5, 2.8]},
  {"codigo_asignatura": "MA001", "num_documento": "1018234567", "notas": [3.8, 4.0, 3.9]}
]
```

-----

## Módulo 2 — `utils/integracion.py`

### Lógica de integración por claves comunes

La integración conecta los cuatro DataFrames usando las columnas que tienen en común:

```
df_notas      ←→ df_estudiantes   por: num_documento
df_notas      ←→ df_asignaturas   por: codigo_asignatura
df_notas      ←→ df_asistencias   por: num_documento + codigo_asignatura
```

El DataFrame de **notas** actúa como tabla central porque es el que tiene la relación N×M (un estudiante puede estar en varias asignaturas, y una asignatura tiene varios estudiantes).

```python
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
```

**¿Por qué `how="left"` y no `how="inner"`?**
Con `left join`, si un estudiante no tiene asistencia registrada, su fila igual aparece en el resultado (con `NaN` en las columnas de asistencia). Con `inner join` esa fila desaparecería silenciosamente. El `left join` permite detectar y reportar esos casos faltantes.

-----

## Módulo 3 — `utils/calculos.py`

### Constantes del modelo de riesgo

Los umbrales deben declararse como constantes con nombre, no como números dentro del código. Esto facilita cambiarlos sin buscar en todo el archivo:

```python
# ── Constantes del modelo de riesgo ─────────────────────────────────
UMBRAL_NOTA_MINIMA    = 3.0   # Nota mínima para aprobar (escala colombiana 0-5)
UMBRAL_ASISTENCIA_MIN = 75.0  # % mínimo de asistencia requerido
```

-----

### Función 1: Calcular promedio de notas

La columna `notas` contiene una lista Python por cada fila. Esta función procesa esa lista elemento a elemento:

```python
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
```

**¿Por qué `.apply()` y no un ciclo `for` sobre el DataFrame?**
`.apply()` recorre las filas internamente de forma eficiente y el código queda más limpio. Un ciclo `for` sobre un DataFrame es mucho más lento en archivos grandes.

-----

### Función 2: Calcular porcentaje de asistencia

```python
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
```

-----

### Función 3: Clasificar el estado de riesgo académico

```python
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
```

**Pseudocódigo de `clasificar_riesgo`:**

```
FUNCIÓN clasificar_riesgo(promedio, pct_asistencia)
  nota_baja       ← promedio < 3.0
  asistencia_baja ← pct_asistencia < 75.0

  SI nota_baja Y asistencia_baja ENTONCES
    RETORNAR "En riesgo crítico"
  SINO SI nota_baja O asistencia_baja ENTONCES
    RETORNAR "En riesgo parcial"
  SINO
    RETORNAR "Sin riesgo"
  FIN SI
FIN FUNCIÓN
```

-----

### Función 4: Función maestra de cálculo

```python
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
```

-----

## Casos de prueba documentados

Es buena práctica verificar manualmente que las funciones retornan lo esperado antes de integrarlas en la aplicación:

|Caso                  |Entrada               |Resultado esperado     |¿Por qué?                     |
|----------------------|----------------------|-----------------------|------------------------------|
|Normal                |`[3.5, 4.0, 4.5]`     |`4.0`                  |Suma=12, cantidad=3, 12/3=4.0 |
|Lista vacía           |`[]`                  |`0.0`                  |No hay notas que promediar    |
|Nota inválida mezclada|`["a", 3.0, 4.0]`     |`3.5`                  |Ignora “a”, promedia 3.0 y 4.0|
|Nota fuera de rango   |`[6.0, 3.0]`          |`3.0`                  |6.0 > 5.0 → se ignora         |
|Asistencia normal     |`hechas=28, total=32` |`87.5`                 |(28/32)×100                   |
|Total = 0             |`hechas=10, total=0`  |`0.0`                  |Previene división por cero    |
|Riesgo crítico        |`promedio=2.5, pct=60`|`"🔴 En riesgo crítico"`|Ambos criterios fallan        |
|Riesgo parcial        |`promedio=3.5, pct=60`|`"🟡 En riesgo parcial"`|Solo asistencia falla         |
|Sin riesgo            |`promedio=3.8, pct=85`|`"🟢 Sin riesgo"`       |Ninguno falla                 |

-----

## Resumen de relaciones entre módulos

```
app.py (Streamlit)
    │
    ├── llama a → cargar_estudiantes()   ┐
    ├── llama a → cargar_asignaturas()   │  utils/carga_datos.py
    ├── llama a → cargar_notas()         │
    ├── llama a → cargar_asistencias()   ┘
    │
    ├── llama a → integrar_datos()           utils/integracion.py
    │
    └── llama a → calcular_todos_indicadores()  utils/calculos.py
                      ├── agregar_promedio()
                      ├── agregar_porcentaje_asistencia()
                      └── agregar_riesgo()
                              └── clasificar_riesgo()
```

Cada módulo tiene **una sola responsabilidad**. Ninguno depende de otro módulo del mismo nivel: `calculos.py` no importa `carga_datos.py`, y viceversa. Solo `app.py` importa de todos.

-----

## Conceptos del curso aplicados en este módulo

|Concepto visto en clase           |Dónde se aplica                                                                  |
|----------------------------------|---------------------------------------------------------------------------------|
|Ciclo `for`                       |Recorrer `columnas_requeridas`, recorrer la lista de notas en `calcular_promedio`|
|Condicional `if/elif/else`        |Validar columnas faltantes, clasificar riesgo, prevenir división por cero        |
|Funciones con parámetros y retorno|Todas las funciones de los módulos `utils/`                                      |
|Arreglos / listas                 |La columna `notas` es una lista; `columnas_requeridas` es una lista              |
|Diccionarios                      |Cada entrada del JSON es un diccionario; `registros` es lista de diccionarios    |
|Arreglos multidimensionales       |El DataFrame es conceptualmente una matriz de filas × columnas                   |
|Estructuras y archivos            |Lectura de Excel, CSV, JSON y PRN como archivos estructurados                    |

-----

*Guía de Lógica de Negocio — Lógica Computacional · IDIA · Universidad Santo Tomás · Semestre I*