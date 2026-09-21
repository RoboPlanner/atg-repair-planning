"""Normalize archived candidate dataflow. Reference records are not an input."""
from collections import Counter
import hashlib,re
from atomic_task.schema import AtomicTaskGraph


def adapt(candidate,tools):
    nodes=candidate.get('task_nodes');links=candidate.get('task_links')
    if not isinstance(nodes,list) or not nodes or not isinstance(links,list):raise ValueError('invalid_node_or_link_container')
    names=[n.get('task') if isinstance(n,dict) else None for n in nodes]
    if any(not isinstance(n,str) or n not in tools for n in names):raise ValueError('unknown_tool')
    if len(set(names))!=len(names):raise ValueError('ambiguous_repeated_tool')
    nameid={name:f't{i+1}' for i,name in enumerate(names)}
    atg=[];s0=set();signature_errors=[]
    for i,node in enumerate(nodes):
        args=node.get('arguments')
        if not isinstance(args,list) or any(not isinstance(v,str) for v in args):raise ValueError('invalid_argument_container')
        pre=[];types=[]
        for arg in args:
            match=re.fullmatch(r'<node-(\d+)>',arg.strip())
            if match:
                k=int(match[1])
                if k>=len(nodes) or k==i:raise ValueError('invalid_node_reference')
                pre.append(f'output:{k}')
                outs=tools[names[k]]['output-type']
                types.append(outs[0] if len(outs)==1 else 'unknown')
            else:
                if '<node-' in arg:raise ValueError('unsupported_embedded_reference')
                key='literal:'+hashlib.sha256(arg.encode()).hexdigest()
                pre.append(key);s0.add(key)
                types.append('image' if re.search(r'\.(jpg|jpeg|png|bmp)$',arg,re.I) else
                    'audio' if re.search(r'\.(wav|mp3|flac)$',arg,re.I) else
                    'video' if re.search(r'\.(mp4|avi|mov)$',arg,re.I) else 'text')
        if not pre:raise ValueError('empty_arguments')
        if Counter(types)!=Counter(tools[names[i]]['input-type']):signature_errors.append(i)
        atg.append({'id':f't{i+1}','action':names[i],'object':f'call:{i}','pre_state':sorted(set(pre)),
                    'post_state':[f'output:{i}'],'duration':1,'resource':[],'candidate_arm':['left','right'],'mode':'single'})
    edges=[]
    for link in links:
        if not isinstance(link,dict) or link.get('source') not in nameid or link.get('target') not in nameid:raise ValueError('unresolved_link_endpoint')
        u,v=link['source'],link['target']
        edges.append({'source':nameid[u],'target':nameid[v],'type':'state_support','state':f'output:{names.index(u)}'})
    # Do not silently deduplicate model relation declarations.
    return AtomicTaskGraph.from_dict({'nodes':atg,'edges':edges}),s0,{f'output:{i}' for i in range(len(nodes))},signature_errors


def raw_sets(candidate):
    ns=candidate.get('task_nodes',[]);es=candidate.get('task_links',[])
    nodes={n['task'] for n in ns if isinstance(n,dict) and isinstance(n.get('task'),str)} if isinstance(ns,list) else set()
    edges={(e['source'],e['target']) for e in es if isinstance(e,dict) and isinstance(e.get('source'),str) and isinstance(e.get('target'),str)} if isinstance(es,list) else set()
    return nodes,edges


def graph_sets(graph):
    names={n.id:n.action for n in graph.nodes}
    return set(names.values()),{(names[e.source],names[e.target]) for e in graph.edges if e.type=='state_support'}


def f1(pred,ref):
    return 2*len(pred&ref)/(len(pred)+len(ref)) if pred or ref else 1.0
