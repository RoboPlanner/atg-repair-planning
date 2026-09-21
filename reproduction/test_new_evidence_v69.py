from pathlib import Path
import sys,unittest,copy,inspect,json
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'implementation_v7_69'))
from external_adapter import adapt
from repair_comparators import evaluate,direct_field_match
from atomic_task.schema import AtomicTaskGraph

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tools={'read':{'input-type':['text'],'output-type':['text']},'write':{'input-type':['text'],'output-type':['text']}}
        self.c={'task_nodes':[{'task':'read','arguments':['hello']},{'task':'write','arguments':['<node-0>']}],'task_links':[]}
    def test_missing_link_repaired_from_argument(self):
        g,s0,sg,issues=adapt(self.c,self.tools)
        self.assertFalse(evaluate(g,s0,sg,'audit_only')[1])
        for m in ['field_match','field_match_compressed','full']:
            fixed,plan,_=evaluate(g,s0,sg,m);self.assertIsNotNone(plan)
            self.assertEqual({(e.source,e.target,e.state) for e in fixed.edges},{('t1','t2','output:0')})
        self.assertEqual(g.edges,[])
    def test_rejects_ambiguous_tool_identity(self):
        c=copy.deepcopy(self.c);c['task_nodes'][1]['task']='read'
        with self.assertRaisesRegex(ValueError,'ambiguous_repeated_tool'):adapt(c,self.tools)
    def test_rejects_bad_and_self_references(self):
        for a in ['<node-9>','<node-1>','prefix <node-0>']:
            c=copy.deepcopy(self.c);c['task_nodes'][1]['arguments']=[a]
            with self.assertRaises(ValueError):adapt(c,self.tools)
    def test_reference_not_in_adaptation_or_repair_interface(self):
        self.assertEqual(list(inspect.signature(adapt).parameters),['candidate','tools'])
        self.assertEqual(list(inspect.signature(direct_field_match).parameters),['graph','initial'])
    def test_unit_time_resource_scope(self):
        g,s0,sg,_=adapt(self.c,self.tools)
        self.assertEqual(sg,{'output:0','output:1'})
        self.assertTrue(all(n.duration==1 and n.resource==[] and n.mode=='single' for n in g.nodes))
    def test_archived_denominators_preserved(self):
        for model,archive,adapted in [('CodeLlama-13b',497,234),('mistral-7b',489,67)]:
            rows=[json.loads(s) for s in (W/'results/fair_comparison'/f'external_{model}_details.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(rows),archive*4)
            self.assertEqual(len({str(r['metrics']['id']) for r in rows}),archive)
            for m in ['audit_only','field_match','field_match_compressed','full']:
                rs=[r['metrics'] for r in rows if r['metrics']['method']==m]
                self.assertEqual(len(rs),archive)
                self.assertEqual(sum(r['adapted'] for r in rs),adapted)

if __name__=='__main__':unittest.main(verbosity=2)
