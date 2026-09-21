import unittest
from atomic_task.schema import AtomicTaskNode, AtomicTaskEdge, AtomicTaskGraph
from atomic_task.planning import PlannedStep, schedule_issues
from atomic_task.pipeline import run_verified_atg

def case(duration):
    g=AtomicTaskGraph([
        AtomicTaskNode('t1','produce','x',['ready'],['produced'],duration,[],['left']),
        AtomicTaskNode('t2','consume','x',['produced'],['done'],duration,[],['right']),
    ],[AtomicTaskEdge('t1','t2','state_support',state='produced')])
    items=[PlannedStep('t1','produce','x',0,duration,['left'],[]),
           PlannedStep('t2','consume','x',0,duration,['right'],[])]
    return g,items

class PrecedenceScaleTest(unittest.TestCase):
    def test_overlapping_cross_unit_causal_tasks_are_rejected_at_all_scales(self):
        for duration in (1e-17,1e-10,0.25,1,1e8):
            with self.subTest(duration=duration):
                graph,items=case(duration)
                self.assertTrue(any('precedence' in x for x in schedule_issues(graph,items)))

    def test_exact_boundary_is_valid_at_all_scales(self):
        for duration in (1e-17,1e-10,0.25,1,1e8):
            with self.subTest(duration=duration):
                graph,items=case(duration)
                items[1].start=duration
                items[1].finish=2*duration
                self.assertEqual(schedule_issues(graph,items),[])

    def test_formal_pipeline_produces_exact_causal_boundary(self):
        for duration in (1e-17,1e-10,0.25,1,1e8):
            with self.subTest(duration=duration):
                graph,_=case(duration)
                result=run_verified_atg(graph,{'ready'},{'done'})
                self.assertTrue(result.accepted)
                self.assertEqual(result.schedule.items[0].finish,result.schedule.items[1].start)

if __name__=='__main__':unittest.main()
