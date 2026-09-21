import unittest
from atomic_task.pipeline import run_verified_atg


def task():
    return {'nodes': [{
        'id': 't1', 'action': 'inspect', 'object': 'part',
        'pre_state': ['inspection_ready'], 'post_state': ['recorded'],
        'duration': 1, 'resource': [], 'candidate_arm': ['left'], 'mode': 'single',
    }], 'edges': []}


class ExplicitTaskContextTests(unittest.TestCase):
    def test_omitted_initial_cannot_invent_missing_precondition(self):
        r=run_verified_atg(task(), goal_states={'recorded'})
        self.assertFalse(r.accepted);self.assertIsNone(r.schedule)
        self.assertTrue(any('initial_states' in s for s in r.failure_reasons))

    def test_omitted_goal_cannot_become_vacuous_goal(self):
        r=run_verified_atg(task(), initial_states={'inspection_ready'})
        self.assertFalse(r.accepted);self.assertIsNone(r.schedule)
        self.assertTrue(any('goal_states' in s for s in r.failure_reasons))

    def test_explicit_empty_initial_is_not_inferred(self):
        r=run_verified_atg(task(), set(), {'recorded'})
        self.assertFalse(r.accepted)
        self.assertTrue(any('inspection_ready' in s for s in r.failure_reasons))

    def test_explicit_empty_goal_and_valid_states_are_allowed(self):
        for goal in [set(), frozenset(), {'recorded'}]:
            with self.subTest(goal=goal):
                self.assertTrue(run_verified_atg(task(), {'inspection_ready'}, goal).accepted)
        self.assertFalse(run_verified_atg(task(), {'inspection_ready'}, {'approved'}).accepted)

    def test_raw_context_types_rejected_without_coercion(self):
        for bad in [None, 'inspection_ready', ['inspection_ready'], {'': 1}, {''}, {True}, {1}]:
            with self.subTest(value=bad):
                r=run_verified_atg(task(), bad, {'recorded'})
                self.assertFalse(r.accepted);self.assertIsNone(r.schedule)
                r=run_verified_atg(task(), {'inspection_ready'}, bad)
                self.assertFalse(r.accepted);self.assertIsNone(r.schedule)


if __name__=='__main__':unittest.main()
