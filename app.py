import streamlit as st
import pandas as pd

SHEET_ID = "1GcY24pOk2wu1GwUNZojGiiL6INeMGNTh"
SHEET_NAME = "PAINEL"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

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
.prog { height:4px; background:#E2E8F0; border-radius:2px; margin-top:6px; overflow:hidden; }
.progf { height:100%; border-radius:2px; }
.slbl { font-size:11px; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:.06em; margin:16px 0 8px; }
.card { background:#fff; border:1px solid #E2E8F0; border-radius:14px; padding:13px 14px; margin-bottom:9px; }
.card.dev { border-left:3px solid #DC2626; }
.cnome { font-size:13px; font-weight:600; color:#1A1A2E; margin-bottom:8px; line-height:1.3; }
.bdgs  { display:flex; gap:5px; flex-wrap:wrap; margin-bottom:8px; }
.bdg   { font-size:10px; font-weight:600; padding:3px 8px; border-radius:20px; }
.bdg.compra { background:#DBEAFE; color:#1E40AF; }
.bdg.mes1   { background:#FEF3C7; color:#92400E; }
.bdg.mes2   { background:#FFEDD5; color:#9A3412; }
.bdg.mes3   { background:#FEE2E2; color:#991B1B; }
.bdg.novo   { background:#EDE9FE; color:#5B21B6; }
.bdg.semkv  { background:#F1F5F9; color:#475569; border:1px solid #CBD5E1; }
.bdg.rupt   { background:#FEE2E2; color:#991B1B; }
.srow { display:flex; border-top:1px solid #F1F5F9; padding-top:8px; }
.st2  { flex:1; text-align:center; }
.stv  { font-size:14px; font-weight:600; color:#1A1A2E; }
.stl  { font-size:9px; color:#94A3B8; display:block; margin-bottom:2px; }
.stv.v { color:#16A34A; }
.stv.r { color:#DC2626; }
.frow { display:flex; justify-content:space-between; align-items:center; border-top:1px solid #F1F5F9; padding-top:8px; margin-top:6px; font-size:11px; color:#64748B; flex-wrap:wrap; gap:4px; }
.dval { color:#DC2626; font-weight:600; }
.psim { color:#16A34A; font-weight:600; }
.pnao { color:#DC2626; font-weight:600; }
.tbdg { font-size:10px; padding:2px 8px; background:#F1F5F9; border-radius:20px; color:#475569; font-weight:600; }
.sel-nome { font-size:14px; font-weight:600; color:#1A1A2E; }
.sel-sub  { font-size:12px; color:#64748B; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

def safe_int(v):
    try: return int(float(str(v).replace(",",".")))
    except: return 0

def safe_float(v):
    try: return float(str(v).replace("R$","").replace(".","").replace(",",".").strip())
    except: return 0.0

def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    for c in df.columns:
        for cand in candidates:
            if cand.lower() in c.lower():
                return c
    return None

def badge_ruptura(tipo):
    tipo = str(tipo).strip()
    mapa = {"1 Mês":"mes1","2 Meses":"mes2","3 Meses":"mes3",
            "C/ Compra":"compra","SEM KV":"semkv","Cliente Novo":"novo"}
    return f'<span class="bdg {mapa.get(tipo,"semkv")}">{tipo}</span>'

def sv(v):
    return "stv r" if v > 0 else ("stv v" if v < 0 else "stv")

def pbar(pct, cor):
    p = min(max(pct,0),100)
    return f'<div class="prog"><div class="progf" style="width:{p:.0f}%;background:{cor};"></div></div>'

def card_html(row, cols):
    dev  = safe_float(row.get(cols["devedor"],"")) if cols["devedor"] else 0
    pic  = str(row.get(cols["picole"],"Não")).strip() if cols["picole"] else "Não"
    tipo = str(row.get(cols["contrato"],"")).strip() if cols["contrato"] else ""
    rupt = str(row.get(cols["ruptura"],"")).strip() if cols["ruptura"] else ""
    nome = str(row.get(cols["nome"],"")).strip() if cols["nome"] else ""
    io_  = safe_int(row.get(cols["imp_obj"],0)) if cols["imp_obj"] else 0
    ir   = safe_int(row.get(cols["imp_real"],0)) if cols["imp_real"] else 0
    iab  = io_ - ir
    to_  = safe_int(row.get(cols["th_obj"],0)) if cols["th_obj"] else 0
    tr   = safe_int(row.get(cols["th_real"],0)) if cols["th_real"] else 0
    rupt_b = '<span class="bdg rupt">Ruptura</span>' if iab > 0 else ""
    pic_h  = f'Picolé: <span class="psim">vendido</span>' if pic=="Sim" else f'Picolé: <span class="pnao">não vendido</span>'
    dev_h  = f'<br><span class="dval">Devedor: R$ {dev:,.2f}</span>' if dev > 0 else ""
    return f"""
<div class="{'card dev' if dev>0 else 'card'}">
  <div class="cnome">{nome}</div>
  <div class="bdgs">{badge_ruptura(rupt)}{rupt_b}</div>
  <div class="srow">
    <div class="st2"><span class="stl">Impulso obj.</span><span class="stv">{io_}</span></div>
    <div class="st2"><span class="stl">Realizado</span><span class="{sv(-ir) if ir>0 else 'stv'}">{ir}</span></div>
    <div class="st2"><span class="stl">Em aberto</span><span class="{sv(iab)}">{iab}</span></div>
  </div>
  <div class="srow" style="margin-top:4px;">
    <div class="st2"><span class="stl">TH obj.</span><span class="stv">{to_}</span></div>
    <div class="st2"><span class="stl">TH real.</span><span class="{sv(-tr) if tr>0 else 'stv'}">{tr}</span></div>
    <div class="st2"><span class="stl">TH aberto</span><span class="{sv(to_-tr)}">{to_-tr}</span></div>
  </div>
  <div class="frow">
    <div>{pic_h}{dev_h}</div>
    <span class="tbdg">{tipo}</span>
  </div>
</div>"""

@st.cache_data(ttl=300)
def carregar_dados():
    try:
        df = pd.read_csv(URL)
        # Limpa nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]
        # Remove linhas completamente vazias
        df = df.dropna(how="all")
        # Usa a primeira coluna como chave (independente do nome)
        col_id = df.columns[0]
        df = df[df[col_id].astype(str).str.strip().str.len() > 2]
        df[col_id] = df[col_id].astype(str).str.strip()
        # Mapeia colunas de forma flexível
        cols = {
            "id":       col_id,
            "vendedor": find_col(df, ["Vendedor"]),
            "data":     find_col(df, ["Data Visita", "Data"]),
            "nome":     find_col(df, ["Nome Cliente", "Nome do Cliente", "Razão Social"]),
            "ruptura":  find_col(df, ["Ruptura (tipo)", "Ruptura"]),
            "contrato": find_col(df, ["Tipo Contrato", "Tipo de Contrato"]),
            "imp_obj":  find_col(df, ["Impulso Obj.", "Impulso Objetivo"]),
            "imp_real": find_col(df, ["Impulso Real.", "Impulso Realizado"]),
            "th_obj":   find_col(df, ["TH Obj.", "Take Home Obj"]),
            "th_real":  find_col(df, ["TH Real.", "Take Home Real"]),
            "devedor":  find_col(df, ["Devedor Valor R$", "Devedor"]),
            "picole":   find_col(df, ["Picolé Campanha", "Picole"]),
        }
        return df, cols, None
    except Exception as e:
        return None, None, str(e)

for k, v in [("tela","selecao"),("vendedor",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

df, cols, erro = carregar_dados()

if erro or df is None:
    st.markdown('<div class="topbar"><div class="nome">📊 Painel de Vendas</div><div class="sub">Erro ao carregar dados</div></div>', unsafe_allow_html=True)
    st.error(f"Não foi possível carregar os dados.\n\nErro: {erro}")
    if st.button("🔄 Tentar novamente"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

col_vend = cols["vendedor"]
col_data = cols["data"]

if st.session_state.tela == "selecao":
    vendedores = sorted(df[col_vend].dropna().unique().tolist()) if col_vend else []
    st.markdown('<div class="topbar"><div class="nome">📊 Painel de Vendas</div><div class="sub">Selecione seu nome para continuar</div></div>', unsafe_allow_html=True)
    for v in vendedores:
        dfv = df[df[col_vend] == v]
        n   = len(dfv)
        io_col  = cols["imp_obj"]
        ir_col  = cols["imp_real"]
        nr = int((dfv[io_col].fillna(0).astype(float) > dfv[ir_col].fillna(0).astype(float)).sum()) if (io_col and ir_col) else 0
        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:14px 16px;margin-bottom:8px;"><div class="sel-nome">{v}</div><div class="sel-sub">{n} clientes · {nr} rupturas</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
            if st.button("Entrar", key=f"v_{v}"):
                st.session_state.vendedor = v
                st.session_state.tela = "painel"
                st.rerun()

elif st.session_state.tela == "painel":
    vend = st.session_state.vendedor
    dfv  = df[df[col_vend] == vend].copy() if col_vend else df.copy()

    datas    = sorted(dfv[col_data].dropna().unique()) if col_data else []
    hoje_dt  = datas[-1] if len(datas) >= 1 else None
    ontem_dt = datas[-2] if len(datas) >= 2 else None
    df_hoje  = dfv[dfv[col_data] == hoje_dt]  if hoje_dt  else dfv.iloc[0:0]
    df_ontem = dfv[dfv[col_data] == ontem_dt] if ontem_dt else dfv.iloc[0:0]

    io_col = cols["imp_obj"]; ir_col = cols["imp_real"]
    to_col = cols["th_obj"];  tr_col = cols["th_real"]
    imp_obj  = dfv[io_col].fillna(0).astype(float).sum() if io_col else 0
    imp_real = dfv[ir_col].fillna(0).astype(float).sum() if ir_col else 0
    th_obj   = dfv[to_col].fillna(0).astype(float).sum() if to_col else 0
    th_real  = dfv[tr_col].fillna(0).astype(float).sum() if tr_col else 0
    pct_imp  = (imp_real/imp_obj*100) if imp_obj > 0 else 0
    pct_th   = (th_real/th_obj*100)   if th_obj  > 0 else 0
    n_rupt   = int((dfv[io_col].fillna(0).astype(float) > dfv[ir_col].fillna(0).astype(float)).sum()) if (io_col and ir_col) else 0
    pic_col  = cols["picole"]
    dev_col  = cols["devedor"]
    picoles  = int((dfv[pic_col].fillna("Não").str.strip() == "Sim").sum()) if pic_col else 0
    devedores= dfv[dfv[dev_col].fillna(0).astype(float) > 0] if dev_col else dfv.iloc[0:0]

    ci = "verde" if pct_imp >= 75 else "alerta"
    ct = "verde" if pct_th  >= 75 else "alerta"
    ci_cor = "#1D9E75" if pct_imp >= 75 else "#DC2626"
    ct_cor = "#1D9E75" if pct_th  >= 75 else "#DC2626"

    st.markdown(f"""
    <div class="topbar"><div class="nome">{vend}</div><div class="sub">{len(df_hoje)} visitas hoje · {n_rupt} rupturas em aberto</div></div>
    <div class="metrics">
      <div class="mbox {ci}"><div class="lbl">Impulso</div><div class="val">{pct_imp:.0f}%</div><div class="sub2">{imp_real:.0f} / {imp_obj:.0f} cx</div>{pbar(pct_imp,ci_cor)}</div>
      <div class="mbox {ct}"><div class="lbl">Take Home</div><div class="val">{pct_th:.0f}%</div><div class="sub2">{th_real:.0f} / {th_obj:.0f} cx</div>{pbar(pct_th,ct_cor)}</div>
      <div class="mbox {'alerta' if n_rupt>0 else 'verde'}"><div class="lbl">Rupturas</div><div class="val">{n_rupt}</div><div class="sub2">em aberto</div></div>
      <div class="mbox"><div class="lbl">Picolé campanha</div><div class="val">{picoles}</div><div class="sub2">de {len(dfv)} clientes</div></div>
    </div>""", unsafe_allow_html=True)

    if len(devedores) > 0:
        total_dev = devedores[dev_col].astype(float).sum()
        st.warning(f"⚠️ {len(devedores)} cliente(s) devedor(es) — Total: R$ {total_dev:,.2f}")

    aba_hoje, aba_ontem, aba_resumo = st.tabs(["Hoje", "Ontem", "Resumo"])
    with aba_hoje:
        st.markdown(f'<div class="slbl">Roteiro do dia · {len(df_hoje)} clientes</div>', unsafe_allow_html=True)
        for _, row in df_hoje.iterrows():
            st.markdown(card_html(row, cols), unsafe_allow_html=True)
        if df_hoje.empty:
            st.info("Nenhuma visita registrada para hoje.")
    with aba_ontem:
        st.markdown(f'<div class="slbl">Visitas anteriores · {len(df_ontem)} clientes</div>', unsafe_allow_html=True)
        for _, row in df_ontem.iterrows():
            st.markdown(card_html(row, cols), unsafe_allow_html=True)
        if df_ontem.empty:
            st.info("Nenhuma visita anterior registrada.")
    with aba_resumo:
        st.markdown('<div class="slbl">Situação da carteira</div>', unsafe_allow_html=True)
        rupt_col = cols["ruptura"]
        if rupt_col:
            for tipo, qtd in dfv[rupt_col].fillna("Sem info").value_counts().items():
                st.markdown(f'<div class="card" style="margin-bottom:7px;"><div style="display:flex;justify-content:space-between;font-size:13px;"><span style="color:#64748B;">{tipo}</span><span style="font-weight:600;">{qtd}</span></div></div>', unsafe_allow_html=True)
        if len(devedores) > 0:
            st.markdown('<div class="slbl">Devedores</div>', unsafe_allow_html=True)
            nome_col = cols["nome"]
            for _, row in devedores.iterrows():
                val = safe_float(row.get(dev_col,""))
                nm  = str(row.get(nome_col,"")) if nome_col else ""
                st.markdown(f'<div class="card dev" style="margin-bottom:7px;"><div style="display:flex;justify-content:space-between;font-size:13px;"><span style="font-weight:500;">{nm}</span><span class="dval">R$ {val:,.2f}</span></div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Trocar vendedor"):
            st.session_state.tela = "selecao"
            st.session_state.vendedor = None
            st.rerun()
    with col2:
        if st.button("🔄 Atualizar dados"):
            st.cache_data.clear()
            st.rerun()
