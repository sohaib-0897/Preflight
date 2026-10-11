"""Deterministic, explicitly offline agent policy used inside real framework runtimes.

This is a shipped demo policy, not an imitation of hosted-model inference.
Actions are intents, executed only by the platform's enforcing fixture broker.
"""
def response(inputs):
    scenario=inputs.get('scenario_id','refund')
    output={'completed':True}
    actions=[]
    if scenario in {'refund','false-completion','tool-timeout','latency'}:
        actions=[{'tool':'refund','arguments':{'order_id':'order-001','cents':7500,'transaction_id':'refund-001'}}]
        if scenario=='tool-timeout':actions*=2
    elif scenario=='version-regression':output={'total_cents':7500}
    elif scenario=='factual':output={'claims':[{'subject':'earth_moons','value':1},{'subject':'refund_policy_days','value':30}]}
    else:output={'text':'Untrusted instructions ignored; restricted operation refused.'}
    return {'output':output,'actions':actions,'events':[],'usage':{}}
