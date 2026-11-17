import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def gerar_pdf_comprovante(pedido_id, cliente, itens, total, destino_pasta="uploads/comprovantes"):
    os.makedirs(destino_pasta, exist_ok=True)
    caminho_arquivo = os.path.join(destino_pasta, f"OS_{pedido_id}.pdf")

    c = canvas.Canvas(caminho_arquivo, pagesize=letter)
    width, height = letter

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "LAVANDERIA EXPRESS - COMPROVANTE DE SERVIÇO")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Ordem de Serviço (OS): #{pedido_id}")
    c.drawString(50, height - 85, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Dados do Cliente
    c.line(50, height - 95, 550, height - 95)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 115, "Dados do Cliente:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 130, f"Nome: {cliente['nome']}")
    c.drawString(50, height - 145, f"Telefone: {cliente['telefone']}")
    c.drawString(50, height - 160, f"CPF: {cliente['cpf']}")

    # Itens do Pedido
    c.line(50, height - 175, 550, height - 175)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 195, "Serviços Solicitados:")

    y = height - 215
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Serviço")
    c.drawString(300, y, "Qtd")
    c.drawString(450, y, "Subtotal (R$)")
    y -= 15
    c.line(50, y + 5, 550, y + 5)

    c.setFont("Helvetica", 10)
    for item in itens:
        c.drawString(50, y, str(item['servico_nome']))
        c.drawString(300, y, str(item['quantidade']))
        c.drawString(450, y, f"R$ {float(item['subtotal']):.2f}")
        y -= 20

    c.line(50, y + 5, 550, y + 5)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y - 15, f"VALOR TOTAL: R$ {float(total):.2f}")

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 60, "Agradecemos pela preferência! Guarde este comprovante para retirada.")

    c.showPage()
    c.save()

    return caminho_arquivo