def imprimir_via_recibo(pedido_id, cliente, itens, total, tipo_via="CLIENTE"):
    texto = []
    texto.append("================================")
    texto.append("       LAVANDERIA EXPRESS       ")
    texto.append(f"          VIA {tipo_via}        ")
    texto.append("================================")
    texto.append(f"OS: #{pedido_id}")
    texto.append(f"Cliente: {cliente['nome']}")
    texto.append(f"Telefone: {cliente['telefone']}")
    texto.append("--------------------------------")
    texto.append("ITENS / SERVIÇOS:")
    for item in itens:
        linha = f"{item['servico_nome']} x{item['quantidade']} = R$ {float(item['subtotal']):.2f}"
        texto.append(linha)
    texto.append("--------------------------------")
    texto.append(f"TOTAL: R$ {float(total):.2f}")
    texto.append("================================\n\n\n")

    return "\n".join(texto)


def disparar_impressao_termica(pedido_id, cliente, itens, total):
    via_cliente = imprimir_via_recibo(pedido_id, cliente, itens, total, "CLIENTE")
    via_dono = imprimir_via_recibo(pedido_id, cliente, itens, total, "CONTROLE / LAVANDERIA")

    print("\n--- [IMPRESSÃO VIA CLIENTE] ---")
    print(via_cliente)
    print("--- [IMPRESSÃO VIA DONO] ---")
    print(via_dono)
    return True