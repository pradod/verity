CREATE TABLE clientes (
    cliente_id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    saldo NUMERIC(10,2)
);

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    preco NUMERIC(10,2)
);

CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(cliente_id),
    produto_id INT REFERENCES produtos(id),
    quantidade INT CHECK (quantidade > 0)
);

INSERT INTO clientes (nome, saldo)
VALUES
    ('Uma Carter', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Quinn Green', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Zane White', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Alice Martin', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Dana Williams', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Rachel Jackson', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Leo Walker', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Mona Allen', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Dana Garcia', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Zane Evans', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Wendy Smith', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Bob Adams', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Ian Jones', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Tina Lee', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Mike Hall', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Ian Lee', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Victor Johnson', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Olivia Edwards', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Zane Parker', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Will Gonzalez', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Mike Lewis', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Xander Brown', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Fiona Young', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Charlie Davis', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Dana Scott', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Uma Garcia', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Yara Taylor', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Frank Hernandez', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Charlie Nelson', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Eve Green', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Fiona Brown', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Julia King', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Xenia Moore', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Aaron Wright', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Steve Sanchez', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Diana Green', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('George White', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Karen Wilson', (random() * 5000 + 500)::NUMERIC(10,2)),
    ('Leo Williams', (random() * 5000 + 500)::NUMERIC(10,2));

INSERT INTO produtos (nome, preco) VALUES
    ('Notebook', 1200.00),
    ('Smartphone', 800.00),
    ('Tablet', 600.00),
    ('Monitor', 300.00),
    ('Mouse', 50.00);

INSERT INTO transacoes (cliente_id, produto_id, quantidade)
SELECT 
    (FLOOR(random() * (SELECT MAX(cliente_id) FROM clientes) + 1))::INT,
    (FLOOR(random() * (SELECT MAX(id) FROM produtos) + 1))::INT,
    (FLOOR(random() * 4) + 1)::INT
FROM generate_series(1, 250);
