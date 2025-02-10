import duckdb
import re
import streamlit as st
from dataclasses import dataclass
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.graph import StateGraph

class DBCon:
    def __init__(self, db: str, host: str, user: str):
        self.conn = duckdb.connect()
        self.db = db
        self.host = host
        self.user = user
        self._connect()

    def _connect(self):
        self.conn.sql(f"""
            LOAD postgres;  
            ATTACH 'dbname={self.db} hostaddr={self.host} user={self.user}' 
            AS data (TYPE postgres, READ_ONLY, SCHEMA public);  
        """)

    def fetch_schema(self):
        try:
            tables = self.conn.execute("""
                SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
            """).fetchall()
            schema_info = ""
            for table in tables:
                table_name = table[0]
                columns = self.conn.execute(f"""
                    SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';
                """).fetchall()
                schema_info += f"\nTable: {table_name}\n"
                for col in columns:
                    schema_info += f" - {col[0]} ({col[1]})\n"
            return schema_info
        except Exception as e:
            return f"Erro ao retornar schema: {str(e)}"

    def execute(self, query):
        return self.conn.execute(query)

class Agente:
    SQL_PROMPT_TEMPLATE = """
    You are an expert SQL assistant that generates precise and efficient SQL queries for PostgreSQL.
    Follow these rules:
    1. Only generate valid **PostgreSQL SQL**.
    2. Avoid using SQL commands that modify the database (**e.g., DELETE, DROP, ALTER**).
    3. Ensure all column and table names exist in the database.
    4. Never use `LIMIT 1`.
    6. You SHOULD ALWAYS include the following string before calling any table name `data.public.`
    7. You SHOULD ALWAYS create an alias when using the function `count.
    8. If there is any questions mentioning clients, you should return the clients name instead of clients_id.
    9. You SHOULD ALWAYS output the final query by beginning with the following text `final_version_begins` and ending with the following text `final_version_ends'.
    10. Avoid using subqueries, use common table expression.
    11. Just output the query, nothing more.

    ### Database Schema:
    {schema_info}

    ### User Request:
    {user_query}
    """

    def __init__(self, llm, dbx):
        self.llm = llm
        self.dbx = dbx

    def gen_sql(self, user_query):
        schema_info = self.dbx.fetch_schema()
        prompt = self.SQL_PROMPT_TEMPLATE.format(schema_info=schema_info, user_query=user_query)
        try:
            response = self.llm.invoke(prompt)
            sql_query = self._get_query_from_output(response.content)
            return sql_query
        except Exception as e:
            return f"Error generating SQL: {str(e)}"

    def _get_query_from_output(self, response):
        start = response.find('final_version_begins') + len('final_version_begins')
        end = response.find('final_version_ends')
        return response[start:end].strip()

class SQLValidator:
    @staticmethod
    def validate(sql_query, dbx):
        disallowed_patterns = [r"\bDROP\b", r"\bDELETE\b", r"\bALTER\b", r"\bINSERT\b", r"\bTRUNCATE\b", r"\bEXEC\b"]
        for pattern in disallowed_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                return False, "Erro: A query contem operações desativadas."

        try:
            dbx.execute(f"EXPLAIN (FORMAT TEXT) {sql_query};")
        except Exception as e:
            return False, f"Verifique a sintaxe do código SQL {str(e)}"

        return True, sql_query

class RunQuery:
    def __init__(self, dbx):
        self.dbx = dbx

    def execute(self, sql_query):
        try:
            
            prepared_query = self.dbx.execute(f"PREPARE stmt AS {sql_query}")
            result = self.dbx.execute("EXECUTE stmt")
            
            if result is None or result.rowcount == 0:
                return "Nenhum dado encontrado"

            return result.fetchdf()
        except Exception as e:
            return f"Erro no PostgreSQL: {str(e)}"

@dataclass
class QueryState:
    user_query: str
    sql_query: str = ""
    validated_query: str = ""
    result: str = ""

dbx = DBCon(db='nome_do_bd', host='endereco_host', user='usuario_postgres')
llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    api_key="",
    temperature=0.6,
    top_p=0.7,
    max_tokens=4096
)
sql_agent = Agente(llm, dbx)
sql_validator = SQLValidator()
query_executor = RunQuery(dbx)

def process_query(state):
    sql_query = sql_agent.gen_sql(state.user_query)
    state.sql_query = sql_query
    
    is_valid, validation_result = sql_validator.validate(sql_query, dbx)
    if not is_valid:
        state.result = validation_result
        return state
    
    state.validated_query = validation_result
    execution_result = query_executor.execute(validation_result)
    state.result = execution_result
    return state

graph = StateGraph(QueryState)
graph.add_node("process_query", process_query)
graph.set_entry_point("process_query")
graph.set_finish_point("process_query")
executor = graph.compile()

st.title("Agente SQL")
user_query = st.text_input("Digite algo (e.x: 'Qual cliente comprou a maior variedade de produtos diferentes?'):")
if st.button("Run"):
    if user_query:
        state = QueryState(user_query=user_query)
        final_state = executor.invoke(state)
        final_query = final_state.get('sql_query')
        
        st.write("### SQL gerado")
        st.code(final_query, language='sql')
        
        resultado = final_state.get('result')
        if isinstance(resultado, str):
            st.write("### Output:")
            st.write(resultado)  
        else:
            if resultado.empty:
                st.write("### Output:")
                st.write("O retorno da query foi vazio.")
            else:
                st.write("### Output:")
                st.dataframe(resultado, hide_index=True)
    else:
        st.warning("Por favor digite algo.")
