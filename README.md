# Amazon Bedrock: las ventajas reales de un RAG gestionado en AWS

**Entendiendo RAG construyéndolo tres veces y quitando una capa de abstracción en cada versión.**

Proyecto de la charla presentada en **CodeOn 2026**, organizada por Developer Student Clubs UTP.

Construí el mismo asistente RAG de tres formas para entender qué resuelve **Amazon Bedrock Knowledge Bases** por ti y qué implica construir esas piezas por cuenta propia.

> **Idea central:** Bedrock no es magia: ofrece componentes de RAG gestionados que evitan implementar y mantener ciertas piezas por separado. Entender qué hay detrás permite decidir cuándo conviene utilizarlos y cuándo tiene sentido construir una solución propia.

![Banner de la charla CodeOn 2026](docs/images/banner-codeon2026.png)

## Explora las tres fases

| Fase | Qué encontrarás | README |
|---|---|---|
| **1. RAG gestionado** | Amazon Bedrock Knowledge Bases, S3 y Lambda. Exploración de la recuperación de información sin implementar manualmente el chunking, los embeddings ni la base vectorial. | [Ver la Fase 1](phase1-direct-retrieval/README.md) |
| **2. RAG por componentes en AWS** | Titan Text Embeddings V2, ChromaDB y Amazon Nova Lite. Construcción del flujo de recuperación y generación mediante código propio. | [Ver la Fase 2](phase2-component-based-rag/README.md) |
| **3. RAG fuera de AWS** | LangChain, ChromaDB y Google Gemini. Implementación local del mismo patrón con otras herramientas. | [Ver la Fase 3](phase3-code-first-rag/README.md) |

## El caso de uso

El proyecto utiliza un asistente que responde preguntas sobre las fichas técnicas ficticias de tres vehículos: **Alpha, Beta y Gamma**.

Se probaron dos tipos de preguntas:

- **Pregunta con respuesta disponible:** ¿Cuáles son las especificaciones de seguridad del modelo Alpha?
- **Pregunta trampa:** ¿Cuál es la garantía extendida del modelo Alpha? Esa información no aparece en las fichas técnicas.

La segunda pregunta permite observar cómo se comporta el sistema cuando la información solicitada no está disponible en los documentos.

## ¿Qué hay detrás de un RAG?

RAG significa *Retrieval-Augmented Generation*, o generación aumentada por recuperación. Combina la búsqueda de información relevante con un modelo que utiliza esa información para elaborar una respuesta.

| Componente | Qué hace |
|---|---|
| **Chunking** | Divide los documentos en fragmentos que se pueden recuperar por separado. |
| **Embeddings** | Representa cada fragmento mediante un vector numérico que permite buscar contenido semánticamente parecido. |
| **Base vectorial** | Almacena los vectores y permite recuperar fragmentos cercanos a una consulta. |
| **Generación** | Un modelo redacta una respuesta utilizando los fragmentos recuperados como contexto. |

![Diagrama del flujo de ingesta y consulta de un RAG](docs/images/rag-diagrama.png)

La **R** de RAG corresponde a *Retrieval* (recuperación); la **G**, a *Generation* (generación). En la fase de recuperación se buscan fragmentos relevantes. En la generación, el modelo utiliza el contexto recuperado para elaborar una respuesta.

La diferencia entre las tres implementaciones está en quién se encarga de estas piezas y cuánto control tiene el desarrollador sobre ellas.

## Las tres fases: el mismo patrón con diferentes niveles de abstracción

