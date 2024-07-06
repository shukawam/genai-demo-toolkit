import os
from dotenv import load_dotenv

import streamlit as st
from langchain_community.vectorstores.oraclevs import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
import oracledb

from langchain_community.embeddings.oci_generative_ai import OCIGenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

_ = load_dotenv()
# for Oracle Database 23ai
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
dsn = os.getenv("DSN")
config_dir = os.getenv("CONFIG_DIR")
wallet_dir = os.getenv("WALLET_DIR")
wallet_password = os.getenv("WALLET_PASSWORD")
table_name = os.getenv("TABLE_NAME")
# for OCI Generative AI Service
compartment_id = os.getenv("COMPARTMENT_ID")
service_endpoint = os.getenv("SERVICE_ENDPOINT")

st.title("Chat demo")
st.caption("""
    OCI Generative AI Service と Oracle Database 23ai(ADB-S) を用いた RAG 構成のチャットボットです。 
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar.container():
    with st.sidebar:
        st.sidebar.markdown("## Vector Search Options")
        is_vector_search = st.sidebar.radio(label="Use Vector Search", options=[True, False], horizontal=True)
        fetch_k = st.sidebar.slider(label="Fetch k", min_value=1, max_value=20, value=5, step=1)
        st.sidebar.markdown("## LLM Options")
        streaming = st.sidebar.radio(label="Streaming", options=[True, False], disabled=True, horizontal=True)
        max_tokens = st.sidebar.number_input(label="Max Tokens", min_value=10, max_value=1024, value=500, step=1)
        temperature = st.sidebar.slider(label="Temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
        k = st.sidebar.slider(label="Top k", min_value=0, max_value=500, value=0, step=1)
        p = st.sidebar.slider(label="Top p", min_value=0.0, max_value=0.99, value=0.75, step=0.01)
        frequency_penalty = st.sidebar.slider(label="Frequency Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
        presence_penalty = st.sidebar.slider(label="Presence Penalty", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

connection = oracledb.connect(
    dsn=dsn,
    user=username,
    password=password,
    config_dir=config_dir,
    wallet_location=wallet_dir,
    wallet_password=wallet_password
)
embedding_function = OCIGenAIEmbeddings(
    auth_type="INSTANCE_PRINCIPAL",
    model_id="cohere.embed-multilingual-v3.0",
    service_endpoint=service_endpoint,
    compartment_id=compartment_id,
)
oracle_vs = OracleVS(
    client=connection,
    embedding_function=embedding_function,
    table_name=table_name,
    distance_strategy=DistanceStrategy.COSINE,
    query="What is Oracle Database?"
)
chat = ChatOCIGenAI(
    auth_type="INSTANCE_PRINCIPAL",
    service_endpoint=service_endpoint,
    compartment_id=compartment_id,
    model_id="cohere.command-r-plus",
    is_stream=True,
    model_kwargs={
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": p,
        "top_k": k,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }
)

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if is_vector_search == True:
            template = """
                可能な限り、検索によって得られたコンテキスト情報を使って質問に回答してください。
                コンテキスト: {context}
                ---
                質問: {query}
            """
            prompt_template = PromptTemplate.from_template(
                template=template,
            )
            chain = (
                {"query": RunnablePassthrough(), "context": oracle_vs.as_retriever()}
                | prompt_template
                | chat
                | StrOutputParser()
            )
            res = chain.stream(prompt)
        else:
            template = """
                質問: {{query}}
            """
            prompt_template = PromptTemplate.from_template(
                template=template,
                template_format="jinja2"
            )
            chain = (
                {"query": RunnablePassthrough()}
                | prompt_template
                | chat
                | StrOutputParser()
            )
            res = chain.stream(prompt)
        message = ""
        for chunk in res:
            message += chunk
            message_placeholder.markdown(message)
        st.session_state.messages.append({"role": "assistant", "content": message})

