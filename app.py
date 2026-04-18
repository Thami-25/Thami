import streamlit as st
import pandas as pd
import requests
import io
from datetime import date, timedelta

SHEET_ID = "1ewXcWuiLOCtv609Y-xKKg-qQwOuu21Bq"
DIAS_PT = {0:"Segunda-feira",1:"Terça-feira",2:"Quarta-feira",3:"Quinta-feira",4:"Sexta-feira",5:"Sábado",6:"Domingo"}

st.set_page_config(page_title="Painel de Vendas", page_icon="📊", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding: 1rem 1rem 3rem; max-width: 500px; margin: auto; }
#MainMenu, footer, header { visibility: hidden; }
.topbar { background:#1A1A2E; border-radius:14px; padding:16px 18px 14px; margin-bottom:16px; color:#fff; }
.topbar .nome { font-size:18px; font-weight:600; }
.topbar .sub  { font-size:12px; color:#94A3B8; margin-top:3px; }
.metrics { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
.mbox { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:10px 12px; text-align:center; }
.mbox .val { font-size:22px; font-weight:600; color:#1A1A2E; }
.mbox .lbl { font-size:10px; color:#64748B; margin-top:2px; }
.mbox .sub2 { font-size:10px; color:#94A3B8; }
.mbox.alerta .val { color:#DC2626; }
.mbox.verde  .val { color:#16A34A; }
.mbox.amarelo .val { color:#D97706; }
.prog { height:4px; background:#E2E8F0; border-radius:2px; margin-top:6px; overflow:hidden; }
.progf { height:100%; border-radius:2px; }
.slbl { font-size:11px; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:.06em; margin:16px 0 8px; }
.card { background:#fff; border:1px solid #E2E8F0; border-radius:14px; padding:13px 14px; margin-bottom:9px; }
.card.dev { border-left:3px solid #DC2626; }
.card.sem-compra { border-left:3px solid #F59E0B; }
.cnome { font-size:13px; font-weight:600; color:#1A1A2E; margin-bottom:4px; line-height:1.3; }
.cinfo { font-size:11px; color:#94A3B8; margin-bottom:8px; }
.bdgs  { display:flex; gap:5px; flex-wrap:wrap; margin-bottom:8px; }
.bdg   { font-size:10px; font-weight:600; padding:3px 8px; border-radius:20px; }
.bdg.rupt0   { background:#DCFCE7; color:#166534; }
.bdg.rupt1   { background:#FEF3C7; color:#92400E; }
.bdg.rupt2   { background:#FFEDD5; color:#9A3412; }
.bdg.rupt3   { background:#FEE2E2; color:#991B1B; }
.bdg.devedor { background:#FEE2E2; color:#991B1B; }
.bdg.comprou { background:#DBEAFE; color:#1E40AF; }
.srow { display:flex; border-top:1px solid #F1F5F9; padding-top:8px; margin-top:4px; }
.st2  { flex:1; text-align:center; }
.stv  { font-size:15px; font-weight:600; color:#1A1A2E; }
.stl  { font-size:9px; color:#94A3B8; display:block; margin-bottom:2px; }
.stv.v { color:#16A34A; }
.stv.z { color:#94A3B8; }
.sel-nome { font-size:14px; font-weight:600; color:#1A1A2E; }
.sel-sub  { font-size:12px; color:#64748B; margin-top:2px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def semana_do_mes(d):
    return (d.day - 1) // 7 + 1

def visita_hoje(freq_str, semana):
    try:
        return semana in [int(x) for x in str(freq_str).strip().split()]
    except:
        return False

def safe_int(v):
    try: return int(float(str(v).replace(",",".")))
    except: return 0

def is_devedor(v):
    try:
        return float(str(v).replace("R$","").replace(".","").replace(",",".").strip()) > 0
    except:
        return str(v).lower().strip() in ["sim","s","yes","devedor"]

def badge_ruptura(rupt):
    rupt = str(rupt).strip()
    if not rupt or rupt in ["-","nan","","None"]:
        return '<span class="bdg rupt0">Sem ruptura</span>'
    mapa = {"c/ compra":"rupt0","c/compra":"rupt0","sem kv":"rupt0",
            "1 mês":"rupt1","1 mes":"rupt1",
            "2 meses":"rupt2","2 mês":"rupt2",
            "3 meses":"rupt3","4 meses":"rupt3","5 meses":"rupt3","6 meses":"rupt3","> 6":"rupt3","cliente novo":"rupt0"}
    cls = next((v for k,v in mapa.items() if k in rupt.lower()), "rupt2")
    return f'<span class="bdg {cls}">{rupt}</span>'

def calc_ruptura(dfv):
    total    = len(dfv)
    c_compra = len(dfv[dfv["_ruptura"].str.lower().str.contains("c/ compra|c/compra", na=False)])
    novo     = len(dfv[dfv["_ruptura"].str.lower().str.contains("cliente novo", na=False)])
    sem_kv   = len(dfv[dfv["_ruptura"].str.lower().str.contains("sem kv", na=False)])
    denom    = total - novo - sem_kv
    em_rupt  = max(0, total - c_compra - novo - sem_kv)
    pct      = round(em_rupt / denom * 100, 1) if denom > 0 else 0
    return total, em_rupt, pct

def cor_ruptura(pct):
    if pct >= 50: return "#DC2626"
    if pct >= 30: return "#D97706"
    return "#16A34A"

def cls_ruptura(pct):
    if pct >= 50: return "alerta"
    if pct >= 30: return "amarelo"
    return "verde"


# ── Carregamento de dados ─────────────────────────────────────────────────────
def achar_col(df, nomes):
    for n in nomes:
        for c in df.columns:
            if n.lower() in str(c).lower():
                return c
    return None

@st.cache_data(ttl=3600)
def carregar_roteiro():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
        r = requests.get(url, timeout=30)
        df = pd.read_excel(io.BytesIO(r.content), sheet_name="BASE ATIVA - ROTEIRIZADA", engine="openpyxl")
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all")

        col_id     = achar_col(df, ["customer nu","numero","número"]) or df.columns[0]
        col_nome   = achar_col(df, ["customer name","razao","razão","nome"]) or df.columns[1]
        col_bairro = achar_col(df, ["address line 4","bairro"]) or df.columns[3]
        col_cidade = achar_col(df, ["city","cidade"]) or df.columns[4]
        col_dia    = achar_col(df, ["dia da semana"])
        col_freq   = achar_col(df, ["frequencia","frequência"])
        col_vend   = achar_col(df, ["vendedor"])
        col_cancel = achar_col(df, ["cancelamento"])
        col_rupt   = achar_col(df, ["ruptura"])
        col_dev    = achar_col(df, ["devedor"])

        if col_cancel:
            df = df[df[col_cancel].astype(str).str.strip() == "Ativo"]

        df["_id"]       = df[col_id].astype(str).str.strip()
        df["_nome"]     = df[col_nome].astype(str).str.strip() if col_nome else ""
        df["_bairro"]   = df[col_bairro].astype(str).str.strip() if col_bairro else ""
        df["_cidade"]   = df[col_cidade].astype(str).str.strip() if col_cidade else ""
        df["_dia"]      = df[col_dia].astype(str).str.strip() if col_dia else ""
        df["_freq"]     = df[col_freq].astype(str).str.strip() if col_freq else "1 2 3 4"
        df["_vendedor"] = df[col_vend].astype(str).str.strip() if col_vend else ""
        df["_ruptura"]  = df[col_rupt].astype(str).str.strip() if col_rupt else ""
        df["_devedor"]  = df[col_dev].astype(str).str.strip() if col_dev else ""

        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=300)
def carregar_vendas():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
        r = requests.get(url, timeout=30)
        df = pd.read_excel(io.BytesIO(r.content), sheet_name="VENDAS", engine="openpyxl")
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all")

        col_id     = achar_col(df, ["customer nu","numero","número"]) or df.columns[0]
        col_status = achar_col(df, ["status"])
        col_cat    = achar_col(df, ["categoria","category"])
        col_caixas = achar_col(df, ["somadecaixas","caixas","qtd"])

        df["_id"]     = df[col_id].astype(str).str.strip()
        df["_status"] = df[col_status].astype(str).str.strip() if col_status else "VENDA"
        df["_cat"]    = df[col_cat].astype(str).str.strip().str.upper() if col_cat else ""
        df["_caixas"] = df[col_caixas].apply(safe_int) if col_caixas else 0

        df = df[df["_status"] == "VENDA"]

        resumo = {}
        for sid, grp in df.groupby("_id"):
            resumo[sid] = {
                "impulso": int(grp[grp["_cat"].str.contains("IMPULSO", na=False)]["_caixas"].sum()),
                "th":      int(grp[grp["_cat"].str.contains("TAKE HOME|TH", na=False)]["_caixas"].sum()),
                "comprou": True
            }
        return resumo, None
    except Exception as e:
        return {}, str(e)


# ── Estado da sessão ──────────────────────────────────────────────────────────
for k, v in [("tela","selecao"),("vend",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

hoje        = date.today()
dia_hoje    = DIAS_PT[hoje.weekday()]
semana_hoje = semana_do_mes(hoje)
ontem       = hoje - timedelta(days=1)
dia_ontem   = DIAS_PT[ontem.weekday()]
semana_ontem= semana_do_mes(ontem)

df_rot, erro_rot = carregar_roteiro()
vendas, erro_vend = carregar_vendas()

if erro_rot:
    st.error(f"Erro ao carregar roteiro: {erro_rot}")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# TELA 1 — SELEÇÃO
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.tela == "selecao":
    vendedores = sorted([v for v in df_rot["_vendedor"].dropna().unique() if v and v != "nan"])

    st.markdown(f"""
    <div class="topbar">
      <div class="nome">📊 Painel de Vendas</div>
      <div class="sub">{dia_hoje} · Semana {semana_hoje} do mês</div>
    </div>""", unsafe_allow_html=True)

    for v in vendedores:
        dfv = df_rot[df_rot["_vendedor"] == v]
        hoje_count = len(dfv[
            (dfv["_dia"] == dia_hoje) &
            dfv["_freq"].apply(lambda f: visita_hoje(f, semana_hoje))
        ])
        total, em_rupt, pct = calc_ruptura(dfv)
        cor = cor_ruptura(pct)

        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:14px 16px;margin-bottom:8px;">
              <div class="sel-nome">{v}</div>
              <div class="sel-sub">{hoje_count} visitas hoje · {total} clientes na carteira</div>
              <div style="margin-top:8px;display:flex;align-items:center;gap:8px;">
                <div style="flex:1;height:4px;background:#E2E8F0;border-radius:2px;overflow:hidden;">
                  <div style="width:{pct}%;height:100%;background:{cor};border-radius:2px;"></div>
                </div>
                <span style="font-size:12px;font-weight:600;color:{cor};">{pct}% ruptura</span>
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
            if st.button("Entrar", key=f"v_{v}"):
                st.session_state.vend = v
                st.session_state.tela = "painel"
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TELA 2 — PAINEL DO VENDEDOR
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.tela == "painel":
    vend = st.session_state.vend
    dfv  = df_rot[df_rot["_vendedor"] == vend].copy()

    clientes_hoje  = dfv[(dfv["_dia"]==dia_hoje)  & dfv["_freq"].apply(lambda f: visita_hoje(f, semana_hoje))]
    clientes_ontem = dfv[(dfv["_dia"]==dia_ontem) & dfv["_freq"].apply(lambda f: visita_hoje(f, semana_ontem))]

    todos_ids  = set(dfv["_id"].tolist())
    imp_total  = sum(vendas.get(i,{}).get("impulso",0) for i in todos_ids)
    th_total   = sum(vendas.get(i,{}).get("th",0) for i in todos_ids)
    n_dev      = len(dfv[dfv["_devedor"].apply(is_devedor)])
    total, em_rupt, pct_rupt = calc_ruptura(dfv)
    cor = cor_ruptura(pct_rupt)
    cls = cls_ruptura(pct_rupt)

    st.markdown(f"""
    <div class="topbar">
      <div class="nome">{vend}</div>
      <div class="sub">{len(clientes_hoje)} visitas hoje · Semana {semana_hoje} · Ruptura: {pct_rupt}%</div>
    </div>
    <div class="metrics">
      <div class="mbox {'verde' if imp_total>0 else 'alerta'}">
        <div class="lbl">Impulso mês</div>
        <div class="val">{imp_total}</div>
        <div class="sub2">caixas vendidas</div>
      </div>
      <div class="mbox {'verde' if th_total>0 else 'alerta'}">
        <div class="lbl">Take Home mês</div>
        <div class="val">{th_total}</div>
        <div class="sub2">caixas vendidas</div>
      </div>
      <div class="mbox {cls}">
        <div class="lbl">% Ruptura</div>
        <div class="val" style="color:{cor};">{pct_rupt}%</div>
        <div class="sub2">{em_rupt} de {total} clientes</div>
        <div class="prog"><div class="progf" style="width:{pct_rupt}%;background:{cor};"></div></div>
      </div>
      <div class="mbox {'alerta' if n_dev>0 else 'verde'}">
        <div class="lbl">Devedores</div>
        <div class="val">{n_dev}</div>
        <div class="sub2">clientes</div>
      </div>
    </div>""", unsafe_allow_html=True)

    def render_clientes(df_lista, label):
        st.markdown(f'<div class="slbl">{label} · {len(df_lista)} clientes</div>', unsafe_allow_html=True)
        if df_lista.empty:
            st.info("Nenhuma visita programada.")
            return
        for _, row in df_lista.iterrows():
            sid    = row["_id"]
            nome   = row["_nome"]
            bairro = row["_bairro"]
            cidade = row["_cidade"]
            rupt   = row["_ruptura"]
            dev    = row["_devedor"]
            vd     = vendas.get(sid, {})
            imp    = vd.get("impulso", 0)
            th     = vd.get("th", 0)
            comprou= vd.get("comprou", False)

            dev_ok  = is_devedor(dev)
            card_cls = "card dev" if dev_ok else ("card sem-compra" if not comprou else "card")
            try:
                val_dev = float(str(dev).replace("R$","").replace(".","").replace(",",".").strip())
                dev_txt = f"Devedor: R$ {val_dev:,.2f}".replace(",","X").replace(".",",").replace("X",".") if val_dev > 0 else "Devedor"
            except:
                dev_txt = "Devedor"
            dev_bdg  = f'<span class="bdg devedor">{dev_txt}</span>' if dev_ok else ""
            comp_bdg = '<span class="bdg comprou">Comprou este mês</span>' if comprou else ""
            imp_cls  = "stv v" if imp > 0 else "stv z"
            th_cls   = "stv v" if th  > 0 else "stv z"

            st.markdown(f"""
<div class="{card_cls}">
  <div class="cnome">{nome}</div>
  <div class="cinfo">{bairro} · {cidade} · #{sid}</div>
  <div class="bdgs">{badge_ruptura(rupt)}{dev_bdg}{comp_bdg}</div>
  <div class="srow">
    <div class="st2"><span class="stl">Impulso mês</span><span class="{imp_cls}">{imp} cx</span></div>
    <div class="st2"><span class="stl">Take Home mês</span><span class="{th_cls}">{th} cx</span></div>
  </div>
</div>""", unsafe_allow_html=True)

    aba_hoje, aba_ontem, aba_semana = st.tabs(["Hoje", "Ontem", "Semana toda"])

    with aba_hoje:
        render_clientes(clientes_hoje, f"Roteiro de hoje · {dia_hoje}")

    with aba_ontem:
        render_clientes(clientes_ontem, f"Ontem · {dia_ontem}")

    with aba_semana:
        dias_ordem = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado","Domingo"]
        for dia in dias_ordem:
            sem = semana_hoje
            cl  = dfv[(dfv["_dia"]==dia) & dfv["_freq"].apply(lambda f: visita_hoje(f, sem))]
            if not cl.empty:
                render_clientes(cl, dia)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Trocar vendedor"):
            st.session_state.tela = "selecao"
            st.rerun()
    with col2:
        if st.button("🔄 Atualizar dados"):
            st.cache_data.clear()
            st.rerun()
