# Painel LATAM v2 — Board Academy

Painel do time LATAM no formato do Painel Ascensão (Meta / Realizado / Gap / Previsto), com todas as
regras vindas da **CRN** (`negocios87-sketch/CRN`, branch `main`). Em português e espanhol.

## Estrutura

```
.
├── api/index.py      # Flask (função da Vercel): rotas + bloco que baixa a CRN
├── api/_dados.py     # cálculos, só com funções da biblioteca crn
├── api/_pagina.py    # o HTML do painel (embutido: a Vercel entrega tudo para a função)
├── requirements.txt
└── vercel.json
```

Arquivos com `_` na frente não viram rota na Vercel.

## Deploy na Vercel

1. Vercel → **Add New → Project** → importa `negocios87-sketch/latam_painel_v2`. Sem build settings.
2. **Settings → Environment Variables**:

| Variável | Para que serve |
|---|---|
| `PIPEDRIVE_TOKEN` | token do Pipedrive (o seu) |
| `URL_COLAB` | CSV publicado da aba Colab |
| `URL_METAS` | CSV publicado da aba Metas |
| `CRN_GITHUB_TOKEN` | token fine-grained, só o repositório CRN, Contents: Read-only |

   Não precisa de `URL_FERIADOS`: o LATAM usa os feriados do México (regra A3), calculados na CRN.
3. **Redeploy** depois de salvar as variáveis.
4. **Atualização automática:** Settings → Git → Deploy Hooks (branch = Production Branch) → copiar o link →
   GitHub da CRN → Settings → Secrets and variables → Actions → secret `HOOK_LATAM_PAINEL_V2`.
5. Registrar o painel no `paineis.json` da CRN.

## Conferindo

- `/api/index?fmt=health` → versão da CRN, time LATAM do mês com metas, nomes que não batem com o Pipedrive
  e se o funil LATAM aparece no filtro do forecast.
- `/crn-versao` → `{"versao": "<commit>"}`. Igual ao último commit da CRN = atualizado.
- Rodapé do painel: carimbo com a versão da CRN e os parâmetros.

## Regras usadas (CRN)

| Bloco | Regra |
|---|---|
| Recorte | LT1 (funil LATAM), R3 (só BRL), R4 (cortesia fora), G1 (automático fora) |
| Realizado | M1, M2-B / M2-M (seletor Bruto / c/ Multiplicador) |
| Atingimento, MTD | M3-B / M3-M, T1 |
| Dias úteis | A2 com os feriados do México (A3) |
| Previsto, forecast, projeção | F1 + F2, só etapas de negociação (EN1) |
| Pendências | FQ1 (Larissa Vitor entra pela exceção `donos_extra`) |
| Perdidos e motivos | M8, P1 |
| Produtos | G2 |
| Indicação | G6 / RF1 |
| Reuniões do time | RC1 |

## Escolhas do painel (não são regra)

- Meta do mês = soma das metas financeiras dos closers do time LATAM (Colab + Metas).
- Realizado = qualquer dono que vendeu no funil LATAM (quem não está no time aparece como "fora do time").
- Forecast sempre em valor bruto (a F1 é bruta).
- Em aberto, forecast e pendências são estoque: só aparecem no mês corrente.
- "Previsto ontem" fica "—": não existe foto diária do forecast (S1) para o LATAM.
- Gap e Meta/dia restante: (meta − realizado) e (meta − realizado) ÷ DU restantes (conta simples; ver pendência T1 na CRN).
- Motivos de perda e produtos sem agrupamento.

## Rodando local

```bash
pip install -r requirements.txt   # e a crn instalada pelo instalar.bat
# .env com PIPEDRIVE_TOKEN, URL_COLAB, URL_METAS (não sobe para o GitHub)
python api/index.py               # http://localhost:5000
```
