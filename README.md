# verity

Para executar o script, há a necessidade de uma conexão com algum bd PostgreSQL. Favor substituir as variáveis db, host e user (linha 124) para realizar a conexão. O script de criação de tabelas, bem como inserção de dados fictícios se encontra nesse repositório. Além disso, há a necessidade de inserir uma 'api_key' Nvidia Nim para conexão com o LLM (linha 127).

Após a criação do banco, tabelas e inserção da chave, basta rodar no terminal 'streamlit run agente.py'.
