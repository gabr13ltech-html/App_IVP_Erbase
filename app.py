"""
IVP - Índice de Valor Paisagístico
Backend Flask - Sophia Polis
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import base64
import os
import json
import random
from dotenv import load_dotenv
import os
import requests
import tempfile

load_dotenv()

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")

print("Chave encontrada:", bool(PLANTNET_API_KEY))

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
#  BASE DE ESPÉCIES ARBÓREAS DO NORDESTE
#  (simulada — substitua por modelo de ML real)
# ─────────────────────────────────────────────
ESPECIES = {
    "Craibeira": {
        "nome_cientifico": "Tabebuia aurea",
        "familia": "Bignoniaceae",
        "origem": "Nativa",
        "porte": "Médio a grande",
        "descricao": "Árvore símbolo de Pernambuco, muito usada em arborização urbana no Nordeste. Flores amarelas intensas.",
        "valor_ecologico": 8.5,
        "valor_estetico": 9.0,
        "valor_cultural": 8.0,
        "cor": "#F5C842"
    },
    "Ipê-amarelo": {
        "nome_cientifico": "Handroanthus albus",
        "familia": "Bignoniaceae",
        "origem": "Nativa",
        "porte": "Médio",
        "descricao": "Uma das árvores mais belas do Brasil, floresce sem folhas com exuberantes flores amarelas.",
        "valor_ecologico": 8.0,
        "valor_estetico": 9.5,
        "valor_cultural": 9.0,
        "cor": "#FFD700"
    },
    "Algaroba": {
        "nome_cientifico": "Prosopis juliflora",
        "familia": "Fabaceae",
        "origem": "Exótica",
        "porte": "Pequeno a médio",
        "descricao": "Espécie exótica amplamente distribuída no semiárido nordestino. Fornece sombra e forragem.",
        "valor_ecologico": 5.0,
        "valor_estetico": 5.5,
        "valor_cultural": 6.0,
        "cor": "#8B7355"
    },
    "Umbuzeiro": {
        "nome_cientifico": "Spondias tuberosa",
        "familia": "Anacardiaceae",
        "origem": "Nativa",
        "porte": "Médio",
        "descricao": "Árvore sagrada do sertão nordestino, produz o umbu, fruta símbolo da caatinga. Alta resistência à seca.",
        "valor_ecologico": 9.5,
        "valor_estetico": 7.0,
        "valor_cultural": 10.0,
        "cor": "#6B8E23"
    },
    "Oiticica": {
        "nome_cientifico": "Licania rigida",
        "familia": "Chrysobalanaceae",
        "origem": "Nativa",
        "porte": "Grande",
        "descricao": "Árvore nativa do Nordeste muito usada em arborização urbana. Oferece excelente sombra.",
        "valor_ecologico": 8.0,
        "valor_estetico": 7.5,
        "valor_cultural": 7.0,
        "cor": "#228B22"
    },
    "Mangueira": {
        "nome_cientifico": "Mangifera indica",
        "familia": "Anacardiaceae",
        "origem": "Exótica",
        "porte": "Grande",
        "descricao": "Amplamente cultivada no Nordeste, a mangueira é símbolo da paisagem cultural nordestina.",
        "valor_ecologico": 7.0,
        "valor_estetico": 8.0,
        "valor_cultural": 9.5,
        "cor": "#2D8C3E"
    },
    "Jurema-preta": {
        "nome_cientifico": "Mimosa tenuiflora",
        "familia": "Fabaceae",
        "origem": "Nativa",
        "porte": "Pequeno",
        "descricao": "Espécie pioneira da caatinga com alto valor medicinal e cultural para povos tradicionais do sertão.",
        "valor_ecologico": 8.5,
        "valor_estetico": 5.0,
        "valor_cultural": 9.0,
        "cor": "#8B6914"
    },
    "Cactos-xique-xique": {
        "nome_cientifico": "Pilosocereus gounellei",
        "familia": "Cactaceae",
        "origem": "Nativa",
        "porte": "Médio",
        "descricao": "Cactus colunar icônico da caatinga, essencial para fauna local e identidade visual do semiárido.",
        "valor_ecologico": 9.0,
        "valor_estetico": 8.0,
        "valor_cultural": 8.5,
        "cor": "#5A7A3A"
    }
}


# ─────────────────────────────────────────────
#  CÁLCULO DO IVP
# ─────────────────────────────────────────────
def calcular_ivp(dados):
    """
    Calcula o IVP com base nos parâmetros fornecidos.
    Fórmula adaptada do método brasileiro IVP.
    Cada critério recebe nota de 1 a 3.
    """
    scores = {}

    # 1. FITOSSANIDADE (condição fitossanitária)
    fitossanidade_map = {"otima": 3, "boa": 2, "ruim": 1}
    scores["fitossanidade"] = fitossanidade_map.get(dados.get("fitossanidade", "boa"), 2)

    # 2. INJÚRIAS MECÂNICAS
    injurias_map = {"sem": 3, "leves": 2, "graves": 1}
    scores["injurias"] = injurias_map.get(dados.get("injurias", "leves"), 2)

    # 3. CONFLITOS COM INFRAESTRUTURA
    conflitos_map = {"sem": 3, "moderado": 2, "grave": 1}
    scores["conflitos"] = conflitos_map.get(dados.get("conflitos", "moderado"), 2)

    # 4. ÁREA DE COPA (m²)
    copa = float(dados.get("copa", 10))
    if copa >= 25:
        scores["copa"] = 3
    elif copa >= 10:
        scores["copa"] = 2
    else:
        scores["copa"] = 1

    # 5. ALTURA (m)
    altura = float(dados.get("altura", 5))
    if altura >= 10:
        scores["altura"] = 3
    elif altura >= 5:
        scores["altura"] = 2
    else:
        scores["altura"] = 1

    # 6. DAP - Diâmetro à Altura do Peito (cm)
    dap = float(dados.get("dap", 20))
    if dap >= 40:
        scores["dap"] = 3
    elif dap >= 20:
        scores["dap"] = 2
    else:
        scores["dap"] = 1

    # 7. ORIGEM DA ESPÉCIE
    origem_map = {"nativa": 3, "exotica_adaptada": 2, "exotica": 1}
    scores["origem"] = origem_map.get(dados.get("origem", "nativa"), 2)

    # 8. VALOR PAISAGÍSTICO SUBJETIVO
    paisagistico_map = {"alto": 3, "medio": 2, "baixo": 1}
    scores["paisagistico"] = paisagistico_map.get(dados.get("paisagistico", "medio"), 2)

    total = sum(scores.values())
    maximo = len(scores) * 3
    ivp_percentual = (total / maximo) * 100

    # Classificação
    if ivp_percentual >= 80:
        classificacao = "Excelente"
        cor = "#22c55e"
        recomendacao = "Preservar com alta prioridade. Indivíduo de grande importância paisagística."
    elif ivp_percentual >= 60:
        classificacao = "Bom"
        cor = "#84cc16"
        recomendacao = "Manter com monitoramento periódico e tratamento preventivo."
    elif ivp_percentual >= 40:
        classificacao = "Regular"
        cor = "#eab308"
        recomendacao = "Necessita intervenção: poda, tratamento fitossanitário ou substituição planejada."
    else:
        classificacao = "Crítico"
        cor = "#ef4444"
        recomendacao = "Avaliar remoção com substituição por espécie nativa adequada."

    return {
        "scores": scores,
        "total": total,
        "maximo": maximo,
        "ivp_percentual": round(ivp_percentual, 1),
        "classificacao": classificacao,
        "cor": cor,
        "recomendacao": recomendacao
    }


# ─────────────────────────────────────────────
#  IDENTIFICAÇÃO DE ESPÉCIE (simulada)
#  Para produção: usar PlantNet API ou modelo CNN
# ───────────────────
def identificar_especie_plantnet(imagem_base64):
    """
    Envia imagem para PlantNet e retorna espécies identificadas.
    """

    try:
        # remove prefixo data:image/jpeg;base64,...
        if "," in imagem_base64:
            imagem_base64 = imagem_base64.split(",")[1]

        imagem_bytes = base64.b64decode(imagem_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
            temp.write(imagem_bytes)
            caminho_imagem = temp.name

        url = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"

        with open(caminho_imagem, "rb") as img:
            files = [
                ("images", img)
            ]

            resposta = requests.post(
                url,
                files=files,
                timeout=30
            )

        os.remove(caminho_imagem)

        if resposta.status_code != 200:
            return {
                "erro": f"PlantNet retornou {resposta.status_code}",
                "detalhes": resposta.text
            }

        dados = resposta.json()

        resultados = []

        for item in dados.get("results", [])[:5]:

            especie = item.get("species", {})

            resultados.append({
                "nome_cientifico": especie.get("scientificNameWithoutAuthor", "Desconhecido"),
                "familia": especie.get("family", {}).get("scientificNameWithoutAuthor", ""),
                "confianca": round(item.get("score", 0) * 100, 1)
            })

        return resultados

    except Exception as e:
        return {"erro": str(e)}


# ─────────────────────────────────────────────
#  ROTAS
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/identificar", methods=["POST"])
def identificar():
    """Recebe imagem em base64 e retorna espécies identificadas."""
    try:
        data = request.get_json()
        if not data or "imagem" not in data:
            return jsonify({"erro": "Nenhuma imagem recebida"}), 400

        # Aqui você integraria com PlantNet ou seu modelo
        # Por ora, retorna simulação realista
        resultados = identificar_especie_plantnet(data["imagem"])
        return jsonify({"sucesso": True, "resultados": resultados})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/calcular-ivp", methods=["POST"])
def calcular():
    """Recebe parâmetros e retorna o IVP calculado."""
    try:
        dados = request.get_json()
        resultado = calcular_ivp(dados)
        return jsonify({"sucesso": True, "resultado": resultado})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/especies", methods=["GET"])
def listar_especies():
    """Retorna lista de espécies da base."""
    return jsonify({"especies": ESPECIES})


if __name__ == "__main__":
    print("\n" + "═"*50)
    print("  🌳 IVP - Índice de Valor Paisagístico")
    print("  Sophia Polis · IFS-Campus Lagarto")
    print("═"*50)
    print("  Servidor rodando em: http://localhost:5000")
    print("  Pressione Ctrl+C para encerrar")
    print("═"*50 + "\n")
    app.run(debug=True, port=5000)
