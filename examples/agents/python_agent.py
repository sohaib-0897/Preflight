from preflight_sdk.server import serve
from offline import response
async def invoke(inputs,seed):
    result=response(inputs)
    result['events']=[{'kind':'agent_invocation','framework':'python','seed':seed}]
    return result
if __name__=='__main__':serve(invoke)
