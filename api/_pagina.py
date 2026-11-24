# Página do painel (HTML embutido: a Vercel entrega tudo para a função Python).
# Para mexer no visual, edite daqui para baixo.
PAGINA_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LATAM · Board Academy</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{--bg:#F6F7F9;--card:#FFFFFF;--line:#E3E6EC;--txt:#1F2A44;--muted:#6B7280;
        --azul:#3E5C8A;--azul2:#9DB0CC;--verde:#3C7D5A;--verm:#A94442;--amar:#B7862B;--cinza:#C9CED8}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--txt);font:14px/1.45 -apple-system,"Segoe UI",Roboto,Arial,sans-serif}
  header{background:var(--card);border-bottom:1px solid var(--line);padding:14px 24px;display:flex;
         flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:5}
  h1{font-size:18px;margin:0;font-weight:600;letter-spacing:.2px}
  h1 small{font-weight:400;color:var(--muted);margin-left:8px;font-size:13px}
  .ctl{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  select,button{font:inherit;color:var(--txt);background:#fff;border:1px solid var(--line);border-radius:6px;padding:6px 10px}
  button{cursor:pointer}
  .seg{display:inline-flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
  .seg button{border:0;border-radius:0;padding:6px 12px;background:#fff}
  .seg button.on{background:var(--txt);color:#fff}
  .tabs{display:flex;gap:4px;padding:0 24px;background:var(--card);border-bottom:1px solid var(--line)}
  .tab{padding:10px 16px;cursor:pointer;color:var(--muted);border-bottom:2px solid transparent}
  .tab.on{color:var(--txt);border-bottom-color:var(--txt);font-weight:600}
  main{padding:20px 24px 40px;max-width:1400px;margin:0 auto}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px;margin-bottom:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
  .card .k{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.4px}
  .card .v{font-size:22px;font-weight:600;margin-top:4px}
  .card .s{color:var(--muted);font-size:12px;margin-top:2px}
  .grid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
  @media(max-width:1000px){.grid2{grid-template-columns:1fr}}
  .box{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;margin-bottom:16px}
  .box h2{font-size:14px;margin:0 0 12px;font-weight:600}
  .box h2 small{font-weight:400;color:var(--muted);margin-left:6px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
  th:first-child,td:first-child{text-align:left}
  th{color:var(--muted);font-weight:500;font-size:12px;background:#FAFBFC}
  td.l,th.l{text-align:left}
  tr.tot td{font-weight:600;border-top:2px solid var(--line)}
  .scroll{overflow-x:auto;max-height:520px;overflow-y:auto}
  .pos{color:var(--verde)} .neg{color:var(--verm)} .mut{color:var(--muted)}
  .chip{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;margin:1px 2px;
        background:#F1F2F5;border:1px solid var(--line);color:var(--txt)}
  .chip.a{background:#FBF6EA;border-color:#E9D9B0;color:#7A5A16}
  .chip.r{background:#F8ECEC;border-color:#E6C7C7;color:#7E2E2E}
  .aviso{background:#FBF6EA;border:1px solid #E9D9B0;color:#6B4E12;border-radius:6px;padding:8px 12px;margin-bottom:14px;font-size:13px}
  .erro{background:#F8ECEC;border:1px solid #E6C7C7;color:#7E2E2E;border-radius:6px;padding:12px;white-space:pre-wrap}
  .na{color:var(--muted);font-style:italic;padding:8px 0}
  a{color:var(--azul);text-decoration:none} a:hover{text-decoration:underline}
  footer{color:var(--muted);font-size:11px;padding:10px 24px 24px;max-width:1400px;margin:0 auto}
  .load{color:var(--muted);padding:30px 0;text-align:center}
  canvas{max-height:300px}
</style>
</head>
<body>
<header>
  <h1>LATAM · Board Academy <small id="sub"></small></h1>
  <div class="ctl">
    <select id="selMes"></select>
    <select id="selAno"></select>
    <span class="seg" id="segValor">
      <button data-v="bruto" class="on" data-t="bruto"></button>
      <button data-v="mult" data-t="mult"></button>
    </span>
    <span class="seg" id="segLang">
      <button data-l="pt" class="on">PT</button>
      <button data-l="es">ES</button>
    </span>
    <button id="btnAtualizar" data-t="atualizar"></button>
  </div>
</header>
<div class="tabs">
  <div class="tab on" data-view="mes" data-t="tab_mes"></div>
  <div class="tab" data-view="graficos" data-t="tab_graf"></div>
  <div class="tab" data-view="forecast" data-t="tab_fc"></div>
</div>
<main id="conteudo"><div class="load">…</div></main>
<footer id="carimbo"></footer>

<script>
const T = {
 pt: {
  bruto:"Bruto", mult:"c/ Multiplicador", atualizar:"Atualizar", tab_mes:"Painel do Mês", tab_graf:"Gráficos", tab_fc:"Forecast",
  carregando:"Carregando…", meses:["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
  meta_mes:"Meta do mês", realizado:"Realizado", atingimento:"Atingimento", deveria:"Deveria estar (MTD)", gap:"Gap 100%",
  meta_dia_rest:"Meta/dia restante", previsto_hoje:"Previsto hoje", em_aberto_hoje:"Em aberto hoje", vendas:"Vendas",
  ticket:"Ticket médio (bruto)", metricas:"Métricas do mês", metrica:"Métrica", valor:"Valor",
  r_meta_mes:"Meta Mês", r_meta_dia:"Meta Dia", r_real_b:"Realizado Bruto", r_real_m:"Realizado c/ Multiplicador",
  r_deveria:"Deveria (100%) — MTD", r_pct_mtd:"% do MTD", r_ating:"Atingimento", r_gap:"Gap 100%", r_meta_dia_rest:"Meta/Dia 100%",
  r_prev_hoje:"Previsto hoje (20/50/70)", r_prev_ontem:"Previsto ontem", r_aberto:"Em aberto hoje", r_entrou_hoje:"Entrou hoje",
  r_entrou_ontem:"Entrou ontem", r_du:"Dias úteis (total · passados · restantes)",
  sem_foto:"sem foto do forecast", feriados:"Feriados do México no mês", nenhum_feriado:"Nenhum feriado no mês",
  por_closer:"Por Closer", nome:"Nome", meta:"Meta", qtd:"Qtd", ating:"Ating.", meta_mtd:"Meta MTD", pct_mtd:"% MTD",
  sem_meta:"sem meta", fora_time:"fora do time", total:"TOTAL",
  pendencias:"Pendências do forecast", pend_sub:"negócios abertos em negociação com algo mal preenchido",
  negocio:"Negócio", dono:"Dono", prob:"Prob.", prevista:"Data prevista", motivos:"Motivos", sem_pend:"Nenhuma pendência. 👏",
  m_sem_data_prevista:"Sem data prevista", m_data_vencida:"Data vencida", m_probabilidade:"Prob. fora de 20/50/70",
  m_sem_reuniao_recente:"Sem reunião há 15+ dias", m_data_empurrada:"Data empurrada 3+ vezes",
  lista_vendas:"Vendas do mês", produto:"Produto", data:"Data", indicacao:"Indicação", sem_vendas:"Nenhuma venda no período.",
  estoque_na:"Disponível só no mês corrente: deal aberto é estoque, não dá para ver como estava no passado.",
  aviso_fora:"{n} negócio(s) com data hoje e probabilidade fora de 20/50/70 ({v}) não entram no previsto.",
  aviso_latam_fc:"O funil LATAM não aparece no filtro do forecast: previsto e pendências podem vir zerados.",
  g_acum:"Meta × Realizado acumulado", g_meta:"Meta", g_vendas_dia:"Vendas por dia", g_reu:"Reuniões do time por dia",
  g_feitas:"Feitas", g_noshow:"No-show", g_agendadas:"Agendadas", g_perd:"Perdidos por dia", g_motivos:"Motivos de perda — top 10",
  g_prod:"Produtos vendidos", g_ind:"Venda de indicação", g_ind_sub:"(referido, pela tag do negócio)",
  combo:"Combo conta em mais de um produto quando o nome traz dois programas.",
  fc_resto:"Pipe do resto do mês", ponderado:"Ponderado", fc_7:"Próximos 7 dias", projecao:"Projeção do mês",
  proj_sub:"realizado + ponderado que falta", pct_meta:"% da meta", fora_mes:"Previstos para fora deste mês",
  vencidos:"Com data vencida (no filtro)", sem_data:"Sem data prevista — ficam fora do forecast", dia_a_dia:"De hoje até o fim do mês",
  em_aberto_col:"Em aberto", dia:"Dia", fc_deals:"Negócios no forecast deste mês", fc_bruto:"Forecast sempre em valor bruto (F1).",
  fc_na:"O forecast é estoque: só existe para o mês corrente.", erro:"Erro", feriado:"feriado"
 },
 es: {
  bruto:"Bruto", mult:"c/ Multiplicador", atualizar:"Actualizar", tab_mes:"Panel del Mes", tab_graf:"Gráficos", tab_fc:"Forecast",
  carregando:"Cargando…", meses:["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],
  meta_mes:"Meta del mes", realizado:"Realizado", atingimento:"Cumplimiento", deveria:"Debería estar (MTD)", gap:"Gap 100%",
  meta_dia_rest:"Meta/día restante", previsto_hoje:"Previsto hoy", em_aberto_hoje:"Abierto hoy", vendas:"Ventas",
  ticket:"Ticket promedio (bruto)", metricas:"Métricas del mes", metrica:"Métrica", valor:"Valor",
  r_meta_mes:"Meta Mes", r_meta_dia:"Meta Día", r_real_b:"Realizado Bruto", r_real_m:"Realizado c/ Multiplicador",
  r_deveria:"Debería (100%) — MTD", r_pct_mtd:"% del MTD", r_ating:"Cumplimiento", r_gap:"Gap 100%", r_meta_dia_rest:"Meta/Día 100%",
  r_prev_hoje:"Previsto hoy (20/50/70)", r_prev_ontem:"Previsto ayer", r_aberto:"Abierto hoy", r_entrou_hoje:"Entró hoy",
  r_entrou_ontem:"Entró ayer", r_du:"Días hábiles (total · pasados · restantes)",
  sem_foto:"sin foto del forecast", feriados:"Feriados de México en el mes", nenhum_feriado:"Ningún feriado en el mes",
  por_closer:"Por Closer", nome:"Nombre", meta:"Meta", qtd:"Cant.", ating:"Cumpl.", meta_mtd:"Meta MTD", pct_mtd:"% MTD",
  sem_meta:"sin meta", fora_time:"fuera del equipo", total:"TOTAL",
  pendencias:"Pendientes del forecast", pend_sub:"negocios abiertos en negociación con algo mal llenado",
  negocio:"Negocio", dono:"Dueño", prob:"Prob.", prevista:"Fecha prevista", motivos:"Motivos", sem_pend:"Ningún pendiente. 👏",
  m_sem_data_prevista:"Sin fecha prevista", m_data_vencida:"Fecha vencida", m_probabilidade:"Prob. fuera de 20/50/70",
  m_sem_reuniao_recente:"Sin reunión hace 15+ días", m_data_empurrada:"Fecha aplazada 3+ veces",
  lista_vendas:"Ventas del mes", produto:"Producto", data:"Fecha", indicacao:"Referido", sem_vendas:"Ninguna venta en el periodo.",
  estoque_na:"Disponible solo en el mes actual: el negocio abierto es inventario, no se puede ver cómo estaba en el pasado.",
  aviso_fora:"{n} negocio(s) con fecha hoy y probabilidad fuera de 20/50/70 ({v}) no entran en el previsto.",
  aviso_latam_fc:"El embudo LATAM no aparece en el filtro del forecast: previsto y pendientes pueden venir en cero.",
  g_acum:"Meta × Realizado acumulado", g_meta:"Meta", g_vendas_dia:"Ventas por día", g_reu:"Reuniones del equipo por día",
  g_feitas:"Realizadas", g_noshow:"No-show", g_agendadas:"Agendadas", g_perd:"Perdidos por día", g_motivos:"Motivos de pérdida — top 10",
  g_prod:"Productos vendidos", g_ind:"Venta de referido", g_ind_sub:"(por la etiqueta del negocio)",
  combo:"Un combo cuenta en más de un producto cuando el nombre trae dos programas.",
  fc_resto:"Pipe del resto del mes", ponderado:"Ponderado", fc_7:"Próximos 7 días", projecao:"Proyección del mes",
  proj_sub:"realizado + ponderado que falta", pct_meta:"% de la meta", fora_mes:"Previstos para fuera de este mes",
  vencidos:"Con fecha vencida (en el filtro)", sem_data:"Sin fecha prevista — quedan fuera del forecast", dia_a_dia:"De hoy al fin del mes",
  em_aberto_col:"Abierto", dia:"Día", fc_deals:"Negocios en el forecast de este mes", fc_bruto:"Forecast siempre en valor bruto (F1).",
  fc_na:"El forecast es inventario: solo existe para el mes actual.", erro:"Error", feriado:"feriado"
 }
};
const S = {lang: localGet("latam_lang","pt"), valor: localGet("latam_valor","bruto"), view:"mes", cache:{}, charts:[]};
const hoje = new Date();
function localGet(k,d){try{return localStorage.getItem(k)||d}catch(e){return d}}
function localSet(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function t(k){return (T[S.lang]||T.pt)[k] ?? k}
const loc = () => S.lang==="es" ? "es-MX" : "pt-BR";
function R(v){ if(v===null||v===undefined) return "—"; return new Intl.NumberFormat(loc(),{style:"currency",currency:"BRL",maximumFractionDigits:0}).format(v) }
function P(v){ if(v===null||v===undefined) return "—"; return new Intl.NumberFormat(loc(),{maximumFractionDigits:1}).format(v)+"%" }
function N(v){ if(v===null||v===undefined) return "—"; return new Intl.NumberFormat(loc()).format(v) }
function D(iso){ if(!iso) return "—"; const [a,m,d]=iso.split("-"); return `${d}/${m}` }
function esc(s){return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function cls(v){return v===null||v===undefined?"":(v<0?"neg":"pos")}

/* controles */
const selMes=document.getElementById("selMes"), selAno=document.getElementById("selAno");
for(let a=2024;a<=hoje.getFullYear()+1;a++){const o=document.createElement("option");o.value=a;o.textContent=a;selAno.appendChild(o)}
selAno.value=hoje.getFullYear();
function montarMeses(){const atual=selMes.value||String(hoje.getMonth()+1);selMes.innerHTML="";
  t("meses").forEach((n,i)=>{const o=document.createElement("option");o.value=i+1;o.textContent=n;selMes.appendChild(o)});selMes.value=atual}
function textos(){document.querySelectorAll("[data-t]").forEach(e=>e.textContent=t(e.dataset.t));montarMeses();document.documentElement.lang=loc()}
document.querySelectorAll("#segValor button").forEach(b=>b.onclick=()=>{S.valor=b.dataset.v;localSet("latam_valor",S.valor);marcar();render()});
document.querySelectorAll("#segLang button").forEach(b=>b.onclick=()=>{S.lang=b.dataset.l;localSet("latam_lang",S.lang);marcar();textos();render()});
document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{S.view=b.dataset.view;marcar();carregar()});
selMes.onchange=selAno.onchange=()=>carregar();
document.getElementById("btnAtualizar").onclick=()=>{S.cache={};carregar()};
function marcar(){
  document.querySelectorAll("#segValor button").forEach(b=>b.classList.toggle("on",b.dataset.v===S.valor));
  document.querySelectorAll("#segLang button").forEach(b=>b.classList.toggle("on",b.dataset.l===S.lang));
  document.querySelectorAll(".tab").forEach(b=>b.classList.toggle("on",b.dataset.view===S.view));
}

async function carregar(){
  const mes=selMes.value, ano=selAno.value, k=`${S.view}-${ano}-${mes}`;
  document.getElementById("sub").textContent=`${t("meses")[mes-1]} ${ano}`;
  if(!S.cache[k]){
    document.getElementById("conteudo").innerHTML=`<div class="load">${t("carregando")}</div>`;
    try{
      const r=await fetch(`/api/index?fmt=${S.view}&mes=${mes}&ano=${ano}`);
      const j=await r.json();
      if(j.erro){throw new Error(j.erro+(j.detalhe?"\n"+j.detalhe:"")+(j.trace?"\n\n"+j.trace:""))}
      S.cache[k]=j;
    }catch(e){document.getElementById("conteudo").innerHTML=`<div class="erro">${t("erro")}: ${esc(e.message)}</div>`;return}
  }
  render();
}
function render(){
  const k=`${S.view}-${selAno.value}-${selMes.value}`, d=S.cache[k];
  if(!d) return;
  S.charts.forEach(c=>c.destroy()); S.charts=[];
  const el=document.getElementById("conteudo");
  el.innerHTML = S.view==="mes"?viewMes(d):S.view==="graficos"?viewGraf(d):viewFc(d);
  if(S.view==="graficos") desenharGraf(d);
  if(S.view==="mes" && d.corrente) carregarPend();
  const val = S.valor==="bruto"?"bruto":"c/ multiplicador";
  document.getElementById("carimbo").textContent = (d.carimbo||"").replace(" · Meta:", ` · Valor: ${val} · Meta:`);
}

async function carregarPend(){
  const k=`pend-${selAno.value}-${selMes.value}`;
  if(!S.cache[k]){
    try{const j=await (await fetch(`/api/index?fmt=pendencias&mes=${selMes.value}&ano=${selAno.value}`)).json();
        if(j.erro) throw new Error(j.erro); S.cache[k]=j;}
    catch(e){const b=document.getElementById("pendBox"); if(b) b.innerHTML=`<div class="erro">${t("erro")}: ${esc(e.message)}</div>`; return}
  }
  const b=document.getElementById("pendBox"); if(b) b.innerHTML=tabPend(S.cache[k]);
}

/* ── Painel do Mês ── */
function viewMes(d){
  const b=d[S.valor], v=S.valor, du=d.du, pv=d.previsto;
  let h="";
  if(pv && pv.fora_faixa_qtd) h+=`<div class="aviso">${t("aviso_fora").replace("{n}",pv.fora_faixa_qtd).replace("{v}",R(pv.fora_faixa_valor))}</div>`;
  if(d.latam_no_forecast===false) h+=`<div class="aviso">${t("aviso_latam_fc")}</div>`;
  h+=`<div class="cards">
    ${card(t("meta_mes"),R(d.meta_mes),`${t("r_meta_dia")}: ${R(d.meta_dia)}`)}
    ${card(t("realizado"),R(b.realizado),`${N(d.vendas_qtd)} ${t("vendas").toLowerCase()}`)}
    ${card(t("atingimento"),P(b.atingimento),"")}
    ${card(t("deveria"),R(b.deveria_mtd),`${t("pct_mtd")}: ${P(b.pct_mtd)}`)}
    ${card(t("gap"),R(b.gap),"")}
    ${card(t("meta_dia_rest"),R(b.meta_dia_restante),`${du.restantes} DU`)}
    ${card(t("previsto_hoje"),pv?R(pv.hoje):"—",pv?`${t("em_aberto_hoje")}: ${R(pv.em_aberto)}`:t("sem_foto"))}
    ${card(t("ticket"),R(d.ticket_bruto),"")}
  </div>`;
  const e=d.entrou;
  const rows=[
    [t("r_meta_mes"),R(d.meta_mes)],[t("r_meta_dia"),R(d.meta_dia)],
    [t("r_real_b"),R(d.bruto.realizado)],[t("r_real_m"),R(d.mult.realizado)],
    [t("r_deveria"),R(b.deveria_mtd)],[t("r_pct_mtd"),P(b.pct_mtd)],[t("r_ating"),P(b.atingimento)],
    [t("r_gap"),R(b.gap)],[t("r_meta_dia_rest"),R(b.meta_dia_restante)],
    [t("r_prev_hoje"),pv?`${R(pv.hoje)} <span class="mut">(20%: ${R(pv.p20)} · 50%: ${R(pv.p50)} · 70%: ${R(pv.p70)})</span>`:"—"],
    [t("r_prev_ontem"),`— <span class="mut">(${t("sem_foto")})</span>`],
    [t("r_aberto"),pv?R(pv.em_aberto):"—"],
    [t("r_entrou_hoje"),d.corrente?`${R(e.hoje[v])} <span class="mut">(${e.hoje.qtd})</span>`:"—"],
    [t("r_entrou_ontem"),d.corrente?`${R(e.ontem[v])} <span class="mut">(${e.ontem.qtd} · ${D(e.ontem.data)})</span>`:"—"],
    [t("r_du"),`${du.total} · ${du.passados} · ${du.restantes}`]
  ];
  const fer = d.feriados.length? d.feriados.map(f=>`${D(f.data)} ${esc(f.nome)}`).join(" · ") : t("nenhum_feriado");
  h+=`<div class="grid2">
    <div class="box"><h2>${t("metricas")} <small>${t(S.valor)}</small></h2>
      <table><tr><th>${t("metrica")}</th><th>${t("valor")}</th></tr>
      ${rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td></tr>`).join("")}</table>
      <div class="mut" style="margin-top:10px;font-size:12px">${t("feriados")}: ${fer}</div></div>
    <div class="box"><h2>${t("por_closer")} <small>${t(S.valor)}</small></h2>${tabPessoas(d)}</div>
  </div>`;
  h+=`<div class="box"><h2>${t("pendencias")} <small>${t("pend_sub")}</small></h2><div id="pendBox">${d.corrente?`<div class="load">${t("carregando")}</div>`:`<div class="na">${t("estoque_na")}</div>`}</div></div>`;
  h+=`<div class="box"><h2>${t("lista_vendas")} <small>${N(d.vendas.length)}</small></h2>${tabVendas(d.vendas)}</div>`;
  return h;
}
function card(k,v,s){return `<div class="card"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${s||"&nbsp;"}</div></div>`}
function tabPessoas(d){
  const v=S.valor, at=v==="bruto"?"ating_bruto":"ating_mult", mt=v==="bruto"?"mtd_pct_bruto":"mtd_pct_mult";
  let tq=0,tr=0,tm=0;
  const linhas=d.pessoas.map(p=>{tq+=p.qtd;tr+=p[v]||0;tm+=p.meta||0;
    const tag=!p.no_time?` <span class="chip">${t("fora_time")}</span>`:(!p.meta?` <span class="chip">${t("sem_meta")}</span>`:"");
    return `<tr><td>${esc(p.nome)}${tag}</td><td>${R(p.meta)}</td><td>${N(p.qtd)}</td><td>${R(p[v])}</td><td>${P(p[at])}</td><td>${R(p.mtd_meta)}</td><td>${P(p[mt])}</td></tr>`}).join("");
  return `<div class="scroll"><table><tr><th>${t("nome")}</th><th>${t("meta")}</th><th>${t("qtd")}</th><th>${t("realizado")}</th><th>${t("ating")}</th><th>${t("meta_mtd")}</th><th>${t("pct_mtd")}</th></tr>
    ${linhas}<tr class="tot"><td>${t("total")}</td><td>${R(tm)}</td><td>${N(tq)}</td><td>${R(tr)}</td><td>${P(tm?tr/tm*100:null)}</td><td>${R(d[v].deveria_mtd)}</td><td>${P(d[v].pct_mtd)}</td></tr></table></div>`;
}
function tabPend(p){
  if(!p.disponivel) return `<div class="na">${t("estoque_na")}</div>`;
  const it=p.itens;
  if(!it.length) return `<div class="na">${t("sem_pend")}</div>`;
  return `<div class="scroll"><table><tr><th>${t("negocio")}</th><th class="l">${t("dono")}</th><th>${t("valor")}</th><th>${t("prob")}</th><th>${t("prevista")}</th><th class="l">${t("motivos")}</th></tr>
  ${it.map(i=>`<tr><td><a href="${i.link}" target="_blank">${esc(i.titulo)}</a></td><td class="l">${esc(i.dono)}</td><td>${R(i.valor)}</td><td>${i.prob??"—"}</td><td>${i.prevista?D(i.prevista):"—"}</td>
  <td class="l">${i.motivos.map(m=>`<span class="chip r">${t("m_"+m)}</span>`).join("")}${i.alertas.map(m=>`<span class="chip a">${t("m_"+m)}</span>`).join("")}</td></tr>`).join("")}</table></div>`;
}
function tabVendas(vs){
  if(!vs.length) return `<div class="na">${t("sem_vendas")}</div>`;
  return `<div class="scroll"><table><tr><th>${t("negocio")}</th><th class="l">${t("dono")}</th><th class="l">${t("produto")}</th><th>${t("bruto")}</th><th>${t("mult")}</th><th>${t("data")}</th><th>${t("indicacao")}</th></tr>
  ${vs.map(x=>`<tr><td><a href="${x.link}" target="_blank">${esc(x.titulo)}</a></td><td class="l">${esc(x.dono)}</td><td class="l">${esc(x.produto)}</td><td>${R(x.bruto)}</td><td>${R(x.mult)}</td><td>${D(x.data)}</td><td>${x.indicacao?"✓":""}</td></tr>`).join("")}</table></div>`;
}

/* ── Gráficos ── */
function viewGraf(d){
  const v=S.valor, i=d.indicacao;
  return `<div class="grid2">
    <div class="box"><h2>${t("g_acum")} <small>${t(v)}</small></h2><canvas id="cAcum"></canvas></div>
    <div class="box"><h2>${t("g_vendas_dia")} <small>${t(v)}</small></h2><canvas id="cVendas"></canvas></div>
    <div class="box"><h2>${t("g_reu")}</h2><canvas id="cReu"></canvas></div>
    <div class="box"><h2>${t("g_perd")} <small>${N(d.perdidos_total)}</small></h2><canvas id="cPerd"></canvas></div>
    <div class="box"><h2>${t("g_motivos")}</h2><canvas id="cMot"></canvas></div>
    <div class="box"><h2>${t("g_ind")} <small>${t("g_ind_sub")}</small></h2>
      <div class="cards" style="margin:0">${card(t("vendas"),`${N(i.qtd)} / ${N(i.total_qtd)}`,P(i.total_qtd?i.qtd/i.total_qtd*100:null))}
      ${card(t("valor"),R(i[v]),P(i["total_"+v]?i[v]/i["total_"+v]*100:null))}</div>
      <h2 style="margin-top:16px">${t("g_prod")}</h2>
      <div class="scroll"><table><tr><th>${t("produto")}</th><th>${t("qtd")}</th><th>${t(v)}</th></tr>
      ${d.produtos.map(p=>`<tr><td>${esc(p.produto)}</td><td>${N(p.qtd)}</td><td>${R(p[v])}</td></tr>`).join("")}</table></div>
      <div class="mut" style="font-size:11px;margin-top:6px">${t("combo")}</div></div>
  </div>`;
}
const COR={azul:"#3E5C8A",azul2:"#9DB0CC",cinza:"#B8BFCC",verde:"#3C7D5A",verm:"#A94442",amar:"#B7862B"};
function base(extra){return Object.assign({responsive:true,maintainAspectRatio:false,animation:false,
  plugins:{legend:{labels:{boxWidth:12,color:"#1F2A44"}}},
  scales:{x:{grid:{display:false},ticks:{color:"#6B7280",font:{size:10}}},y:{grid:{color:"#EEF0F4"},ticks:{color:"#6B7280",font:{size:10}},beginAtZero:true}}},extra||{})}
function k(v){return v>=1000?Math.round(v/1000)+"k":Math.round(v)}
function desenharGraf(d){
  const v=S.valor, lab=d.serie.map(s=>D(s.dia));
  const mk=(id,cfg)=>{const c=document.getElementById(id); if(c){c.parentElement.style.height="330px";S.charts.push(new Chart(c,cfg))}};
  mk("cAcum",{type:"line",data:{labels:lab,datasets:[
    {label:t("g_meta"),data:d.serie.map(s=>s.acum_meta),borderColor:COR.cinza,borderDash:[5,4],pointRadius:0,tension:0},
    {label:t("realizado"),data:d.serie.map(s=>s["acum_"+v]),borderColor:COR.azul,backgroundColor:"rgba(62,92,138,.08)",fill:true,pointRadius:2,tension:.15}]},
    options:base({scales:{x:{grid:{display:false},ticks:{color:"#6B7280",font:{size:10}}},y:{ticks:{callback:k,color:"#6B7280"},grid:{color:"#EEF0F4"},beginAtZero:true}}})});
  mk("cVendas",{type:"bar",data:{labels:lab,datasets:[{label:t(v),data:d.serie.map(s=>s["vendas_"+v]),backgroundColor:d.serie.map(s=>s.util?COR.azul:COR.azul2)}]},
    options:base({plugins:{legend:{display:false},tooltip:{callbacks:{afterLabel:(c)=>{const s=d.serie[c.dataIndex];return `${s.vendas_qtd} ${t("vendas").toLowerCase()}${s.feriado?" · "+s.feriado:""}`}}}},
      scales:{x:{grid:{display:false},ticks:{color:"#6B7280",font:{size:10}}},y:{ticks:{callback:k,color:"#6B7280"},grid:{color:"#EEF0F4"},beginAtZero:true}}})});
  mk("cReu",{type:"bar",data:{labels:d.reunioes.map(s=>D(s.dia)),datasets:[
    {label:t("g_feitas"),data:d.reunioes.map(s=>s.feitas),backgroundColor:COR.azul},
    {label:t("g_noshow"),data:d.reunioes.map(s=>s.no_show),backgroundColor:COR.amar},
    {label:t("g_agendadas"),data:d.reunioes.map(s=>s.agendadas),type:"line",borderColor:COR.cinza,pointRadius:0}]},options:base()});
  mk("cPerd",{type:"bar",data:{labels:lab,datasets:[{label:t("g_perd"),data:d.serie.map(s=>s.perdidos),backgroundColor:COR.verm}]},
    options:base({plugins:{legend:{display:false}}})});
  mk("cMot",{type:"bar",data:{labels:d.motivos.map(m=>m.motivo.length>40?m.motivo.slice(0,40)+"…":m.motivo),datasets:[{data:d.motivos.map(m=>m.qtd),backgroundColor:COR.cinza}]},
    options:base({indexAxis:"y",plugins:{legend:{display:false}},scales:{x:{beginAtZero:true,grid:{color:"#EEF0F4"},ticks:{color:"#6B7280"}},y:{grid:{display:false},ticks:{color:"#1F2A44",font:{size:11}}}}})});
}

/* ── Forecast ── */
function viewFc(d){
  if(!d.disponivel) return `<div class="box"><div class="na">${t("fc_na")}</div></div>`;
  const r=d.resto_mes, p=d.projecao;
  let h=`<div class="aviso">${t("fc_bruto")}</div><div class="cards">
    ${card(t("fc_resto"),R(r.em_aberto),`20%: ${R(r.p20)} · 50%: ${R(r.p50)} · 70%: ${R(r.p70)}`)}
    ${card(t("ponderado"),R(r.ponderado),"")}
    ${card(t("fc_7"),R(d.proximos_7.em_aberto),`${t("ponderado")}: ${R(d.proximos_7.ponderado)}`)}
    ${card(t("projecao"),R(p.projecao_bruto),t("proj_sub"))}
    ${card(t("pct_meta"),P(p.pct_meta_bruto),`${t("meta")}: ${R(d.meta_mes)}`)}
    ${card(t("fora_mes"),R(d.fora_do_mes.valor),`${N(d.fora_do_mes.qtd)} ${t("negocio").toLowerCase()}s`)}
    ${card(t("vencidos"),R(d.vencidos.valor),`${N(d.vencidos.qtd)}`)}
    ${card(t("sem_data"),R(d.sem_data.valor),`${N(d.sem_data.qtd)}`)}
  </div>`;
  h+=`<div class="grid2"><div class="box"><h2>${t("dia_a_dia")}</h2><div class="scroll"><table>
    <tr><th>${t("dia")}</th><th>20%</th><th>50%</th><th>70%</th><th>${t("em_aberto_col")}</th><th>${t("ponderado")}</th></tr>
    ${d.dias.map(x=>`<tr><td>${D(x.dia)}</td><td>${R(x.p20)}</td><td>${R(x.p50)}</td><td>${R(x.p70)}</td><td>${R(x.em_aberto)}</td><td>${R(x.ponderado)}</td></tr>`).join("")}
    </table></div></div>
    <div class="box"><h2>${t("fc_deals")} <small>${N(d.deals.length)}</small></h2><div class="scroll"><table>
    <tr><th>${t("negocio")}</th><th class="l">${t("dono")}</th><th>${t("valor")}</th><th>${t("prob")}</th><th>${t("prevista")}</th></tr>
    ${d.deals.map(x=>`<tr><td><a href="${x.link}" target="_blank">${esc(x.titulo)}</a></td><td class="l">${esc(x.dono)}</td><td>${R(x.valor)}</td><td>${x.prob??"—"}</td><td>${D(x.prevista)}</td></tr>`).join("")}
    </table></div></div></div>`;
  return h;
}

marcar(); textos(); carregar();
</script>
</body>
</html>
"""
