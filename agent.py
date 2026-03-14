from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from tools import (get_popular_movies, get_similar_movies, add_movie_to_cart, view_cart, checkout, init_db)

init_db()

store = {}

tools = [get_popular_movies, get_similar_movies, add_movie_to_cart, view_cart, checkout]

llm = ChatOllama(model="ministral-3:8b", temperature=0)

llm_with_tools = llm.bind_tools(tools)

tools_by_name = {
                "get_popular_movies": get_popular_movies,
                "get_similar_movies": get_similar_movies,
                "add_movie_to_cart": add_movie_to_cart,
                "view_cart": view_cart,
                "checkout": checkout
}

def process_message(user_input: str, session_id: str) -> str:
    if session_id not in store:
        store[session_id] = []
    history = store[session_id]

    if len(history) == 0:
        history.append(SystemMessage(content=f"""You are a movie recommendation assistant with access to a specific Netflix movie database from 2006. 
        CRITICAL RULES:
        1. You MUST use the provided tools to get movie information. NEVER make up movie recommendations from your training data.
        2. If a movie is not found in the database, say "I couldn't find that movie in our database" and suggest using the get_popular_movies tool instead.
        3. Only recommend movies that the tools return to you.
        4. The user's session_id is: {session_id}"""))


    history.append(HumanMessage(content=user_input))

    ai_response = llm_with_tools.invoke(history)
    history.append(ai_response)

    if ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")
            name = tool_call["name"]
            args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool_to_run = tools_by_name[name]
            result = tool_to_run.invoke(args)
            print(f"Tool result: {result}")
            history.append(ToolMessage(content=result, tool_call_id=tool_call_id))

        ai_response = llm_with_tools.invoke(history)
        history.append(ai_response)
    return ai_response.content