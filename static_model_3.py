import streamlit as st
import pandas as pd
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import mykey

# Set up the OpenAI API key
OPENAI_API_KEY = mykey.OPENAI_API_KEY

# Set up the SQLite connection and load the data
sqlite_connection = sqlite3.connect("ksa.db")
excel_file_path = r"RBLatest52Weeks_Data.xlsx"
data = pd.read_excel(excel_file_path)

# Write the data to the SQLite database
data.to_sql("Sales", con=sqlite_connection, index=False, if_exists="replace")

# Query data from SQLite table and store it in a pandas DataFrame
df = pd.read_sql("SELECT * FROM Sales", sqlite_connection)

def initialize_agent(model_name):
    """Initialize the ChatOpenAI agent with the specified model."""
    llm_code = ChatOpenAI(temperature=0.0, model=model_name, openai_api_key=OPENAI_API_KEY)
    agent = create_pandas_dataframe_agent(
        llm_code,
        df,
        agent_type="tool-calling",
        verbose=True
    )
    return agent

agent = initialize_agent("gpt-3.5-turbo-0125")



# Streamlit UI
st.title("Data analysis App")
st.write("This app uses an AI agent to answer queries about sales data.")

# Select model
model_options = ["gpt-3.5-turbo-0613","gpt-4-0613", "gpt-4o-2024-05-13","gpt-3.5-turbo-0125","gpt-4-turbo-2024-04-09"]
# model_name = st.selectbox("Select the model:", options=model_options)

# Input query
query = st.text_input("Enter your query:")
visualization_keywords = [
    'graph', 'plot', 'chart', 'charts', 'plt',
    'visualize', 'display', 'illustrate', 'depict', 'render',
    'diagram', 'map', 'graphical', 'visual', 'image', 'scatter',
    'bar', 'line', 'pie', 'histogram', 'heatmap', 'boxplot', 'bubble',
    'area', 'radar', 'doughnut', 'treemap'
]

# transformation_keywords = [
#     'change', 'update', 'transform', 'modify', 'adjust', 'infer', 'edit',
#     'revise', 'alter', 'convert', 'switch', 'adapt', 'refine', 'reshape',
#     'tweak', 'amend', 'rework', 'reform', 'redesign', 'edit', 'improve',
#     'upgrade', 'enhance', 'optimize', 'reconstruct'
# ]

# table_keywords = [
#     'tabular', 'table', 'spreadsheet', 'matrix', 'grid', 'sheet', 'tabulation',
#     'list', 'record', 'database', 'rows', 'columns', 'ledger', 'catalog',
#     'register', 'inventory', 'log', 'index', 'schedule', 'plan', 'file',
#     'format', 'layout', 'structure'
# ]

if any(keyword in query for keyword in visualization_keywords):
    query += r'Do not draw the chart. Just Provide all data in JSON Format strictly having these keys only (do not make spelling mistake in any key). Take this format as example and do not add anything in this json - { "title": " ", "labels": [  ], "backgroundColor": [ ], "chartsData": [  ], "chartType": " ", "displayLegend": " " }'

# if any(keyword in query for keyword in transformation_keywords):
    # query += r'Take this json response for a chart and apply the query. Give the response strictly in the json format provide to you'

# if any(keyword in query for keyword in table_keywords):
#     query += r''' Provide the rows and header names according to query in the following tabular JSON format strictly : '
#         '{ "headers": ["", "",...], '
#         '"rows": [["", "", ..], '
#         '["", "", ....], ....] }'''
    
# Button to run the query
if st.button("Run Query"):
    
    response = agent.invoke(query)
    st.write("Response:", response)


