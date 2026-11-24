"""Painel LATAM v2 — cálculos. Todas as regras vêm da biblioteca crn (negocios87-sketch/CRN, main).

Recortes deste painel (escolha do painel, não regra; vão no carimbo):
- Funil LATAM (LT1). Qualquer dono que vendeu no funil entra no realizado.
- Time = pessoas da Colab do mês com squad LATAM. Meta do mês = soma das metas financeiras dos closers do time (R2).
- Dias úteis pelo calendário do México (A3 + A2).
- Forecast = filtro da F1 ∩ funil LATAM ∩ etapas de negociação (EN1). Valor bruto (F1).
- Estoque (em aberto, forecast, pendências) só existe para o mês corrente (M9).
"""
import time
from calendar import monthrange
from datetime import date, timedelta

import crn
from crn.base import fontes, pipedrive
from crn.base.config import campo, config, filtro
from crn.base.fuso import agora_brasil, atividade_dia, data_brasil, data_local, hoje_brasil
from crn.base.texto import cf, dono_id, norm, numero, responsavel_id
from crn.regras import (a3_feriados_mexico as a3, en1_etapa_negociacao as en1, f1_forecast_faixas as f1,
                        f2_forecast_media as f2, fq1_forecast_irregular as fq1, g2_produto as g2,
                        g6_indicacao as g6, lt1_latam as lt1, m1_ganho_closer as m1,
                        m2_faturamento_closer as m2, m3_atingimento_closer as m3, m8_deal_perdido as m8,
                        p1_motivo_perda as p1, rc1_reunioes_closer as rc1, t1_mtd_closer as t1)

SQUAD_LATAM = "latam"
LINK_DEAL = "https://{dominio}.pipedrive.com/deal/{id}"

# ── cache por instância (o Pipedrive tem limite de requisições) ─────────────
_MEMO: dict = {}


def memo(chave, fn, ttl=120):
    agora = time.time()
    if chave in _MEMO and agora - _MEMO[chave][0] < ttl:
        return _MEMO[chave][1]
    valor = fn()
    _MEMO[chave] = (agora, valor)
    return valor


def r2(v):
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return None


def link(deal_id):
    return LINK_DEAL.format(dominio=config()["pipedrive"]["dominio"], id=deal_id)


# ── fontes ─────────────────────────────────────────────────────────────────
def usuarios():
    return memo(("usuarios",), pipedrive.usuarios, 600)


def funis_nome():
    return memo(("funis",), pipedrive.funis, 600)


def opcoes_produto():
    return memo(("opcoes_produto",), lambda: pipedrive.opcoes_campo(campo("nome_produto")), 600)


def feriados_mx(ano):
    return a3.feriados([ano - 1, ano, ano + 1])


def ultimo_du_antes(dia: date, feriados) -> date:
    d = dia - timedelta(days=1)
    while d.weekday() >= 5 or d in feriados:
        d -= timedelta(days=1)
    return d


def ganhos(ini: date, fim: date) -> list[dict]:
    """Ganhos válidos do funil LATAM (M1: sem cortesia, outra moeda e automático)."""
    hoje = hoje_brasil()
    if ini > hoje:
        return []
    fim = min(fim, hoje)

    def buscar():
        brutos = pipedrive.ganhos_do_periodo(ini, fim, pipeline_id=config()["funis"]["latam"][0])
        sep = m1.separar_ganhos(brutos, ini=ini, fim=fim, usuarios=usuarios())
        return [d for d in sep["validos"] if lt1.eh_latam(d)]
    return memo(("ganhos", ini, fim), buscar)


def perdidos(ini: date, fim: date) -> list[dict]:
    hoje = hoje_brasil()
    if ini > hoje:
        return []
    fim = min(fim, hoje)

    def buscar():
        brutos = pipedrive.perdidos_do_periodo(ini, fim, pipeline_id=config()["funis"]["latam"][0])
        return [d for d in m8.perdidos(brutos, ini, fim) if lt1.eh_latam(d)]
    return memo(("perdidos", ini, fim), buscar)


def deals_forecast_todos():
    """Deals do filtro da F1 (todos os funis): usado para saber os funis do forecast (FQ1)."""
    return memo(("forecast_filtro",), lambda: pipedrive.deals(filter_id=filtro("forecast")))


def deals_forecast_latam():
    return [d for d in deals_forecast_todos()
            if lt1.eh_latam(d) and en1.eh_negociacao(d) and d.get("status", "open") == "open"]


def abertos_latam():
    return memo(("abertos",), lambda: pipedrive.deals(pipeline_id=config()["funis"]["latam"][0], status="open"))


