import os
import urllib.parse
from flask import Flask, render_template, request, jsonify, send_file
from db import get_connection
from pdf_generator import gerar_pdf_comprovante
from printer import disparar_impressao_termica

app = Flask(__name__)

@app.route('/')
def index():
    # Carrega serviços pré-cadastrados
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, preco_base FROM servicos")
            servicos = cursor.fetchall()
        return render_template('index.html', servicos=servicos)
    finally:
        conn.close()

@app.route('/api/clientes/<cpf>', methods=['GET'])
def buscar_cliente(cpf):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, cpf, telefone FROM clientes WHERE cpf = %s", (cpf,))
            cliente = cursor.fetchone()
            if cliente:
                return jsonify(cliente)
            return jsonify({"erro": "Cliente não encontrado"}), 404
    finally:
        conn.close()

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    nome = data.get('nome')
    cpf = data.get('cpf')
    telefone = data.get('telefone')
    itens = data.get('itens', [])

    if not nome or not cpf or not telefone or not itens:
        return jsonify({"erro": "Dados obrigatórios incompletos."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Cadastra ou atualiza cliente
            cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE nome = VALUES(nome), telefone = VALUES(telefone)
            """, (nome, cpf, telefone))

            cursor.execute("SELECT id FROM clientes WHERE cpf = %s", (cpf,))
            cliente_id = cursor.fetchone()['id']

            # 2. Calcula total
            total_pedido = sum(float(item['subtotal']) for item in itens)

            # 3. Cria pedido
            cursor.execute("""
                INSERT INTO pedidos (cliente_id, valor_total)
                VALUES (%s, %s)
            """, (cliente_id, total_pedido))
            pedido_id = cursor.lastrowid

            # 4. Salva itens e garante 'servico_nome' para o PDF e impressora
            for item in itens:
                cursor.execute("""
                    INSERT INTO itens_pedido (pedido_id, servico_id, quantidade, preco_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pedido_id,
                    item['servico_id'],
                    item['quantidade'],
                    item['preco_unitario'],
                    item['subtotal']
                ))

                nome_srv = item.get('servico_nome') or item.get('nome_servico') or item.get('servico') or item.get('nome')
                if not nome_srv:
                    cursor.execute("SELECT nome FROM servicos WHERE id = %s", (item['servico_id'],))
                    res = cursor.fetchone()
                    nome_srv = res['nome'] if res else f"Serviço #{item['servico_id']}"

                item['servico_nome'] = nome_srv
                item['nome_servico'] = nome_srv
                item['servico'] = nome_srv
                item['nome'] = nome_srv

            conn.commit()

        # 5. Gera o PDF do comprovante (garantindo que a pasta exista na nuvem)
        cliente_dados = {"nome": nome, "telefone": telefone, "cpf": cpf}
        pasta_comprovantes = os.path.join(app.root_path, "uploads", "comprovantes")
        os.makedirs(pasta_comprovantes, exist_ok=True)
        gerar_pdf_comprovante(pedido_id, cliente_dados, itens, total_pedido, destino_pasta=pasta_comprovantes)

        # 6. Dispara a impressão térmica (ignora se estiver rodando na nuvem sem USB)
        try:
            disparar_impressao_termica(pedido_id, cliente_dados, itens, total_pedido)
        except Exception as e:
            print(f"Impressora térmica indisponível neste ambiente: {e}")

        # 7. Formata link de WhatsApp direto com mensagem pronta
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if len(telefone_limpo) in [10, 11] and not telefone_limpo.startswith('55'):
            telefone_limpo = f"55{telefone_limpo}"

        mensagem = (
            f"Olá {nome}! Seu pedido na Lavanderia foi registrado com sucesso!\n\n"
            f"📄 *Ordem de Serviço:* #{pedido_id}\n"
            f"💰 *Total:* R$ {total_pedido:.2f}\n\n"
            f"Avisaremos assim que suas peças estiverem prontas para retirada!"
        )
        whatsapp_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(mensagem)}"

        return jsonify({
            "sucesso": True,
            "pedido_id": pedido_id,
            "whatsapp_link": whatsapp_url,
            "pdf_url": f"/comprovante/{pedido_id}"
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route('/comprovante/<int:pedido_id>')
def download_comprovante(pedido_id):
    caminho = os.path.join(app.root_path, "uploads", "comprovantes", f"OS_{pedido_id}.pdf")
    if not os.path.exists(caminho):
        return jsonify({"erro": "Comprovante não encontrado."}), 404
    return send_file(caminho, as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)