| Característica | Fase 1: Bedrock gestionado | Fase 2: componentes propios en AWS | Fase 3: fuera de AWS |
|---|---|---|---|
| **Enfoque** | Servicio gestionado; se probó la recuperación | Componentes conectados mediante código propio | Componentes conectados con LangChain |
| **Entorno** | Cuenta de AWS | Entorno temporal de laboratorio de AWS | Máquina local |
| **División de documentos** | Bedrock: configuración observada de 300 tokens y 20 % de traslape | Función propia: 500 caracteres y 100 de traslape | `RecursiveCharacterTextSplitter`: 500 caracteres y 100 de traslape |
| **Embeddings** | Gestionados por Bedrock; el modelo utilizado no quedó identificado en la consola | Titan Text Embeddings V2 | Gemini (`gemini-embedding-001`) |
| **Base vectorial** | Gestionada por Bedrock | ChromaDB local | ChromaDB local |
| **Generación** | No validada por un límite de cuota de la cuenta | Nova Lite mediante la API Converse | Gemini (`gemini-3.6-flash`) |
| **Orquestación** | Knowledge Bases y una Lambda que consulta mediante `Retrieve` | Código propio con `boto3` | Cadena de LangChain |

### ¿Qué cambia al pasar de una fase a otra?

**Fase 1 — Bedrock se encarga de la infraestructura de recuperación.**

La Knowledge Base gestiona el proceso de ingesta y la infraestructura de búsqueda vectorial. La Lambda consulta la información recuperada mediante la API `Retrieve`. En esta fase no se validó la generación de respuestas con la Knowledge Base.

**Fase 2 — las piezas quedan más visibles.**

El código controla la división de documentos, genera embeddings con Titan, almacena los vectores en ChromaDB y utiliza Nova Lite para generar las respuestas. Esto permite inspeccionar más directamente cómo se conectan los componentes.

**Fase 3 — el mismo patrón con otras herramientas.**

LangChain organiza el flujo, ChromaDB almacena los vectores y Gemini genera los embeddings y las respuestas. La aplicación se ejecuta localmente.

> Estas fases ilustran diferentes formas de construir un RAG; no son una comparación controlada de rendimiento. En la Fase 3 cambiaron tanto el proveedor de modelos como el framework de orquestación.

## Hallazgos y limitaciones

- **No medí costos, latencia ni calidad de respuestas** mediante una evaluación sistemática. El proyecto no permite concluir qué implementación es más rápida, barata o precisa.
- La comparación no está controlada: en la Fase 3 cambiaron al mismo tiempo el proveedor de modelos y el framework.
- Se utilizaron solo **tres documentos cortos**. Con una colección tan pequeña, la búsqueda puede devolver una gran parte de los fragmentos disponibles; el contexto final depende de la lógica de la aplicación.
- En la Fase 1, la generación con Bedrock no pudo validarse debido a un error `ThrottlingException` asociado a la cuota diaria de tokens de la cuenta utilizada. Esto no demuestra una limitación general de Bedrock.
- En la Fase 3, las distancias de recuperación de dos preguntas fueron distintas, pero no se validó un umbral de relevancia con un conjunto amplio de ejemplos.

Los resultados y las limitaciones específicos de cada implementación están documentados en sus respectivos README.

## ¿Qué necesitas para reproducir el proyecto?

| Fase | Requisitos principales | Consideraciones |
|---|---|---|
| **3. Fuera de AWS** | Python 3.10 o superior — probado con Python 3.13 — y una clave de API de Gemini | Ejecución local. Verifica las cuotas y condiciones vigentes de Gemini. |
| **2. Componentes propios en AWS** | Credenciales de AWS y acceso a Titan Text Embeddings V2 y Nova Lite en `us-east-1` | Los modelos y recursos utilizados pueden generar costos. Consulta los precios vigentes. |
| **1. Bedrock gestionado** | Cuenta de AWS, bucket de S3, Knowledge Base y Lambda con permisos adecuados | Los recursos pueden generar costos. Elimínalos al terminar y revisa la facturación. |

Si solo quieres explorar el flujo con una ejecución local, empieza por la **Fase 3**. Si quieres entender qué componentes gestiona Bedrock, empieza por la **Fase 1**.

## Cómo clonar y empezar

