# 🍦 Club Grido Intelligence — Data Analytics Hub

Tablero analítico interno para el programa de fidelización Club Grido.

## Estructura del Proyecto

```
club_grido/
├── .streamlit/
│   └── config.toml          # Theme oscuro con paleta Grido
├── assets 
├── data/
│   ├── dim_branch.parquet
│   └── c_franquicias.parquet
├── app.py                    # Aplicación principal
├── requirements.txt
└── README.md
```

## Requisitos

```bash
pip install requirements.txt
```

## Ejecución

```bash
cd env
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

## 5 Tabs / Iniciativas

| Tab | Iniciativa | Modelo/Técnica |
|-----|-----------|----------------|
| 📍 Mapa de Clientes | Geolocalización de socios | pydeck ScatterplotLayer |
| 💓 Estado de Socios | Supervivencia / Abandono | BG/NBD - Poisson (P(alive)) |
| 🎯 Ocasión de Consumo | Segmentación por ocasión | MiniBatchKMeans + heurísticas |

## Datos Reales

Para conectar datos reales, reemplazar los archivos `.parquet` en `data/`
manteniendo los mismos nombres de columnas.

## Paleta de Colores

- Azul oscuro (fondo): `#092c73`
- Naranja (acento principal): `#ec7e04`
- Rosa (terciario): `#e54a82`
- Celeste (terciario): `#49c3fb`
