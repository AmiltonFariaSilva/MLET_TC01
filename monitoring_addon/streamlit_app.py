import time
import requests
import pandas as pd
import streamlit as st
from prometheus_client.parser import text_string_to_metric_families

st.set_page_config(page_title="API Monitoring Dashboard", layout="wide")
st.title("API Monitoring Dashboard")

api_base = st.sidebar.text_input("API base URL", "http://localhost:8000")
metrics_url = api_base.rstrip("/") + "/metrics"
refresh_sec = st.sidebar.slider("Refresh (seconds)", 5, 60, 10)

placeholder = st.empty()

def fetch_metrics(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        st.error(f"Erro ao buscar métricas: {e}")
        return None

def parse_prometheus(text):
    data = []
    if not text:
        return pd.DataFrame()
    for fam in text_string_to_metric_families(text):
        name = fam.name
        for s in fam.samples:
            metric = {
                "metric": s.name,
                "value": s.value,
                "labels": s.labels,
            }
            data.append(metric)
    return pd.DataFrame(data)

while True:
    with placeholder.container():
        st.subheader("Métricas cruas (Prometheus)")
        raw = fetch_metrics(metrics_url)
        if raw:
            df = parse_prometheus(raw)
            if not df.empty:
                st.dataframe(df)

                # Exemplos: latência e contadores padrão do Instrumentator
                # http_server_requests_seconds_count / sum / bucket, etc.
                latency = df[df["metric"].str.contains("http_server_requests_seconds_sum|_count")]
                if not latency.empty:
                    st.subheader("Resumo de requisições")
                    # Pivot rápido por método e status se disponível nas labels
                    try:
                        counts = df[df["metric"].str.endswith("_count")]
                        counts["status"] = counts["labels"].apply(lambda x: x.get("status", ""))
                        counts["method"] = counts["labels"].apply(lambda x: x.get("method", ""))
                        agg = counts.groupby(["method", "status"])["value"].sum().reset_index()
                        st.bar_chart(agg, x="status", y="value")
                    except Exception:
                        pass
            else:
                st.info("Sem métricas ainda. Faça algumas chamadas na API.")
    time.sleep(refresh_sec)