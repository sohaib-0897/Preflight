import json
import os
os.environ['OTEL_SDK_DISABLED']='true'
os.environ['CREWAI_TELEMETRY_ENABLED']='false'
os.environ['CREWAI_DISABLE_TELEMETRY']='true'
from crewai import Agent,Crew,Task,BaseLLM
from preflight_adapters import CrewAIAdapter
from preflight_sdk.server import serve
from offline import response

async def invoke(inputs,seed):
    calls=[]
    class OfflinePolicy(BaseLLM):
        def __init__(self):super().__init__(model='preflight/offline-deterministic',temperature=0)
        def call(self,messages,tools=None,callbacks=None,available_functions=None,**kwargs):
            calls.append({'kind':'model_invocation','model':'offline deterministic policy','provider':'local shipped policy','hosted_model_called':False})
            return 'Final Answer: '+json.dumps(response(inputs))
        def supports_function_calling(self):return False
        def get_context_window_size(self):return 8192
    agent=Agent(role='Authorized fixture planner',goal='Plan only permitted fixture actions',backstory='Deterministic offline integration example',llm=OfflinePolicy(),max_iter=2,allow_delegation=False,verbose=False)
    task=Task(description=inputs['prompt'],expected_output='JSON object with output, actions, events and usage',agent=agent)
    result=await CrewAIAdapter(Crew(agents=[agent],tasks=[task],verbose=False,cache=False)).invoke(inputs,seed)
    contract=json.loads(result.output)
    return {**contract,'events':calls+result.events,'metadata':{'framework':'crewai','inference':'offline deterministic policy'}}

if __name__=='__main__':serve(invoke)
