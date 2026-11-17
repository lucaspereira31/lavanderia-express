CREATE DATABASE IF NOT EXISTS lavanderia_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE lavanderia_db;

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabela de Serviços Pré-cadastrados (facilita alterar preços e adicionar novos)
CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco_base DECIMAL(10, 2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB;

-- Carga inicial dos serviços solicitados
INSERT INTO servicos (nome, preco_base) VALUES
('Roupas', 0.00),
('Tênis', 0.00),
('Tapetes', 0.00),
('Capacete', 0.00),
('Roupas e Acessórios Pet', 0.00)
ON DUPLICATE KEY UPDATE nome = VALUES(nome);

-- Tabela de Pedidos / Ordens de Serviço (OS)
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    status ENUM('RECEBIDO', 'EM_LAVAGEM', 'PRONTO', 'ENTREGUE', 'CANCELADO') DEFAULT 'RECEBIDO',
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    observacoes TEXT NULL,
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_entrega_prevista DATETIME NULL,
    CONSTRAINT fk_pedidos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Itens do Pedido (permite um pedido ter múltiplos serviços, ex: tênis + tapete)
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    servico_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    detalhes VARCHAR(255) NULL, -- Ex: "Cor azul", "Mancha na gola"
    CONSTRAINT fk_itens_pedido
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_itens_servico
        FOREIGN KEY (servico_id) REFERENCES servicos(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;