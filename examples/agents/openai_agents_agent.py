import json
from agents import Agent, Model, ModelResponse, Usage, function_tool, set_tracing_disabled
from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseFunctionToolCall,
)
from preflight_adapters import OpenAIAgentsAdapter
from preflight_sdk.server import serve
from offline import response

set_tracing_disabled(True)  # No telemetry upload or hosted model invocation in the offline example.


async def invoke(inputs, seed):
    @function_tool
    def propose_actions() -> str:
        """Plan authorized fixture actions; the platform broker applies them."""
        return json.dumps(response(inputs))

    class OfflineModel(Model):
        async def get_response(
            self,
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            tracing,
            **kwargs,
        ):
            returned = (
                next(
                    (
                        item
                        for item in input
                        if isinstance(item, dict) and item.get("type") == "function_call_output"
                    ),
                    None,
                )
                if isinstance(input, list)
                else None
            )
            if returned:
                output = [
                    ResponseOutputMessage(
                        id="offline-message",
                        role="assistant",
                        type="message",
                        status="completed",
                        content=[
                            ResponseOutputText(
                                type="output_text", text=returned["output"], annotations=[]
                            )
                        ],
                    )
                ]
            else:
                output = [
                    ResponseFunctionToolCall(
                        id="offline-tool",
                        type="function_call",
                        name="propose_actions",
                        call_id="offline-call",
                        arguments="{}",
                    )
                ]
            return ModelResponse(output=output, usage=Usage(requests=1), response_id=None)

        async def stream_response(self, *args, **kwargs):
            raise NotImplementedError("Offline example uses nonstreaming execution")
            yield

    result = await OpenAIAgentsAdapter(
        Agent(
            name="Offline fixture planner",
            instructions="Plan permitted actions only.",
            model=OfflineModel(),
            tools=[propose_actions],
        )
    ).invoke({"prompt": inputs["prompt"]}, seed)
    contract = json.loads(result.output)
    return {
        **contract,
        "events": result.events,
        "metadata": {
            "framework": "openai-agents",
            "inference": "offline deterministic model; no hosted call",
        },
    }


if __name__ == "__main__":
    serve(invoke)