def time_do_mes(ano, mes):
    """Pessoas do time LATAM na Colab + meta financeira de quem é closer (R2)."""
    colab = fontes.carregar_colab(ano, mes)
    metas = fontes.carregar_metas(ano, mes)
    meta_por_nome = {m["nome_norm"]: m for m in metas}
    pessoas = []
    for p in colab:
        if norm(p["squad"]) != SQUAD_LATAM:
            continue
        m = meta_por_nome.get(p["nome_norm"])
        meta = m["meta_financeira"] if m and m["papel"] == "closer" else 0.0
        pessoas.append({"nome": p["nome"], "nome_norm": p["nome_norm"], "meta": meta,
                        "com_meta": meta > 0})
    return pessoas, metas


def nome_do_dono(d):
    return m1.nome_dono(d, usuarios()) or "(sem dono)"


def item_venda(d):
    return {"id": d.get("id"), "titulo": d.get("title") or "(sem título)", "dono": nome_do_dono(d),
            "produto": g2.produto(d, opcoes_produto()) or "—",
            "bruto": r2(m2.bruto([d])), "mult": r2(m2.multiplicador([d])),
            "data": str(data_brasil(d.get("won_time")) or ""),
            "indicacao": g6.eh_indicacao(d), "link": link(d.get("id"))}


# ── Painel do Mês ──────────────────────────────────────────────────────────
def painel_mes(ano: int, mes: int) -> dict:
    hoje = hoje_brasil()
    ini, fim = date(ano, mes, 1), date(ano, mes, monthrange(ano, mes)[1])
    corrente = ini <= hoje <= fim
    feriados = feriados_mx(ano)
    du = fontes.dias_uteis_periodo(ano, mes, feriados, hoje)

    pessoas, metas = time_do_mes(ano, mes)
    meta_mes = sum(p["meta"] for p in pessoas)
    vendas = ganhos(ini, fim)

    real = {"bruto": m2.bruto(vendas), "mult": m2.multiplicador(vendas)}

    def bloco(chave):
        realizado = real[chave]
        mtd = t1.mtd(realizado, meta_mes, du["total"], du["passados"])
        gap = meta_mes - realizado
        return {"realizado": r2(realizado), "atingimento": r2(m3.atingimento(realizado, meta_mes)),
                "deveria_mtd": r2(mtd["meta_mtd"]), "pct_mtd": r2(mtd["pct"]), "desvio_mtd": r2(-mtd["gap"]),
                "gap": r2(gap),
                "meta_dia_restante": r2(gap / du["restantes"]) if du["restantes"] and gap > 0 else (0.0 if gap <= 0 else None)}

    # entrou hoje / ontem (último dia útil do México)
    ontem = ultimo_du_antes(hoje, feriados)
    vendas_hoje = [d for d in vendas if data_brasil(d.get("won_time")) == hoje] if corrente else []
    vendas_ontem = ganhos(ontem, ontem) if corrente else []
    entrou = {
        "hoje": {"qtd": len(vendas_hoje), "bruto": r2(m2.bruto(vendas_hoje)), "mult": r2(m2.multiplicador(vendas_hoje))},
        "ontem": {"qtd": len(vendas_ontem), "bruto": r2(m2.bruto(vendas_ontem)), "mult": r2(m2.multiplicador(vendas_ontem)),
                  "data": ontem.isoformat()},
    }

    # por closer: time da Colab + qualquer outro dono que vendeu no funil
    por_dono: dict = {}
    for d in vendas:
        por_dono.setdefault(norm(nome_do_dono(d)), []).append(d)
    linhas = []
    vistos = set()
    for p in pessoas:
        ds = por_dono.get(p["nome_norm"], [])
        vistos.add(p["nome_norm"])
        linhas.append(_linha_pessoa(p["nome"], p["meta"], ds, du, no_time=True))
    for nn, ds in por_dono.items():
        if nn not in vistos:
            linhas.append(_linha_pessoa(nome_do_dono(ds[0]), 0.0, ds, du, no_time=False))
    linhas.sort(key=lambda l: -(l["bruto"] or 0))

    # previsto e em aberto de hoje (estoque: só mês corrente)
    previsto = None
    if corrente:
        fc = deals_forecast_latam()
        fx = f1.faixas(fc, hoje, hoje)
        fora = [d for d in fc if data_local(d.get("expected_close_date")) == hoje
                and d.get("probability") not in config()["F1_forecast"]["probabilidades"]]
        previsto = {"hoje": r2(f2.media_ponderada(fx)), "p20": r2(fx[20]), "p50": r2(fx[50]), "p70": r2(fx[70]),
                    "em_aberto": r2(fx["em_aberto"]), "fora_faixa_qtd": len(fora),
                    "fora_faixa_valor": r2(sum(numero(d.get("value")) for d in fora))}

    feriados_mes = [{"data": d.isoformat(), "nome": n} for d, n in a3.feriados_do_mes(ano, mes).items()]
    return {
        "ano": ano, "mes": mes, "corrente": corrente, "hoje": hoje.isoformat(),
        "meta_mes": r2(meta_mes), "meta_dia": r2(meta_mes / du["total"]) if du["total"] else None,
        "du": du, "feriados": feriados_mes,
        "bruto": bloco("bruto"), "mult": bloco("mult"),
        "vendas_qtd": len(vendas), "ticket_bruto": r2(m2.ticket_medio(vendas)),
        "entrou": entrou, "previsto": previsto,
        "pessoas": linhas,
        "vendas": sorted((item_venda(d) for d in vendas), key=lambda v: v["data"], reverse=True),
        "latam_no_forecast": latam_no_forecast() if corrente else None,
    }


