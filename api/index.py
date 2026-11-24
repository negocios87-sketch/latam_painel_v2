"""Painel LATAM v2 — Board Academy. Flask na Vercel; regras pela CRN (negocios87-sketch/CRN, main).

Rotas (a Vercel entrega tudo para esta função; a decisão é pelo ?fmt=):
    /                                     → o painel (HTML)
    /api/index?fmt=mes&mes=&ano=          → Painel do Mês (JSON)
    /api/index?fmt=graficos&mes=&ano=     → Gráficos (JSON)
    /api/index?fmt=forecast&mes=&ano=     → Forecast (JSON)
    /api/index?fmt=pendencias&mes=&ano=   → Pendências do forecast, FQ1 (JSON; carrega depois do Painel do Mês)
    /api/index?fmt=health                 → diagnóstico (JSON)
    /crn-versao                           → {"versao": crn.versao()} (público, sem dado)

Environment Variables na Vercel: PIPEDRIVE_TOKEN, URL_COLAB, URL_METAS, CRN_GITHUB_TOKEN.
"""
import io
import os

# ── CRN: baixada do GitHub quando o painel liga ───────────────
# A Vercel não repassa o token para o instalador do build, então a CRN não entra pelo
# requirements.txt. O painel baixa a versão atual da main (com o token, que em tempo de
# execução funciona) e carrega. Cada vez que o painel liga, pega as regras mais recentes.
# No computador, se a crn já estiver instalada (instalar.bat), usa a instalada.
def _carregar_crn():
    import importlib.util
    import shutil
    import sys
    import tarfile
    import tempfile
    if importlib.util.find_spec("crn") is not None:
        return None
    import requests
    token = (os.environ.get("CRN_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("CRN_GITHUB_TOKEN não está nas Environment Variables da Vercel.")
    r = requests.get("https://api.github.com/repos/negocios87-sketch/CRN/tarball/main",
                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                     timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Não consegui baixar a CRN do GitHub (HTTP {r.status_code}). Confira o CRN_GITHUB_TOKEN.")
    base = tempfile.mkdtemp(prefix="crn_")
    with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
        tar.extractall(base, filter="data")
    raiz = os.path.join(base, os.listdir(base)[0])          # negocios87-sketch-CRN-<commit>
    destino = os.path.join(base, "pacote", "crn")
    shutil.copytree(os.path.join(raiz, "lib"), destino)     # mesmo mapa do pyproject da CRN
    shutil.copytree(os.path.join(raiz, "config"), os.path.join(destino, "config"))
    sys.path.insert(0, os.path.join(base, "pacote"))
    return os.path.basename(raiz).rsplit("-", 1)[-1][:7]   # commit que entrou

_COMMIT_CRN = _carregar_crn()

import crn
if _COMMIT_CRN:
    crn.versao = lambda: _COMMIT_CRN                        # carimbo mostra o commit carregado

import math
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests as req
from flask import Flask, Response, jsonify, request

from crn.base.fontes import FonteInvalida
from crn.base.fuso import hoje_brasil

import _dados as dados
from _pagina import PAGINA_HTML

app = Flask(__name__)


def limpar(obj):
    if isinstance(obj, dict):
        return {str(k): limpar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [limpar(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


def _periodo():
    h = hoje_brasil()
    mes = request.args.get("mes", type=int) or h.month
    ano = request.args.get("ano", type=int) or h.year
    if not (1 <= mes <= 12 and 2020 <= ano <= 2100):
        raise ValueError("Mês ou ano inválido.")
    return ano, mes


def _responder(fn):
    try:
        ano, mes = _periodo()
        data = fn(ano, mes)
        data["carimbo"] = dados.carimbo()
        return jsonify(limpar(data))
    except FonteInvalida as e:
        return jsonify({"erro": f"Planilha: {e}"}), 400
    except req.HTTPError as e:
        return jsonify({"erro": f"Pipedrive respondeu {e.response.status_code}",
                        "detalhe": e.response.text[:400]}), 502
    except Exception as e:  # noqa: BLE001
        return jsonify({"erro": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]}), 500


@app.route("/", defaults={"p": ""}, methods=["GET"])
@app.route("/<path:p>", methods=["GET"])
def roteador(p):
    modo = (request.args.get("fmt") or "").strip().lower()
    alvo = (p or "").strip("/").lower()
    if modo == "versao" or alvo.endswith("crn-versao"):
        return jsonify({"versao": crn.versao()})
    if modo == "health":
        return jsonify(limpar(dados.saude()))
    if modo == "mes":
        return _responder(dados.painel_mes)
    if modo == "graficos":
        return _responder(dados.graficos)
    if modo == "forecast":
        return _responder(dados.forecast)
    if modo == "pendencias":
        return _responder(dados.pendencias)
    return Response(PAGINA_HTML, mimetype="text/html; charset=utf-8")


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), debug=True)
