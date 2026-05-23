# Panel de Análisis Académico — IDIA

Aplicación web desarrollada con **Streamlit** para el análisis del rendimiento académico de estudiantes del programa **Ingeniería de Datos e Inteligencia Artificial**, en el marco del curso de Lógica Computacional.

La herramienta integra cuatro fuentes de datos (estudiantes, asignaturas, notas y asistencias), calcula indicadores de riesgo académico y los presenta mediante tablas interactivas y gráficos.

---

## Funcionalidades

- **Carga de archivos en la interfaz**: sube los cuatro archivos desde el panel lateral sin necesidad de modificar código.
- **Integración automática de datos**: cruce de estudiantes, asignaturas, notas y asistencias usando claves comunes.
- **Cálculo de indicadores**:
  - Promedio de notas por estudiante y asignatura (escala 0–5).
  - Porcentaje de asistencia.
  - Clasificación de riesgo académico en tres niveles.
- **Vistas de análisis**:
  - Resumen general del semestre con métricas globales y gráficos.
  - Búsqueda y detalle por estudiante.
  - Análisis por asignatura.
- **Probador interactivo** de las funciones de cálculo directamente en la app.
- **Exportación** del reporte completo en formato CSV.

### Niveles de riesgo académico

| Estado | Condición |
|---|---|
| 🟢 Sin riesgo | Promedio ≥ 3.0 **y** asistencia ≥ 75% |
| 🟡 En riesgo parcial | Solo uno de los dos criterios falla |
| 🔴 En riesgo crítico | Promedio < 3.0 **y** asistencia < 75% |

---

## Estructura del proyecto

```
proyecto_final/
├── app.py                  # Aplicación principal (Streamlit)
├── utils/
│   ├── __init__.py
│   ├── calculos.py         # Funciones de promedio, asistencia y riesgo
│   ├── carga_datos.py      # Lectura y validación de los cuatro archivos
│   └── integracion.py      # Merge de los DataFrames
└── files/
    ├── estudiantes.xlsx    # Datos personales de estudiantes
    ├── asignaturas.csv     # Espacios académicos
    ├── notas.json          # Calificaciones por estudiante y asignatura
    └── asistencias.prn     # Asistencias en formato de ancho fijo
```

---

## Formatos de archivo

### `estudiantes.xlsx` — Excel
Columnas requeridas:

| Columna | Descripción |
|---|---|
| `nombre_completo` | Nombre completo del estudiante |
| `tipo_documento` | Tipo de identificación (CC, TI, etc.) |
| `num_documento` | Número de documento (clave de unión) |
| `genero` | Género |
| `fecha_nacimiento` | Fecha de nacimiento |
| `eps` | EPS del estudiante |
| `direccion` | Dirección de residencia |
| `telefono` | Teléfono de contacto |
| `email` | Correo electrónico |

### `asignaturas.csv` — CSV (separador `;` o `,`)
Columnas requeridas: `codigo`, `nombre`, `creditos`, `facultad`

```
codigo;nombre;creditos;facultad
LC001;Lógica Computacional;3;Ingeniería
```

### `notas.json` — JSON
Lista de objetos con los campos `codigo_asignatura`, `num_documento` y `notas` (lista de números):

```json
[
  {
    "codigo_asignatura": "LC001",
    "num_documento": "1001234567",
    "notas": [4.0, 4.3, 4.2]
  }
]
```

### `asistencias.prn` — Ancho fijo (PRN)
Columnas por posición de carácter:

| Posición | Columna |
|---|---|
| 0–9 | `codigo_asignatura` |
| 10–21 | `num_documento` |
| 22–25 | `asistencias_hechas` |
| 26–29 | `asistencias_total` |

```
LC001     1001234567    31  32
```

---

## Instalación

### Requisitos previos
- Python 3.10 o superior
- pip

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/joalsaoss/proyectofinal.git
   cd proyectofinal
   ```

2. Crea y activa un entorno virtual:
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # macOS / Linux
   python -m venv env
   source env/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install streamlit pandas plotly openpyxl
   ```

---

## Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en el navegador en `http://localhost:8501`.

### Uso rápido con los datos de prueba

En la carpeta `files/` ya existen archivos de prueba listos para usar. Desde el panel lateral de la aplicación, sube cada uno en su campo correspondiente:

1. `estudiantes.xlsx` → campo **Datos de estudiantes (Excel)**
2. `asignaturas.csv` → campo **Espacios académicos (CSV)**
3. `notas.json` → campo **Notas (JSON)**
4. `asistencias.prn` → campo **Asistencias (PRN)**

Una vez cargados los cuatro archivos, la aplicación mostrará el análisis completo.

### Generar nuevos datos de prueba

```bash
python files/_generar_datos.py
```

---

## Tecnologías utilizadas

| Librería | Uso |
|---|---|
| [Streamlit](https://streamlit.io/) | Interfaz web interactiva |
| [Pandas](https://pandas.pydata.org/) | Manipulación y análisis de datos |
| [Plotly](https://plotly.com/python/) | Gráficos interactivos |
| [openpyxl](https://openpyxl.readthedocs.io/) | Lectura de archivos Excel |

---

## Autores

Proyecto final — Lógica Computacional  
Ingeniería de Datos e Inteligencia Artificial