def _linha_pessoa(nome, meta, deals, du, no_time):
    b, mu = m2.bruto(deals), m2.multiplicador(deals)
    mtd_b = t1.mtd(b, meta, du["total"], du["passados"])
    mtd_m = t1.mtd(mu, meta, du["total"], du["passados"])
    return {"nome": nome, "meta": r2(meta) if meta else None, "no_time": no_time, "qtd": len(deals),
            "bruto": r2(b), "mult": r2(mu),
            "ating_bruto": r2(m3.atingimento(b, meta)), "ating_mult": r2(m3.atingimento(mu, meta)),
            "mtd_meta": r2(mtd_b["meta_mtd"]) if meta else None,
            "mtd_pct_bruto": r2(mtd_b["pct"]) if meta else None, "mtd_pct_mult": r2(mtd_m["pct"]) if meta else None}


# ── Pendências (FQ1) ──────────────────────────────────────────────────────
def universo_fq1() -> list[dict]:
    """Universo da FQ1 no funil LATAM: abertos em negociação de closers com meta + exceções (donos_extra)."""
    def calcular():
        hoje = hoje_brasil()
        metas = fontes.carregar_metas(hoje.year, hoje.month)
        donos = fq1.donos_do_universo(metas)
        ids = {uid for uid, nome in usuarios().items() if norm(nome) in donos}
        funis = fq1.funis_do_forecast(deals_forecast_todos())
        return fq1.universo(abertos_latam(), funis, ids, funis_nome())
    return memo(("universo_fq1",), calcular)


def latam_no_forecast() -> bool:
    return config()["funis"]["latam"][0] in fq1.funis_do_forecast(deals_forecast_todos())


def pendencias(ano: int | None = None, mes: int | None = None) -> dict:
    """Só existe para o mês corrente (estoque). Uma chamada de atividades e uma de histórico por deal do universo."""
    hoje = hoje_brasil()
    if (ano, mes) != (None, None) and (ano, mes) != (hoje.year, hoje.month):
        return {"disponivel": False}

    def calcular():
        univ = universo_fq1()
        deal_ids = [d["id"] for d in univ]
        tipo_reuniao = config()["pipedrive"]["tipos_atividade"]["reuniao"]
        reunioes = pipedrive.atividades_dos_deals(deal_ids, tipos=[tipo_reuniao]) if deal_ids else {}
        mudancas = pipedrive.mudancas_de_campo(deal_ids, "expected_close_date") if deal_ids else {}
        agora = agora_brasil()
        itens = []
        for d in univ:
            mot = fq1.motivos(d, reunioes.get(d["id"], []), mudancas.get(d["id"], []), agora)
            ale = fq1.alertas(d, mudancas.get(d["id"], []), agora)
            if mot or ale:
                itens.append({"id": d["id"], "titulo": d.get("title") or "(sem título)", "dono": nome_do_dono(d),
                              "valor": r2(numero(d.get("value"))), "prob": d.get("probability"),
                              "prevista": str(d.get("expected_close_date") or "")[:10] or None,
                              "motivos": mot, "alertas": ale, "link": link(d["id"])})
        itens.sort(key=lambda i: (-len(i["motivos"]), i["dono"]))
        return {"disponivel": True, "universo": len(univ), "irregulares": sum(1 for i in itens if i["motivos"]),
                "itens": itens, "latam_no_forecast": latam_no_forecast()}
    return memo(("pendencias",), calcular)


