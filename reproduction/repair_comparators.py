"""Transparent same-input comparators; no reference graphs are passed here."""
from atomic_task.schema import AtomicTaskEdge, node_sort_key
from atomic_task.verification import graph_schema_issues, joint_graph_audit
from atomic_task.planning import plan_graph, PlanningValidationError
from atomic_task.pipeline import run_verified_atg
from atomic_task.optimization import compress_redundant_order_edges


def direct_field_match(graph, initial, *, avoid_cycles=False):
    g=graph.copy();nm=g.node_map
    # Construct edges from the supplied fields without calling the full repair.
    g.edges=[e for e in g.edges if e.type=='order' or
        (e.type=='state_support' and e.state in set(nm[e.source].post_state)&set(nm[e.target].pre_state)) or
        (e.type=='resource_mutex' and e.resource in set(nm[e.source].resource)&set(nm[e.target].resource))]
    ordered=sorted(g.nodes,key=lambda n:node_sort_key(n.id))
    for target in ordered:
        for state in sorted(set(target.pre_state)-initial):
            if any(e.type=='state_support' and e.target==target.id and e.state==state for e in g.edges):continue
            producer=next((n for n in ordered if n.id!=target.id and state in n.post_state
                           and (not avoid_cycles or not g.has_path(target.id,n.id))),None)
            if producer:g.add_edge(AtomicTaskEdge(producer.id,target.id,'state_support',state=state))
    for e in list(g.edges):
        if e.type=='state_support' and nm[e.target].mode=='cooperative':
            g.add_edge(AtomicTaskEdge(e.source,e.target,'synchronization',state=e.state))
    order=g.topological_order();rank={n:i for i,n in enumerate(order)}
    for a,b in g.incomparable_pairs():
        for resource in sorted(set(nm[a].resource)&set(nm[b].resource)):
            u,v=(a,b) if rank[a]<rank[b] else (b,a)
            g.add_edge(AtomicTaskEdge(u,v,'resource_mutex',resource=resource))
    return g


def evaluate(graph,s0,sg,method):
    if method=='full':
        r=run_verified_atg(graph,s0,sg)
        return r.graph or graph, r.schedule, r.failure_reasons
    g=graph.copy()
    try:
        errors=graph_schema_issues(g,check_relationships=False)
        if errors:return g,None,errors
        if method in ('field_match','field_match_compressed','field_match_acyclic_compressed'):
            g=direct_field_match(g,s0,avoid_cycles=method=='field_match_acyclic_compressed')
            if method in ('field_match_compressed','field_match_acyclic_compressed'):
                g=compress_redundant_order_edges(g,s0,sg)
        elif method!='audit_only':raise ValueError(method)
        q=joint_graph_audit(g,s0,sg)
        if not q.valid:return g,None,q.failure_reasons()
        return g,plan_graph(g,True,s0,sg,strict=True),[]
    except (ValueError,KeyError,TypeError,PlanningValidationError) as exc:
        return g,None,[str(exc)]
