from langgraph.graph import StateGraph, START, END
from preflight_adapters import LangGraphAdapter
from preflight_sdk.server import serve
from offline import response

builder = StateGraph(dict)
builder.add_node("policy", lambda state: response(state))
builder.add_edge(START, "policy")
builder.add_edge("policy", END)
adapter = LangGraphAdapter(builder.compile())


async def invoke(inputs, seed):
    result = await adapter.invoke(inputs, seed)
    contract = result.output
    return {
        **contract,
        "events": result.events,
        "metadata": {"framework": "langgraph", "inference": "offline deterministic policy"},
    }


if __name__ == "__main__":
    serve(invoke)
