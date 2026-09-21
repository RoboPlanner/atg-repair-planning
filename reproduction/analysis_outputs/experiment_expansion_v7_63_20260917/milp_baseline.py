"""Same-graph MILP scheduler via scipy.optimize.milp (HiGHS).

All four accepted relation types remain fixed precedence constraints. Binary arm
choices implement Cand; cooperative nodes occupy both L and R. A shared order
binary per incomparable pair activates no-overlap on each selected common arm
or declared shared resource. Big-M is a feasible all-serial horizon sum(d).
"""
import itertools,time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import lil_matrix


def solve(graph,time_limit=10):
    begin=time.perf_counter()
    nodes=graph.nodes;n=len(nodes);horizon=sum(x.duration for x in nodes)
    index={node.id:i for i,node in enumerate(nodes)}
    variables=n+1;flex={}
    for i,node in enumerate(nodes):
        if node.mode=='single' and set(node.candidate_arm)=={'left','right'}:
            flex[i]=variables;variables+=1
    successors={i:set() for i in range(n)}
    for e in graph.edges:successors[index[e.source]].add(index[e.target])
    reach={i:set(v) for i,v in successors.items()}
    for k in range(n):
        for i in range(n):
            if k in reach[i]:reach[i].update(reach[k])
    def occupancy(i,arm):
        node=nodes[i]
        if node.mode=='cooperative':return 1,{}
        if i in flex:return (0,{flex[i]:1}) if arm=='left' else (1,{flex[i]:-1})
        return int(arm in node.candidate_arm),{}
    pairs=[]
    for i,j in itertools.combinations(range(n),2):
        if j in reach[i] or i in reach[j]:continue
        common_resource=bool(set(nodes[i].resource)&set(nodes[j].resource))
        arms=[arm for arm in ['left','right'] if any(occupancy(i,arm)) and any(occupancy(j,arm))]
        if common_resource or arms:
            pairs.append((i,j,variables,common_resource,arms));variables+=1
    rows=[];upper=[]
    def add(coeff,bound):rows.append(coeff);upper.append(bound)
    for i,node in enumerate(nodes):add({i:1,n:-1},-node.duration)
    for i,targets in successors.items():
        for j in targets:add({i:1,j:-1},-nodes[i].duration)
    for i,j,y,shared,arms in pairs:
        if shared:
            add({i:1,j:-1,y:horizon},horizon-nodes[i].duration)
            add({j:1,i:-1,y:-horizon},-nodes[j].duration)
        else:
            for arm in arms:
                ci,ai=occupancy(i,arm);cj,aj=occupancy(j,arm)
                for coeff,bound in [({i:1,j:-1,y:horizon},3*horizon-nodes[i].duration),
                                    ({j:1,i:-1,y:-horizon},2*horizon-nodes[j].duration)]:
                    for var,mult in list(ai.items())+list(aj.items()):coeff[var]=coeff.get(var,0)+horizon*mult
                    add(coeff,bound-horizon*(ci+cj))
    matrix=lil_matrix((len(rows),variables),dtype=float)
    for row,coeff in enumerate(rows):
        for col,value in coeff.items():matrix[row,col]=value
    lb=np.zeros(variables);ub=np.ones(variables);ub[:n+1]=horizon
    integral=np.ones(variables);integral[:n+1]=0
    objective=np.zeros(variables);objective[n]=1
    result=milp(objective,integrality=integral,bounds=Bounds(lb,ub),
                constraints=LinearConstraint(matrix.tocsc(),np.full(len(rows),-np.inf),np.array(upper)),
                options={'time_limit':time_limit,'mip_rel_gap':0.0,'presolve':True})
    output={'status':int(result.status),'success':bool(result.success),'message':result.message,
            'objective':float(result.fun) if result.fun is not None else None,
            'dual_bound':float(result.mip_dual_bound) if getattr(result,'mip_dual_bound',None) is not None else None,
            'mip_gap':float(result.mip_gap) if getattr(result,'mip_gap',None) is not None else None,
            'mip_node_count':int(result.mip_node_count) if getattr(result,'mip_node_count',None) is not None else None,
            'elapsed_seconds_build_and_solve':time.perf_counter()-begin,'variables':variables,'constraints':len(rows),
            'time_limit_seconds':time_limit,'big_M_serial_horizon':horizon,'raw_x':result.x.tolist() if result.x is not None else None,
            'schedule':None}
    if result.x is not None:
        steps=[]
        for i,node in enumerate(nodes):
            start=float(result.x[i]);start=0.0 if abs(start)<1e-9 else start
            if node.mode=='cooperative':arms=['left','right']
            elif i in flex:arms=['left'] if result.x[flex[i]]>=0.5 else ['right']
            else:arms=list(node.candidate_arm)
            steps.append({'node_id':node.id,'start':start,'finish':start+node.duration,
                          'executors':arms,'resources':list(node.resource)})
        output['raw_schedule']={'estimated_makespan':max(s['finish'] for s in steps),'items':steps}
        # Reconstruct exact earliest starts from the solver's integer decisions.
        # This removes primal floating-point tolerance errors without changing
        # arm assignments, pair orders, durations, or fixed graph precedence.
        preds={i:{u for u,targets in successors.items() if i in targets} for i in range(n)}
        for i,j,y,shared,arms in pairs:
            selected_common=shared or bool(set(steps[i]['executors'])&set(steps[j]['executors']))
            if selected_common:
                source,target=(i,j) if result.x[y]>=0.5 else (j,i)
                preds[target].add(source)
        remaining=set(range(n));ends={};polished=[]
        while remaining:
            ready=sorted(i for i in remaining if preds[i]<=ends.keys())
            if not ready:
                output['reconstruction_error']='Integer decisions induce a cycle'
                return output
            for i in ready:
                start=max((ends[p] for p in preds[i]),default=0.0)
                step=dict(steps[i]);step['start']=start;step['finish']=start+nodes[i].duration
                polished.append(step);ends[i]=step['finish'];remaining.remove(i)
        finish=max(ends.values())
        output['schedule']={'estimated_makespan':finish,'items':polished}
        output['reconstruction']='earliest starts for solver-selected arm assignments and pair orders'
        output['reconstructed_upper_minus_dual_bound']=finish-output['dual_bound'] if output['dual_bound'] is not None else None
        output['optimal_within_tolerance']=bool(result.status==0 and output['dual_bound'] is not None and
            abs(finish-output['dual_bound'])<=1e-6*max(1.0,finish))
    return output
