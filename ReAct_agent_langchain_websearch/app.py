import streamlit as st
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
import requests
from bs4 import BeautifulSoup

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=1000)  # Increase max_tokens for longer responses

# Define Bing Search Scraper (No API Key Needed)
def bing_search_scraper(query):
    url = f"https://www.bing.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("li", class_="b_algo")  # Adjust based on Bing's structure

    search_results = []
    for result in results[:10]:  # Get top 10 results for more information
        title = result.find("h2").get_text() if result.find("h2") else "No title"
        link = result.find("a")["href"] if result.find("a") else "No link"
        snippet = result.find("p").get_text() if result.find("p") else "No description"
        search_results.append(f"**{title}**\n{snippet}\n{link}")

    return "\n\n".join(search_results) if search_results else "No results found."

# Set up search tool
search_tool = Tool(
    name="Bing Search",
    func=bing_search_scraper,
    description="Use this tool to search the web using Bing (no API needed)"
)

tools = [search_tool]

# Set up ReAct agent
agent = initialize_agent(
    tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Streamlit app interface
st.title("ReAct Agent with LangChain (Bing Search)")

st.write("Ask anything, and the agent will fetch the information from Bing.")

user_input = st.text_input("Ask a question:")

if user_input:
    response = agent.run(user_input)
    st.write(f"Response: {response}")
