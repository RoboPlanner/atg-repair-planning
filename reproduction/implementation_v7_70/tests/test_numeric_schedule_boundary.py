import unittest
from atomic_task.pipeline import run_verified_atg

def node(nid, pre, post, duration, arm='left'):
    return dict(id=nid,action='act',object='obj',pre_state=[pre],post_state=[post],
                duration=duration,resource=[],candidate_arm=[arm],mode='single')

class NumericScheduleBoundaryTests(unittest.TestCase):
    def test_positive_duration_must_not_collapse_at_nonzero_start(self):
        graph={'nodes':[node('a','ready','s',1),node('b','s','g',1e-17)],
               'edges':[dict(source='a',target='b',type='state_support',state='s')]}
        result=run_verified_atg(graph,{'ready'},{'g'})
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)
        self.assertTrue(any('duration' in r for r in result.failure_reasons))

    def test_small_but_representable_duration_is_not_blanket_rejected(self):
        graph={'nodes':[node('a','ready','g',1e-17)],'edges':[]}
        result=run_verified_atg(graph,{'ready'},{'g'})
        self.assertTrue(result.accepted)
        self.assertEqual(result.schedule.items[0].finish,1e-17)

    def test_positive_but_inaccurate_interval_is_rejected(self):
        graph={'nodes':[node('a','ready','s',1),node('b','s','g',1e-12)],
               'edges':[dict(source='a',target='b',type='state_support',state='s')]}
        result=run_verified_atg(graph,{'ready'},{'g'})
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)

    def test_finite_nodes_must_not_produce_nonfinite_aggregate(self):
        # Include a single unit: finite busy time / overflowing capacity must not
        # quietly produce an accepted utilization of zero.
        for nodes, goals in [([node('a','ready','ga',1e308)],{'ga'}),
                             ([node('a','ready','ga',1e308),node('b','ready','gb',1e308,'right')],{'ga','gb'})]:
            with self.subTest(nodes=len(nodes)):
                result=run_verified_atg({'nodes':nodes,'edges':[]},{'ready'},goals)
                self.assertFalse(result.accepted)
                self.assertIsNone(result.schedule)

    def test_ordinary_fractional_durations_still_accept(self):
        graph={'nodes':[node('a','ready','s',0.1),node('b','s','g',0.2)],
               'edges':[dict(source='a',target='b',type='state_support',state='s')]}
        result=run_verified_atg(graph,{'ready'},{'g'})
        self.assertTrue(result.accepted)
        self.assertGreater(result.schedule.items[-1].finish,result.schedule.items[-1].start)

if __name__=='__main__':unittest.main()