# ── Gráficos ──────────────────────────────────────────────────────────────
def graficos(ano: int, mes: int) -> dict:
    hoje = hoje_brasil()
    ini, fim = date(ano, mes, 1), date(ano, mes, monthrange(ano, mes)[1])
    feriados = feriados_mx(ano)
    pessoas, _ = time_do_mes(ano, mes)
    meta_mes = sum(p["meta"] for p in pessoas)
    uteis = set(fontes.dias_uteis_calendario(ano, mes, feriados))
    meta_dia = meta_mes / len(uteis) if uteis else 0.0

    vendas = ganhos(ini, fim)
    perd = perdidos(ini, fim)
    dias = [ini + timedelta(days=i) for i in range((fim - ini).days + 1)]

    v_dia = {d: [] for d in dias}
    for x in vendas:
        dd = data_brasil(x.get("won_time"))
        if dd in v_dia:
            v_dia[dd].append(x)
    p_dia = {d: 0 for d in dias}
    for x in perd:
        dd = data_brasil(x.get("lost_time"))
        if dd in p_dia:
            p_dia[dd] += 1

    acum_b = acum_m = acum_meta = 0.0
    serie = []
    for d in dias:
        if d in uteis:
            acum_meta += meta_dia
        acum_b += m2.bruto(v_dia[d])
        acum_m += m2.multiplicador(v_dia[d])
        futuro = d > hoje
        serie.append({"dia": d.isoformat(), "util": d in uteis, "feriado": a3.feriados_do_ano(ano).get(d),
                      "vendas_qtd": len(v_dia[d]), "vendas_bruto": r2(m2.bruto(v_dia[d])),
                      "vendas_mult": r2(m2.multiplicador(v_dia[d])), "perdidos": p_dia[d],
                      "acum_meta": r2(acum_meta),
                      "acum_bruto": None if futuro else r2(acum_b), "acum_mult": None if futuro else r2(acum_m)})

    # motivos de perda (P1, sem agrupamento)
    motivos: dict = {}
    for x in perd:
        motivos[p1.motivo(x)] = motivos.get(p1.motivo(x), 0) + 1
    top_motivos = sorted(motivos.items(), key=lambda kv: -kv[1])[:10]

    # produtos (G2) e indicação (G6)
    prods: dict = {}
    for x in vendas:
        nome = g2.produto(x, opcoes_produto()) or "(sem produto)"
        r = prods.setdefault(nome, {"produto": nome, "qtd": 0, "bruto": 0.0, "mult": 0.0})
        r["qtd"] += 1
        r["bruto"] += m2.bruto([x])
        r["mult"] += m2.multiplicador([x])
    ind = [x for x in vendas if g6.eh_indicacao(x)]

    # reuniões do time (RC1), por dia
    reu = _reunioes_por_dia(ini, min(fim, hoje), pessoas) if ini <= hoje else []

    return {
        "ano": ano, "mes": mes, "serie": serie,
        "motivos": [{"motivo": k, "qtd": v} for k, v in top_motivos], "perdidos_total": len(perd),
        "produtos": sorted(({**r, "bruto": r2(r["bruto"]), "mult": r2(r["mult"])} for r in prods.values()),
                           key=lambda r: -r["qtd"]),
        "indicacao": {"qtd": len(ind), "bruto": r2(m2.bruto(ind)), "mult": r2(m2.multiplicador(ind)),
                      "total_qtd": len(vendas), "total_bruto": r2(m2.bruto(vendas)), "total_mult": r2(m2.multiplicador(vendas))},
        "reunioes": reu,
    }


def _reunioes_por_dia(ini, fim, pessoas):
    nomes = {p["nome_norm"] for p in pessoas}
    ids = {uid for uid, nome in usuarios().items() if norm(nome) in nomes}
    if not ids:
        return []
    t = config()["pipedrive"]["tipos_atividade"]
    ativ = memo(("reunioes", ini, fim),
                lambda: pipedrive.atividades_do_periodo(ini, fim, tipos=[t["reuniao"], t["no_show"], t["reagendamento"]]))
    out = []
    d = ini
    while d <= fim:
        por = rc1.reunioes_closer(ativ, d, d, closer_ids=ids)
        out.append({"dia": d.isoformat(),
                    "agendadas": sum(v["agendadas"] for v in por.values()),
                    "feitas": sum(v["feitas"] for v in por.values()),
                    "no_show": sum(v["no_show"] for v in por.values())})
        d += timedelta(days=1)
    return out


