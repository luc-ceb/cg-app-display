# 🍦 Club Grido Intelligence — Data Analytics Hub

Tablero analítico interno para el programa de fidelización Club Grido.

## Estructura del Proyecto

```
club_grido/
├── .streamlit/
│   └── config.toml          # Theme oscuro con paleta Grido
├── data/
│   ├── dim_branch.parquet
│   ├── clientes_mapa.parquet
│   ├── clientes_supervivencia.parquet
│   ├── clientes_segmentacion.parquet
│   ├── forecast_ventas.parquet
│   └── clasificacion_encuestas.parquet
├── app.py                    # Aplicación principal
├── generate_data.py          # Generador de datos sintéticos
└── README.md
```

## Requisitos

```bash
pip install streamlit plotly pydeck pandas pyarrow
```

## Ejecución

```bash
cd club_grido
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

## 5 Tabs / Iniciativas

| Tab | Iniciativa | Modelo/Técnica |
|-----|-----------|----------------|
| 📍 Mapa de Clientes | Geolocalización de socios | pydeck ScatterplotLayer |
| 💓 Estado de Socios | Supervivencia / Abandono | BG/NBD - Poisson (P(alive)) |
| 🎯 Ocasión de Consumo | Segmentación por ocasión | MiniBatchKMeans + heurísticas |
| 📈 Forecast de Ventas | Predicción por producto | TFT / N-HiTS / LightGBM |
| 🧠 Tópicos NLP | Clasificación de encuestas | RoBERTa multi-label fine-tuned |

## Datos Reales

Para conectar datos reales, reemplazar los archivos `.parquet` en `data/`
manteniendo los mismos nombres de columnas. Ver `generate_data.py` como
referencia del schema esperado.

## Paleta de Colores

- Azul oscuro (fondo): `#092c73`
- Naranja (acento principal): `#ec7e04`
- Rosa (terciario): `#e54a82`
- Celeste (terciario): `#49c3fb`
