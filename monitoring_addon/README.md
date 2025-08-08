
# Add-on de Monitoramento & Analytics

Este pacote adiciona:
- **Logs estruturados** (JSON) de todas as chamadas (middleware).
- **Métricas Prometheus** da API em `/metrics`.
- **Dashboard simples (Streamlit)** que consome `/metrics`.


Rode:
```bash
streamlit run monitoring_addon/streamlit_app.py
```
No painel lateral, configure a URL da sua API (ex.: `http://localhost:8000`). O dashboard vai ler `/metrics` e mostrar tabelas e gráficos simples.

## 5) Arquivo principal detectado

Eu encontrei este possível ponto de entrada FastAPI no seu projeto:
`MLET_TC01/main.py`

> Se não for o correto, aplique as instruções no arquivo onde o objeto `FastAPI()` é criado.

## 6) Execução local

- Suba a API:
```bash
uvicorn MLET_TC01.main:app --reload
```

- Abra o dashboard:
```bash
streamlit run monitoring_addon/streamlit_app.py
```

## 7) Dicas

- Para enviar logs para um agregador (CloudWatch, Stackdriver, Loki), basta apontar o handler do `logging.json` para o destino desejado.
- Para métricas mais completas, configure rótulos customizados no Instrumentator e adicione **buckets** de histogramas conforme sua SLO.

