
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage

from app.config.settings import settings


def get_response_from_ai_agents(llm_id, query, allow_search, system_prompt):

    # Initialize Groq LLM
    llm = ChatGroq(
        model=llm_id,
        api_key=settings.GROQ_API_KEY
    )

    # Configure tools
    tools = []

    if allow_search:
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is missing")

        tavily_wrapper = TavilySearchAPIWrapper(
            tavily_api_key=settings.TAVILY_API_KEY
        )

        tavily_tool = TavilySearchResults(
            api_wrapper=tavily_wrapper,
            max_results=2
        )

        tools.append(tavily_tool)

    # Use the parameter supported by your installed LangGraph version
    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=system_prompt or "You are a helpful AI assistant."
    )

    # Convert user queries into HumanMessage objects
    messages = [
        HumanMessage(content=message)
        for message in query
    ]

    # Invoke agent
    response = agent.invoke({
        "messages": messages
    })

    # Extract AI response
    ai_messages = [
        message.content
        for message in response.get("messages", [])
        if isinstance(message, AIMessage) and message.content
    ]

    if not ai_messages:
        raise ValueError("AI Agent returned an empty response")

    return ai_messages[-1]
