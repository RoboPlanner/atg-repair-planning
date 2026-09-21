import unittest,json,copy
from pathlib import Path
from external_discrete import independent_source_audit, recipe_case
W=Path(__file__).resolve().parent
CASES={c['id']:c for c in json.loads((W/'results/external_discrete_run01/frozen_cases.json').read_text(encoding='utf-8'))}
PLANS={d['metrics']['id']:d['schedule'] for d in [json.loads(s) for s in (W/'results/external_discrete_run01/details.jsonl').read_text(encoding='utf-8').splitlines()] if d['metrics']['method']=='full'}
class IndependentReferenceTests(unittest.TestCase):
    def test_all_reported_plans_match_public_reference(self):
        for name,c in CASES.items():self.assertTrue(independent_source_audit(c,PLANS[name])['valid'],name)
    def test_joint_operation_cannot_be_assigned_one_unit(self):
        p=copy.deepcopy(PLANS['pair_assembly']);p['items'][0]['executors']=['left']
        self.assertIn('source simultaneous arity',independent_source_audit(CASES['pair_assembly'],p)['issues'])
    def test_source_duration_is_not_inferred_from_candidate(self):
        c=copy.deepcopy(CASES['pair_assembly']);c['graph']['nodes'][0]['duration']=1
        p=copy.deepcopy(PLANS['pair_assembly']);p['items'][0]['finish']=1;p['estimated_makespan']=1
        self.assertIn('source duration/interval',independent_source_audit(c,p)['issues'])
    def test_machine_resource_omission_is_detected(self):
        p=copy.deepcopy(PLANS['ft06']);p['items'][0]['resources']=[]
        self.assertIn('source resource declaration',independent_source_audit(CASES['ft06'],p)['issues'])
    def test_machine_overlap_uses_original_matrix(self):
        p=copy.deepcopy(PLANS['ft06']);case=CASES['ft06'];items=p['items']
        a=items[0];b=next(s for s in items[1:] if s['resources']==a['resources'])
        d=b['finish']-b['start'];b['start']=a['start'];b['finish']=b['start']+d
        self.assertIn('source resource overlap',independent_source_audit(case,p)['issues'])
    def test_material_consumption_and_goal_are_checked(self):
        p=copy.deepcopy(PLANS['flow_serial_3']);p['items']=p['items'][:-1]
        self.assertIn('source operation coverage',independent_source_audit(CASES['flow_serial_3'],p)['issues'])
    def test_or_precondition_is_checked_at_start(self):
        p=copy.deepcopy(PLANS['public_inclusive_or']);s=next(s for s in p['items'] if s['node_id']=='finish');s['start']=0;s['finish']=2
        issues=independent_source_audit(CASES['public_inclusive_or'],p)['issues']
        self.assertIn('source OR obligation',issues);self.assertIn('source material unavailable',issues)
    def test_xor_is_not_silently_changed_to_or(self):
        ref=copy.deepcopy(CASES['public_inclusive_or']['source_reference']);fin=ref['operations'][-1]
        fin['predecessor_any']=fin.pop('predecessor_any_inclusive')
        with self.assertRaisesRegex(ValueError,'exclusive'):recipe_case(ref,'diagnostic')
if __name__=='__main__':unittest.main()