# ── Forecast ──────────────────────────────────────────────────────────────
def forecast(ano: int, mes: int) -> dict:
    hoje = hoje_brasil()
    ini, fim = date(ano, mes, 1), date(ano, mes, monthrange(ano, mes)[1])
    if not (ini <= hoje <= fim):
        return {"ano": ano, "mes": mes, "disponivel": False}
    fc = deals_forecast_latam()
    pessoas, _ = time_do_mes(ano, mes)
    meta_mes = sum(p["meta"] for p in pessoas)
    vendas = ganhos(ini, fim)

    dias = []
    d = hoje
    while d <= fim:
        fx = f1.faixas(fc, d, d)
        dias.append({"dia": d.isoformat(), "p20": r2(fx[20]), "p50": r2(fx[50]), "p70": r2(fx[70]),
                     "em_aberto": r2(fx["em_aberto"]), "ponderado": r2(f2.media_ponderada(fx))})
        d += timedelta(days=1)
    resto = f1.faixas(fc, hoje, fim)
    prox7 = f1.faixas(fc, hoje, hoje + timedelta(days=6))
    fora_mes = [x for x in fc if (data_local(x.get("expected_close_date")) or date.min) > fim]
    vencidos = [x for x in fc if (data_local(x.get("expected_close_date")) or date.max) < hoje]

    # sem data prevista: universo da FQ1 (o filtro da F1 não traz deal sem data)
    sem_data = [x for x in universo_fq1() if not data_local(x.get("expected_close_date"))]

    previsto_resto = f2.media_ponderada(resto)
    real_b, real_m = m2.bruto(vendas), m2.multiplicador(vendas)

    def deal_fc(x):
        return {"id": x.get("id"), "titulo": x.get("title") or "(sem título)", "dono": nome_do_dono(x),
                "valor": r2(numero(x.get("value"))), "prob": x.get("probability"),
                "prevista": str(x.get("expected_close_date") or "")[:10], "link": link(x.get("id"))}

    no_mes = [x for x in fc if hoje <= (data_local(x.get("expected_close_date")) or date.min) <= fim]
    return {
        "ano": ano, "mes": mes, "disponivel": True, "hoje": hoje.isoformat(), "meta_mes": r2(meta_mes),
        "dias": dias,
        "resto_mes": {"p20": r2(resto[20]), "p50": r2(resto[50]), "p70": r2(resto[70]),
                      "em_aberto": r2(resto["em_aberto"]), "ponderado": r2(previsto_resto)},
        "proximos_7": {"em_aberto": r2(prox7["em_aberto"]), "ponderado": r2(f2.media_ponderada(prox7))},
        "projecao": {"realizado_bruto": r2(real_b), "realizado_mult": r2(real_m),
                     "previsto_que_falta": r2(previsto_resto),
                     "projecao_bruto": r2(real_b + previsto_resto),
                     "pct_meta_bruto": r2(m3.atingimento(real_b + previsto_resto, meta_mes))},
        "fora_do_mes": {"qtd": len(fora_mes), "valor": r2(sum(numero(x.get("value")) for x in fora_mes))},
        "vencidos": {"qtd": len(vencidos), "valor": r2(sum(numero(x.get("value")) for x in vencidos))},
        "sem_data": {"qtd": len(sem_data), "valor": r2(sum(numero(x.get("value")) for x in sem_data))},
        "deals": sorted((deal_fc(x) for x in no_mes), key=lambda x: (x["prevista"], -(x["valor"] or 0))),
    }


# ── carimbo e saúde ───────────────────────────────────────────────────────
def carimbo() -> str:
    return (f"CRN {crn.versao()} · Funil: LATAM (LT1) · Eixo: data de ganho (Brasília) · "
            f"Meta: soma dos closers do time LATAM (Colab + Metas) · Dias úteis: feriados do México (A3) · "
            f"Forecast: filtro F1 ∩ etapas de negociação (EN1), valor bruto · Atualizado: "
            f"{agora_brasil().strftime('%d/%m/%Y %H:%M')}")


def saude() -> dict:
    out = {"crn": crn.versao(), "hoje_br": hoje_brasil().isoformat()}
    try:
        h = hoje_brasil()
        pessoas, _ = time_do_mes(h.year, h.month)
        out["time_latam"] = [{"nome": p["nome"], "meta": p["meta"]} for p in pessoas]
        nomes_pd = {norm(n) for n in usuarios().values()}
        out["nao_encontrados_no_pipedrive"] = [p["nome"] for p in pessoas if p["nome_norm"] not in nomes_pd]
    except Exception as e:  # noqa: BLE001
        out["erro_time"] = f"{type(e).__name__}: {e}"
    try:
        out["latam_no_filtro_forecast"] = latam_no_forecast()
    except Exception as e:  # noqa: BLE001
        out["erro_forecast"] = f"{type(e).__name__}: {e}"
    return out
