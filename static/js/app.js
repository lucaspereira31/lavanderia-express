let itensPedido = [];

// Elementos DOM
const inputCpf = document.getElementById('cpf');
const inputNome = document.getElementById('nome');
const inputTelefone = document.getElementById('telefone');
const statusCliente = document.getElementById('status-cliente');

const selectServico = document.getElementById('servico');
const inputQtd = document.getElementById('quantidade');
const inputPreco = document.getElementById('preco');
const btnAdicionar = document.getElementById('btn-adicionar');
const tbodyItens = document.getElementById('lista-itens');
const spanTotal = document.getElementById('valor-total');
const btnFinalizar = document.getElementById('btn-finalizar');

// Máscara de CPF (000.000.000-00)
inputCpf.addEventListener('input', (e) => {
    let v = e.target.value.replace(/\D/g, '');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    e.target.value = v;

    // Quando completar 14 caracteres (CPF completo), busca no banco
    if (v.length === 14) {
        buscarClientePorCpf(v);
    }
});

// Máscara de Telefone ((11) 99999-9999)
inputTelefone.addEventListener('input', (e) => {
    let v = e.target.value.replace(/\D/g, '');
    v = v.replace(/^(\d{2})(\d)/g, '($1) $2');
    v = v.replace(/(\d)(\d{4})$/, '$1-$2');
    e.target.value = v;
});

// Preenche preço base automaticamente se houver cadastrado no banco
selectServico.addEventListener('change', () => {
    const option = selectServico.options[selectServico.selectedIndex];
    const precoBase = parseFloat(option.dataset.preco || 0);
    if (precoBase > 0) {
        inputPreco.value = precoBase.toFixed(2);
    }
});

// Busca cliente já cadastrado pelo CPF
async function buscarClientePorCpf(cpf) {
    try {
        statusCliente.textContent = 'Buscando cliente...';
        const resp = await fetch(`/api/clientes/${encodeURIComponent(cpf)}`);
        if (resp.ok) {
            const cliente = await resp.json();
            inputNome.value = cliente.nome;
            inputTelefone.value = cliente.telefone;
            statusCliente.textContent = '✓ Cliente encontrado!';
        } else {
            statusCliente.textContent = 'Novo cliente (será cadastrado no pedido).';
        }
    } catch (err) {
        statusCliente.textContent = '';
    }
}

// Adicionar item na tabela
btnAdicionar.addEventListener('click', () => {
    const option = selectServico.options[selectServico.selectedIndex];
    const servicoId = parseInt(selectServico.value);
    const servicoNome = option.dataset.nome;
    const quantidade = parseInt(inputQtd.value);
    const precoUnitario = parseFloat(inputPreco.value);

    if (!quantidade || quantidade <= 0) {
        alert('Informe uma quantidade válida.');
        return;
    }
    if (isNaN(precoUnitario) || precoUnitario <= 0) {
        alert('Informe o preço unitário do serviço.');
        return;
    }

    const subtotal = quantidade * precoUnitario;

    itensPedido.push({
        servico_id: servicoId,
        servico_nome: servicoNome,
        quantidade: quantidade,
        preco_unitario: precoUnitario,
        subtotal: subtotal
    });

    // Limpa campos do item para o próximo
    inputQtd.value = 1;
    inputPreco.value = '';
    renderizarTabela();
});

function removerItem(index) {
    itensPedido.splice(index, 1);
    renderizarTabela();
}

function renderizarTabela() {
    tbodyItens.innerHTML = '';

    if (itensPedido.length === 0) {
        tbodyItens.innerHTML = `
            <tr id="linha-vazia">
                <td colspan="5" class="texto-centro">Nenhum serviço adicionado ainda.</td>
            </tr>`;
        spanTotal.textContent = 'R$ 0,00';
        return;
    }

    let totalGeral = 0;

    itensPedido.forEach((item, idx) => {
        totalGeral += item.subtotal;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.servico_nome}</td>
            <td>${item.quantidade}</td>
            <td>R$ ${item.preco_unitario.toFixed(2).replace('.', ',')}</td>
            <td><strong>R$ ${item.subtotal.toFixed(2).replace('.', ',')}</strong></td>
            <td><button type="button" class="btn-danger" onclick="removerItem(${idx})">Remover</button></td>
        `;
        tbodyItens.appendChild(tr);
    });

    spanTotal.textContent = `R$ ${totalGeral.toFixed(2).replace('.', ',')}`;
}

// Finalizar e Enviar para o Backend
btnFinalizar.addEventListener('click', async () => {
    const cpf = inputCpf.value.trim();
    const nome = inputNome.value.trim();
    const telefone = inputTelefone.value.trim();

    if (!cpf || !nome || !telefone) {
        alert('Preencha CPF, Nome e Telefone do cliente.');
        return;
    }

    if (itensPedido.length === 0) {
        alert('Adicione pelo menos um serviço ao pedido.');
        return;
    }

    btnFinalizar.disabled = true;
    btnFinalizar.textContent = 'Processando pedido e imprimindo...';

    try {
        const resposta = await fetch('/api/pedidos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cpf: cpf,
                nome: nome,
                telefone: telefone,
                itens: itensPedido
            })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(resultado.erro || 'Erro ao registrar pedido.');
        }

        // Exibe painel de sucesso com links de WhatsApp e PDF
        document.getElementById('os-numero').textContent = resultado.pedido_id;
        document.getElementById('link-whatsapp').href = resultado.whatsapp_link;
        document.getElementById('link-pdf').href = resultado.pdf_url;
        document.getElementById('painel-sucesso').classList.remove('oculto');

    } catch (erro) {
        alert('Falha: ' + erro.message);
    } finally {
        btnFinalizar.disabled = false;
        btnFinalizar.textContent = '🖨️ Gerar Pedido, Imprimir (2 Vias) e Preparar WhatsApp';
    }
});

// Botão para limpar a tela e iniciar novo atendimento
document.getElementById('btn-novo-pedido').addEventListener('click', () => {
    inputCpf.value = '';
    inputNome.value = '';
    inputTelefone.value = '';
    statusCliente.textContent = '';
    itensPedido = [];
    renderizarTabela();
    document.getElementById('painel-sucesso').classList.add('oculto');
});