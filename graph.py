from langchain_community.document_loaders import PyPDFLoader


import re
from openai import OpenAI
from neo4j import GraphDatabase
uri = "bolt://localhost:7687"  # Update with your Neo4j instance
user = "neo4j"                 # Your username
password = "password"          # Your password




client = OpenAI(api_key="api-key")
#douments loading 


file_path = "./y.pdf"
loader = PyPDFLoader(file_path)

documents = loader.load()

# Extract text from all documents
text_content = ""
for doc in documents:
    text_content += doc.page_content + "\n\n"





    # Remove extra whitespace
text_content = re.sub(r'\s+', ' ', text_content)
    # Remove page numbers (if applicable)
text_content = re.sub(r'Page \d+', '', text_content)


system_prompt = f"""
    you will be given a text that was extracted from a PDF.
    your job is to generate Cypher queries to:
    1. Create nodes for main entities (e.g., people, organizations, topics).
    2. Define relationships between these entities.
    Include properties like names, descriptions, and dates where applicable.

    the cypher queries should be in the following format:
    CREATE (node1:Label1 {{`property1`: "value1", `property2`: "value2"}})
    CREATE (node2:Label2 {{`property1`: "value1", `property2`: "value2"}})
    CREATE (node1)-[:RELATIONSHIP_TYPE]->(node2)

    and not any other text no a single letter or comma or anything else
    """

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text_content}
    ]
)

print(response.choices[0].message.content)

cypher_queries = response.choices[0].message.content

def run_cypher_queries(cypher_queries, uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for query in cypher_queries.split(";"):
            if query.strip():
                session.run(query)
    driver.close()






run_cypher_queries(cypher_queries, uri, user, password)