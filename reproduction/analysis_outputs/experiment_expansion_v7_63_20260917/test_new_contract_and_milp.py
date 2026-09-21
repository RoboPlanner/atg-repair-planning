import itertools,random,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'implementation_v7_63'))
from atomic_task.schema import AtomicTaskGraph,AtomicTaskNode,AtomicTaskEdge
from atomic_task.pipeline import run_verified_atg
from milp_baseline import solve

def node(n,d=1,mode='single',arms=None,res=None):
    return AtomicTaskNode(n,'act',n,['seed'],[n+'_done'],d,res or [],arms or (['both'] if mode=='cooperative' else ['left','right']),mode)
def brute(graph):
    nodes=graph.nodes;nmap=graph.node_map;best=float('inf')
    choices=[(['left','right'],) if n.mode=='cooperative' else tuple([a] for a in n.candidate_arm) for n in nodes]
    for armsets in itertools.product(*choices):
        assignment=dict(zip([n.id for n in nodes],armsets))
        for order in itertools.permutations([n.id for n in nodes]):
            pos={s:i for i,s in enumerate(order)}
            if any(pos[e.source]>=pos[e.target] for e in graph.edges):continue
            ends={};occupied={}
            for nid in order:
                n=nmap[nid];uses=assignment[nid]+['res:'+r for r in n.resource]
                start=max([ends[e.source] for e in graph.edges if e.target==nid]+[occupied.get(k,0) for k in uses]+[0])
                end=start+n.duration;ends[nid]=end
                for k in uses:occupied[k]=end
            best=min(best,max(ends.values()))
    return best

class ExportContract(unittest.TestCase):
    def test_sub_millisecond_single_interval_preserved(self):
        g=AtomicTaskGraph([node('t1',.0004,arms=['left'])],[])
        r=run_verified_atg(g,{'seed'},{'t1_done'})
        self.assertTrue(r.accepted);s=r.to_dict()['schedule']
        self.assertEqual(s['items'][0]['finish'],.0004);self.assertEqual(s['estimated_makespan'],.0004)
    def test_tiny_cooperative_chain_export_preserved(self):
        a=node('t1',.0004,arms=['left']);b=node('t2',.0006,'cooperative');b.pre_state=['t1_done']
        r=run_verified_atg(AtomicTaskGraph([a,b],[]),{'seed'},{'t2_done'})
        self.assertTrue(r.accepted);s=r.to_dict()['schedule']['items']
        self.assertEqual(s[1]['executors'],['left','right']);self.assertAlmostEqual(s[1]['finish']-s[1]['start'],.0006)
    def test_irrelevant_labels_fail_before_repair(self):
        for typ,state,res in [('order','extra',None),('order',None,'r'),('state_support','t1_done','r'),('synchronization','t1_done','r'),('resource_mutex','extra','r')]:
            with self.subTest(typ=typ,state=state,res=res):
                g=AtomicTaskGraph([node('t1',res=['r']),node('t2',res=['r'])],[AtomicTaskEdge('t1','t2',typ,state=state,resource=res)])
                r=run_verified_atg(g,{'seed'},{'t2_done'})
                self.assertFalse(r.accepted);self.assertIsNone(r.schedule);self.assertIsNone(r.audit)

class MILPTests(unittest.TestCase):
    def check(self,g):
        expected=brute(g);r=solve(g)
        self.assertEqual(r['status'],0,r)
        self.assertAlmostEqual(r['schedule']['estimated_makespan'],expected,places=9)
        self.assertTrue(r['optimal_within_tolerance'])
    def test_flexible_allocation(self):self.check(AtomicTaskGraph([node('t1',3),node('t2',2),node('t3',2)],[]))
    def test_cooperative_occupancy(self):self.check(AtomicTaskGraph([node('t1',3,'cooperative'),node('t2',2,arms=['left']),node('t3',2,arms=['right'])],[]))
    def test_shared_resource(self):self.check(AtomicTaskGraph([node('t1',3,res=['r']),node('t2',2,res=['r']),node('t3',2)],[]))
    def test_mixed_flexible_and_fixed(self):self.check(AtomicTaskGraph([node('t1',5,arms=['left']),node('t2',4),node('t3',2,arms=['right'])],[]))
    def test_fixed_precedence(self):self.check(AtomicTaskGraph([node('t1',3),node('t2',2),node('t3',4),node('t4',1)], [AtomicTaskEdge('t1','t3','order'),AtomicTaskEdge('t2','t4','order')]))
    def test_small_exhaustive_crosscheck(self):
        rng=random.Random(617)
        for case in range(8):
            ns=[node(f't{i}',rng.randint(1,4),'cooperative' if case%3==0 and i==0 else 'single',
                     res=['tool'] if i in [1,3] else []) for i in range(5)]
            edges=[AtomicTaskEdge('t0','t2','order'),AtomicTaskEdge('t1','t4','order')]
            with self.subTest(case=case):self.check(AtomicTaskGraph(ns,edges))

if __name__=='__main__':unittest.main(verbosity=2)