Para ejecutar la Fase 3, clona el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd autospec-voice-assistant-rag/phase3-code-first-rag
```

Reemplaza `<URL_DEL_REPOSITORIO>` por la URL real de este repositorio.

### 1. Crear y activar un entorno virtual

Elige los comandos correspondientes a tu sistema:

| Sistema | Crear entorno | Activar entorno |
|---|---|---|
| Windows, Git Bash | `python -m venv .venv` | `source .venv/Scripts/activate` |
| Windows, PowerShell | `python -m venv .venv` | `.venv\Scripts\Activate.ps1` |

Con el entorno activo, normalmente verás `(.venv)` al inicio de la línea de comandos.

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar la clave de Gemini

Desde la carpeta `phase3-code-first-rag`, crea el archivo `.env` a partir de la plantilla:

| Sistema | Comando |
|---|---|
| macOS / Linux / Git Bash | `cp .env.example .env` |
| PowerShell | `Copy-Item .env.example .env` |

Abre `.env` y reemplaza el valor de ejemplo por tu propia clave de Gemini. No compartas ni subas ese archivo al repositorio.

### 4. Continuar con la ingesta y la aplicación

Los pasos para construir la base vectorial, ejecutar la ingesta y arrancar Streamlit están en el [README de la Fase 3](phase3-code-first-rag/README.md).

## Seguridad

- **Nunca subas claves de API ni credenciales de AWS al repositorio.**
- La clave de Gemini se carga desde `phase3-code-first-rag/.env`, que debe estar excluido mediante `.gitignore`.
- No muestres claves durante grabaciones, capturas o sesiones de pantalla compartida.
- Si una clave se expone, revócala y genera otra. No reutilices una clave expuesta.
- Antes de publicar capturas, oculta el número de cuenta de AWS (*Account ID*) y cualquier otra información sensible.
- Comprueba que Git ignore tu archivo `.env` con:

  ```bash
  git check-ignore -v phase3-code-first-rag/.env
  ```

- En la Fase 1, el rol de Lambda utiliza el permiso `bedrock:Retrieve` sobre la Knowledge Base en lugar de conceder acceso completo a Bedrock.
- Los recursos de AWS pueden generar costos. Elimínalos cuando ya no los necesites.

Durante la charla se mostró brevemente cómo se configura `.env` y la clave que se utilizó fue eliminada posteriormente en Google AI Studio. Este repositorio no incluye esa clave. Si alguna vez muestras una clave por accidente, revócala; no basta con borrarla del código o de una captura.

## Estructura del repositorio

```text
.
├── README.md
├── .gitignore
├── docs/
│   └── images/
│       ├── banner-codeon2026.png
│       ├── rag-diagrama.png
│       ├── cierre-codeon2026.png
│       ├── phase1/
│       ├── phase2/
│       └── phase3/
├── phase1-direct-retrieval/
│   └── README.md
├── phase2-component-based-rag/
│   └── README.md
└── phase3-code-first-rag/
    ├── README.md
    ├── data/
    ├── ingest.py
    ├── rag_chain.py
    ├── app.py
    ├── requirements.txt
    └── .env.example
```

La estructura muestra los archivos principales del proyecto. Puede haber archivos adicionales en las carpetas de cada fase.

## Próximos pasos

- Ejecutar la implementación de la Fase 3 con LangChain y Amazon Bedrock para aislar mejor el efecto del proveedor.
- Evaluar más documentos y preguntas antes de establecer criterios de relevancia para los fragmentos recuperados.
- Medir costos y latencia con un procedimiento reproducible.

## Datos y alcance

Las fichas técnicas utilizadas son **ficticias** y se prepararon para las pruebas del proyecto. No deben utilizarse datos reales de clientes ni credenciales.

## Gracias por CodeOn 2026

Gracias a **Developer Student Clubs UTP** por el espacio para compartir este proyecto y seguir aprendiendo sobre AWS y RAG.