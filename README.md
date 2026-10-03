# Radar Tech

Agregador personal de noticias tech e IA/ML. Costo cero: GitHub Actions + GitHub Pages.

## Cómo funciona
- `feeds.json`: lista de fuentes (nombre, URL del RSS, categoría).
- `fetch_news.py`: lee los feeds, deduplica y escribe `docs/news.json`.
- `.github/workflows/radar.yml`: lo corre todos los días a las 7:00 am (Lima) y hace commit.
- `docs/index.html`: la web que lee `news.json`, con filtros y búsqueda.

## Puesta en marcha
1. Crea un repo en GitHub y sube esta carpeta.
2. En **Settings → Pages**, elige "Deploy from a branch", rama `main`, carpeta `/docs`.
3. En **Actions**, ejecuta "Actualizar radar" a mano la primera vez (Run workflow).
4. Tu radar queda en `https://<usuario>.github.io/<repo>/`.

## Agregar o quitar fuentes
Edita `feeds.json`. Categorías usadas por la web: `general` e `ia`.

## Probar en local
```bash
pip install -r requirements.txt
python fetch_news.py
python -m http.server -d docs 8000   # abrir http://localhost:8000
```
