import streamlit as st
import pandas as pd
from datetime import date, timedelta

SHEET_ID = "1GcY24pOk2wu1GwUNZojGiiL6INeMGNTh"
URL_VENDAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VENDAS"

VENDEDORES = {
    "831-Vendedor 01_Logica MG": "Nicolas Passafaro",
    "832-Vendedor 02_Logica MG": "Anderson Rodrigues da Silva",
    "833-Vendedor 03_Logica MG": "Lucimara De Fatima Sabino",
    "834-Vendedor 04_Logica MG": "Valeria Santos Nascimento",
    "835-Vendedor 05_Logica MG": "Thiago Sousa e Silva",
    "836-Vendedor 06_Logica MG": "Walmir Lino De Sousa",
    "867-Vendedor 07_Logica MG": "Alexandre Passafaro",
    "868-Vendedor 08_Logica MG": "Elton Carneiro",
    "917-ADM_Logica MG": "ADM_Logica MG",
}

DIAS_PT = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
    3: "Quinta-feira",  4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
}

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
.cnome { font-size:13px; font-weight:600; color:#1A1A2E; margin-bottom:6px; line-height:1.3; }
.cinfo { font-size:11px; color:#64748B; margin-bottom:8px; }
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
.sem-dados { text-align:center; padding:32px 16px; color:#94A3B8; font-size:13px; }
</style>
""", unsafe_allow_html=True)

def safe_int(v):
    try: return int(float(str(v).replace(",",".")))
    except: return 0

def safe_float(v):
    try: return float(str(v).replace("R$","").replace(".","").replace(",",".").strip())
    except: return 0.0

def semana_do_mes(d):
    return (d.day - 1) // 7 + 1

def cliente_visita_hoje(freq_str, dia_hoje, semana_hoje):
    try:
        semanas = [int(x) for x in str(freq_str).strip().split()]
        return semana_hoje in semanas
    except:
        return False

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

def card_cliente(row_rot, row_vend=None):
    nome = str(row_rot.get("Razão Social","")).strip()
    cidade = str(row_rot.get("Cidade","")).strip()
    bairro = str(row_rot.get("Bairro","")).strip()
    sold = str(row_rot.get("Sold","")).strip()

    if row_vend is not None:
        dev  = safe_float(row_vend.get("Devedor Valor R$",""))
        pic  = str(row_vend.get("Picolé Campanha","Não")).strip()
        tipo = str(row_vend.get("Tipo Contrato","")).strip()
        rupt = str(row_vend.get("Ruptura (tipo)","")).strip()
        io_  = safe_int(row_vend.get("Impulso Obj.",0))
        ir   = safe_int(row_vend.get("Impulso Real.",0))
        iab  = io_ - ir
        to_  = safe_int(row_vend.get("TH Obj.",0))
        tr   = safe_int(row_vend.get("TH Real.",0))
        tem_dados = True
    else:
        dev=0; pic="Não"; tipo=""; rupt=""; io_=0; ir=0; iab=0; to_=0; tr=0
        tem_dados = False

    rupt_b = '<span class="bdg rupt">Ruptura</span>' if iab > 0 else ""
    pic_h  = f'Picolé: <span class="psim">vendido</span>' if pic=="Sim" else f'Picolé: <span class="pnao">não vendido</span>'
    dev_h  = f'<br><span class="dval">Devedor: R$ {dev:,.2f}</span>' if dev > 0 else ""

    stats = f"""
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
  </div>""" if tem_dados else '<div class="sem-dados" style="padding:8px 0;font-size:11px;color:#94A3B8;">Sem dados de vendas esta semana</div>'

    return f"""
<div class="{'card dev' if dev>0 else 'card'}">
  <div class="cnome">{nome}</div>
  <div class="cinfo">{bairro} · {cidade} · Cód: {sold}</div>
  {'<div class="bdgs">' + badge_ruptura(rupt) + rupt_b + '</div>' if tem_dados else ''}
  {stats}
</div>"""

@st.cache_data(ttl=300)
def carregar_vendas():
    try:
        df = pd.read_csv(URL_VENDAS)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.dropna(how="all")
        col_id = df.columns[0]
        df = df[df[col_id].astype(str).str.strip().str.len() > 2]
        df[col_id] = df[col_id].astype(str).str.strip()
        return df, col_id, None
    except Exception as e:
        return None, None, str(e)

@st.cache_data(ttl=3600)
def carregar_roteiro():
    try:
        df = pd.read_excel("https://docs.google.com/spreadsheets/d/1ewXcWuiLOCtv609Y-xKKg-qQwOuu21Bq/export?format=xlsx&sheet=ROTEIRIZAÇÕES", engine="openpyxl")
        df.columns = df.columns.str.strip()
        df["Sold"] = df["Sold"].astype(str).str.strip()
        df["Vendedor"] = df["Vendedor"].str.strip()
        df["Dia da Semana"] = df["Dia da Semana"].str.strip()
        df["Frequência"] = df["Frequência"].astype(str).str.strip()
        df["Nome Vendedor"] = df["Vendedor"].map(lambda x: next((v for k,v in VENDEDORES.items() if k.strip() in x.strip()), x.strip()))
        return df, None
    except Exception as e:
        return None, str(e)

for k, v in [("tela","selecao"),("vendedor_codigo",None),("vendedor_nome",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

hoje = date.today()
dia_hoje = DIAS_PT[hoje.weekday()]
semana_hoje = semana_do_mes(hoje)

df_rot, erro_rot = carregar_roteiro()
df_vend, col_id_vend, erro_vend = carregar_vendas()

if erro_rot:
    st.error(f"Erro ao carregar roteiro: {erro_rot}")
    st.stop()

if st.session_state.tela == "selecao":
    st.markdown(f"""
    <div class="topbar">
      <div class="nome">📊 Painel de Vendas</div>
      <div class="sub">{dia_hoje} · Semana {semana_hoje} do mês</div>
    </div>
    """, unsafe_allow_html=True)

    vendedores_unicos = df_rot[["Vendedor","Nome Vendedor"]].drop_duplicates()

    for _, row in vendedores_unicos.iterrows():
        cod  = row["Vendedor"]
        nome = row["Nome Vendedor"]
        df_v = df_rot[df_rot["Vendedor"] == cod]
        clientes_hoje = df_v[
            (df_v["Dia da Semana"] == dia_hoje) &
            (df_v["Frequência"].apply(lambda f: cliente_visita_hoje(f, dia_hoje, semana_hoje)))
        ]
        n = len(clientes_hoje)
        col1, col2 = st.columns([5,1])
        with col1:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:14px 16px;margin-bottom:8px;">
              <div class="sel-nome">{nome}</div>
              <div class="sel-sub">{n} clientes hoje · {dia_hoje}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
            if st.button("Entrar", key=f"v_{cod}"):
                st.session_state.vendedor_codigo = cod
                st.session_state.vendedor_nome = nome
                st.session_state.tela = "painel"
                st.rerun()

elif st.session_state.tela == "painel":
    cod  = st.session_state.vendedor_codigo
    nome = st.session_state.vendedor_nome
    df_v = df_rot[df_rot["Vendedor"] == cod]

    clientes_hoje = df_v[
        (df_v["Dia da Semana"] == dia_hoje) &
        (df_v["Frequência"].apply(lambda f: cliente_visita_hoje(f, dia_hoje, semana_hoje)))
    ]
    ontem = hoje - timedelta(days=1)
    dia_ontem = DIAS_PT[ontem.weekday()]
    semana_ontem = semana_do_mes(ontem)
    clientes_ontem = df_v[
        (df_v["Dia da Semana"] == dia_ontem) &
        (df_v["Frequência"].apply(lambda f: cliente_visita_hoje(f, dia_ontem, semana_ontem)))
    ]

    todos_sold_hoje = set(clientes_hoje["Sold"].tolist())
    todos_sold = set(df_v["Sold"].tolist())

    if df_vend is not None:
        vend_map = {}
        for _, row in df_vend.iterrows():
            sid = str(row.get(col_id_vend,"")).strip()
            vend_map[sid] = row.to_dict()
    else:
        vend_map = {}

    imp_obj  = sum(safe_int(vend_map.get(s,{}).get("Impulso Obj.",0)) for s in todos_sold)
    imp_real = sum(safe_int(vend_map.get(s,{}).get("Impulso Real.",0)) for s in todos_sold)
    th_obj   = sum(safe_int(vend_map.get(s,{}).get("TH Obj.",0)) for s in todos_sold)
    th_real  = sum(safe_int(vend_map.get(s,{}).get("TH Real.",0)) for s in todos_sold)
    pct_imp  = (imp_real/imp_obj*100) if imp_obj > 0 else 0
    pct_th   = (th_real/th_obj*100)   if th_obj  > 0 else 0
    n_rupt   = sum(1 for s in todos_sold if safe_int(vend_map.get(s,{}).get("Impulso Obj.",0)) > safe_int(vend_map.get(s,{}).get("Impulso Real.",0)))
    picoles  = sum(1 for s in todos_sold if str(vend_map.get(s,{}).get("Picolé Campanha","Não")).strip()=="Sim")
    n_dev    = sum(1 for s in todos_sold if safe_float(vend_map.get(s,{}).get("Devedor Valor R$","")) > 0)
    total_dev= sum(safe_float(vend_map.get(s,{}).get("Devedor Valor R$","")) for s in todos_sold)

    ci = "verde" if pct_imp >= 75 else "alerta"
    ct = "verde" if pct_th  >= 75 else "alerta"
    ci_cor = "#1D9E75" if pct_imp >= 75 else "#DC2626"
    ct_cor = "#1D9E75" if pct_th  >= 75 else "#DC2626"

    st.markdown(f"""
    <div class="topbar">
      <div class="nome">{nome}</div>
      <div class="sub">{len(clientes_hoje)} clientes hoje · {dia_hoje} · Semana {semana_hoje}</div>
    </div>
    <div class="metrics">
      <div class="mbox {ci}"><div class="lbl">Impulso</div><div class="val">{pct_imp:.0f}%</div><div class="sub2">{imp_real} / {imp_obj} cx</div>{pbar(pct_imp,ci_cor)}</div>
      <div class="mbox {ct}"><div class="lbl">Take Home</div><div class="val">{pct_th:.0f}%</div><div class="sub2">{th_real} / {th_obj} cx</div>{pbar(pct_th,ct_cor)}</div>
      <div class="mbox {'alerta' if n_rupt>0 else 'verde'}"><div class="lbl">Rupturas</div><div class="val">{n_rupt}</div><div class="sub2">em aberto</div></div>
      <div class="mbox"><div class="lbl">Picolé campanha</div><div class="val">{picoles}</div><div class="sub2">de {len(todos_sold)} clientes</div></div>
    </div>
    """, unsafe_allow_html=True)

    if n_dev > 0:
        st.warning(f"⚠️ {n_dev} cliente(s) devedor(es) — Total: R$ {total_dev:,.2f}")

    aba_hoje, aba_ontem, aba_semana = st.tabs(["Hoje", "Ontem", "Semana toda"])

    with aba_hoje:
        st.markdown(f'<div class="slbl">Roteiro de hoje · {len(clientes_hoje)} clientes</div>', unsafe_allow_html=True)
        if clientes_hoje.empty:
            st.info(f"Nenhuma visita programada para {dia_hoje} semana {semana_hoje}.")
        for _, row in clientes_hoje.iterrows():
            sold = str(row["Sold"]).strip()
            st.markdown(card_cliente(row, vend_map.get(sold)), unsafe_allow_html=True)

    with aba_ontem:
        st.markdown(f'<div class="slbl">Ontem · {len(clientes_ontem)} clientes</div>', unsafe_allow_html=True)
        if clientes_ontem.empty:
            st.info("Nenhuma visita programada para ontem.")
        for _, row in clientes_ontem.iterrows():
            sold = str(row["Sold"]).strip()
            st.markdown(card_cliente(row, vend_map.get(sold)), unsafe_allow_html=True)

    with aba_semana:
        st.markdown(f'<div class="slbl">Todos os clientes da semana · {len(df_v)} na carteira</div>', unsafe_allow_html=True)
        dias_ordem = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado","Domingo"]
        for dia in dias_ordem:
            clientes_dia = df_v[
                (df_v["Dia da Semana"] == dia) &
                (df_v["Frequência"].apply(lambda f: cliente_visita_hoje(f, dia, semana_hoje)))
            ]
            if not clientes_dia.empty:
                st.markdown(f'<div class="slbl" style="margin-top:12px;">{dia} · {len(clientes_dia)} clientes</div>', unsafe_allow_html=True)
                for _, row in clientes_dia.iterrows():
                    sold = str(row["Sold"]).strip()
                    st.markdown(card_cliente(row, vend_map.get(sold)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Trocar vendedor"):
            st.session_state.tela = "selecao"
            st.rerun()
    with col2:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
