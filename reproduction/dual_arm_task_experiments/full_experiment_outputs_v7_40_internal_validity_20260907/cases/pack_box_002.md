# pack_box_002

Instruction: Open the box, pick up the snack and bottle in parallel, place both items inside, and close the box with both arms.

## Atomic Nodes
- v1: open(box), pre=['box_closed'], post=['box_open'], executors=['left', 'right'], resources=['box']
- v2: grasp(snack), pre=['snack_on_table'], post=['snack_grasped'], executors=['left'], resources=['snack']
- v3: grasp(bottle), pre=['bottle_on_table'], post=['bottle_grasped'], executors=['left', 'right'], resources=['bottle']
- v4: place(snack), pre=['box_open', 'snack_grasped'], post=['snack_in_box'], executors=['left'], resources=['snack', 'box']
- v5: place(bottle), pre=['box_open', 'bottle_grasped'], post=['bottle_in_box'], executors=['right'], resources=['bottle']
- v6: close(box), pre=['snack_in_box', 'bottle_in_box'], post=['box_packed'], executors=['both'], resources=['box']

## Optimized Edges
- v1 -> v4: state_support, state=box_open, resource=None
- v2 -> v4: state_support, state=snack_grasped, resource=None
- v1 -> v5: state_support, state=box_open, resource=None
- v4 -> v6: state_support, state=snack_in_box, resource=None
- v5 -> v6: state_support, state=bottle_in_box, resource=None
- v3 -> v5: state_support, state=bottle_grasped, resource=None
- v5 -> v6: synchronization, state=bottle_in_box, resource=None
- v4 -> v6: synchronization, state=snack_in_box, resource=None

## Parallel Plan
- v1: 0.00 -> 1.72, executors=['left'], resources=['box']
- v2: 1.72 -> 3.06, executors=['left'], resources=['snack']
- v3: 0.00 -> 1.64, executors=['right'], resources=['bottle']
- v4: 3.06 -> 4.76, executors=['left'], resources=['snack', 'box']
- v5: 1.72 -> 3.95, executors=['right'], resources=['bottle']
- v6: 4.76 -> 6.97, executors=['left', 'right'], resources=['box']

Removed false-parallel pairs: []
Released parallel pairs: [('v1', 'v2'), ('v1', 'v3'), ('v2', 'v3'), ('v2', 'v5'), ('v3', 'v4'), ('v4', 'v5')]
