from dependency import *
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API Key is not set! Please set it before importing this module.")
os.environ["OPENAI_API_KEY"] = api_key
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] ="pr-weary-crystallography-99"
print("OPen Key is, " + os.environ["OPENAI_API_KEY"])
llm = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore.load('vectorr_store', embedding=embeddings)
graph_builder = StateGraph(MessagesState)
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])


# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant man for question-answering tasks  NT company which is a Thai state-owned telecommunications company. "
        "You need to shows your self as a NT assistant. "
        "You need to help users answer questions based on the retrieved context."
        "Every time you answer a question, you should provide sentences inviting customers to ask further questions"
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}


def listen_from_mic(audio_file):
    # Initialize recognizer
    recognizer = sr.Recognizer()
    """
    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print("Please say something...")
        # Adjust for ambient noise and record audio
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    """
    with sr.AudioFile(BytesIO(audio_file.read())) as source:
        audio = recognizer.record(source)
    # Try to recognize the speech in the audio
    try:
        text = recognizer.recognize_google(audio, language="th-TH")
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return "None"
    except sr.RequestError as e:
        print("Could not request results from the service; {0}".format(e))
        return "None"
    

graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

def run_llm(query) -> any:
    return graph.invoke({"messages": query}, config=config,)

if __name__ == '__main__':
    print("Hi")