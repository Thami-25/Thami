import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Painel de Vendas",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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
.mbox .sub { font-size:10px; color:#94A3B8; }
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
    try: return int(float(v))
    except: return 0

def safe_float(v):
    try: return float(v)
    except: return 0.0

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

def card_html(row):
    dev   = safe_float(row.get("Devedor Valor R$",""))
    pic   = str(row.get("Picolé Campanha","Não")).strip()
    tipo  = str(row.get("Tipo Contrato","")).strip()
    rupt  = str(row.get("Ruptura (tipo)","")).strip()
    nome  = str(row.get("Nome Cliente","")).strip()
    io_   = safe_int(row.get("Impulso Obj.",0))
    ir    = safe_int(row.get("Impulso Real.",0))
    iab   = io_ - ir
    to_   = safe_int(row.get("TH Obj.",0))
    tr    = safe_int(row.get("TH Real.",0))
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

for k, v in [("tela","upload"),("df",None),("vendedor",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def carregar_excel(arq):
    try:
        df = pd.read_excel(arq, sheet_name="PAINEL", header=0, engine="openpyxl")
        df.columns = df.columns.str.strip()
        if "Código Cliente" not in df.columns:
            df = pd.read_excel(arq, sheet_name="PAINEL", header=1, engine="openpyxl")
            df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Código Cliente"])
        df = df[df["Código Cliente"].astype(str).str.strip() != ""]
        df["Código Cliente"] = df["Código Cliente"].astype(str).str.strip()
        return df, None
    except Exception as e:
        return None, str(e)

if st.session_state.tela == "upload":
    st.markdown("""
    <div class="topbar">
      <div class="nome">📊 Painel de Vendas</div>
      <div class="sub">Faça o upload do arquivo semanal para começar</div>
    </div>
    """, unsafe_allow_html=True)
    arq = st.file_uploader("Selecione o arquivo **Painel_de_Vendas.xlsx**", type=["xlsx"])
    if arq:
        df, erro = carregar_excel(arq)
        if erro:
            st.error(f"Erro ao ler o arquivo: {erro}")
        else:
            st.success(f"✅ {len(df)} registros carregados!")
            st.session_state.df = df
            if st.button("Continuar →"):
                st.session_state.tela = "selecao"
                st.rerun()

elif st.session_state.tela == "selecao":
    df = st.session_state.df
    vendedores = sorted(df["Vendedor"].dropna().unique().tolist())
    st.markdown("""
    <div class="topbar">
      <div class="nome">Olá! 👋</div>
      <div class="sub">Selecione seu nome para continuar</div>
    </div>
    """, unsafe_allow_html=True)
    for v in vendedores:
        dfv = df[df["Vendedor"] == v]
        n   = len(dfv)
        nr  = int((dfv["Impulso Obj."].fillna(0).astype(float) > dfv["Impulso Real."].fillna(0).astype(float)).sum())
        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:14px 16px;margin-bottom:8px;">
              <div class="sel-nome">{v}</div>
              <div class="sel-sub">{n} clientes · {nr} rupturas</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
            if st.button("Entrar", key=f"v_{v}"):
                st.session_state.vendedor = v
                st.session_state.tela = "painel"
                st.rerun()

elif st.session_state.tela == "painel":
    df_all = st.session_state.df
    vend   = st.session_state.vendedor
    df     = df_all[df_all["Vendedor"] == vend].copy()
    datas  = sorted(df["Data Visita"].dropna().unique())
    hoje_dt  = datas[-1] if len(datas) >= 1 else None
    ontem_dt = datas[-2] if len(datas) >= 2 else None
    df_hoje  = df[df["Data Visita"] == hoje_dt] if hoje_dt is not None else df.iloc[0:0]
    df_ontem = df[df["Data Visita"] == ontem_dt] if ontem_dt is not None else df.iloc[0:0]
    imp_obj  = df["Impulso Obj."].fillna(0).astype(float).sum()
    imp_real = df["Impulso Real."].fillna(0).astype(float).sum()
    th_obj   = df["TH Obj."].fillna(0).astype(float).sum()
    th_real  = df["TH Real."].fillna(0).astype(float).sum()
    pct_imp  = (imp_real/imp_obj*100) if imp_obj > 0 else 0
    pct_th   = (th_real/th_obj*100)   if th_obj  > 0 else 0
    n_rupt   = int((df["Impulso Obj."].fillna(0).astype(float) > df["Impulso Real."].fillna(0).astype(float)).sum())
    picoles  = int((df["Picolé Campanha"].fillna("Não").str.strip() == "Sim").sum())
    devedores= df[df["Devedor Valor R$"].fillna(0).astype(float) > 0]
    ci = "verde" if pct_imp >= 75 else "alerta"
    ct = "verde" if pct_th  >= 75 else "alerta"
    ci_cor = "#1D9E75" if pct_imp >= 75 else "#DC2626"
    ct_cor = "#1D9E75" if pct_th  >= 75 else "#DC2626"
    st.markdown(f"""
    <div class="topbar">
      <div class="nome">{vend}</div>
      <div class="sub">{len(df_hoje)} visitas hoje · {n_rupt} rupturas em aberto</div>
    </div>
    <div class="metrics">
      <div class="mbox {ci}">
        <div class="lbl">Impulso</div>
        <div class="val">{pct_imp:.0f}%</div>
        <div class="sub">{imp_real:.0f} / {imp_obj:.0f} cx</div>
        {pbar(pct_imp, ci_cor)}
      </div>
      <div class="mbox {ct}">
        <div class="lbl">Take Home</div>
        <div class="val">{pct_th:.0f}%</div>
        <div class="sub">{th_real:.0f} / {th_obj:.0f} cx</div>
        {pbar(pct_th, ct_cor)}
      </div>
      <div class="mbox {'alerta' if n_rupt>0 else 'verde'}">
        <div class="lbl">Rupturas</div>
        <div class="val">{n_rupt}</div>
        <div class="sub">em aberto</div>
      </div>
      <div class="mbox">
        <div class="lbl">Picolé campanha</div>
        <div class="val">{picoles}</div>
        <div class="sub">de {len(df)} clientes</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if len(devedores) > 0:
        total_dev = devedores["Devedor Valor R$"].astype(float).sum()
        st.warning(f"⚠️ {len(devedores)} cliente(s) devedor(es) — Total: R$ {total_dev:,.2f}")
    aba_hoje, aba_ontem, aba_resumo = st.tabs(["Hoje", "Ontem", "Resumo"])
    with aba_hoje:
        st.markdown(f'<div class="slbl">Roteiro do dia · {len(df_hoje)} clientes</div>', unsafe_allow_html=True)
        for _, row in df_hoje.iterrows():
            st.markdown(card_html(row), unsafe_allow_html=True)
        if df_hoje.empty:
            st.info("Nenhuma visita registrada para hoje.")
    with aba_ontem:
        st.markdown(f'<div class="slbl">Visitas anteriores · {len(df_ontem)} clientes</div>', unsafe_allow_html=True)
        for _, row in df_ontem.iterrows():
            st.markdown(card_html(row), unsafe_allow_html=True)
        if df_ontem.empty:
            st.info("Nenhuma visita anterior registrada.")
    with aba_resumo:
        st.markdown('<div class="slbl">Situação da carteira</div>', unsafe_allow_html=True)
        tipos = df["Ruptura (tipo)"].fillna("Sem info").value_counts()
        for tipo, qtd in tipos.items():
            st.markdown(f"""
            <div class="card" style="margin-bottom:7px;">
              <div style="display:flex;justify-content:space-between;align-items:center;font-size:13px;">
                <span style="color:#64748B;">{tipo}</span>
                <span style="font-weight:600;color:#1A1A2E;">{qtd}</span>
              </div>
            </div>""", unsafe_allow_html=True)
        if len(devedores) > 0:
            st.markdown('<div class="slbl">Devedores</div>', unsafe_allow_html=True)
            for _, row in devedores.iterrows():
                val = safe_float(row.get("Devedor Valor R$",""))
                st.markdown(f"""
                <div class="card dev" style="margin-bottom:7px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;font-size:13px;">
                    <span style="color:#1A1A2E;font-weight:500;">{row.get('Nome Cliente','')}</span>
                    <span class="dval">R$ {val:,.2f}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Trocar vendedor"):
        st.session_state.tela = "selecao"
        st.session_state.vendedor = None
        st.rerun()
