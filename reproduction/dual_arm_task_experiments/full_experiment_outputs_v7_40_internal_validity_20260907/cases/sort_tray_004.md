# sort_tray_004

Instruction: Stabilize the tray, sort the red and blue blocks into bins, grasp the lid, and cover the tray using both arms.

## Atomic Nodes
- v1: stabilize(tray), pre=['tray_on_table'], post=['tray_stable'], executors=['left'], resources=['tray']
- v2: move(red_block), pre=['red_block_on_tray', 'tray_stable'], post=['red_block_in_left_bin'], executors=['right'], resources=['red_block', 'tray']
- v3: move(blue_block), pre=['blue_block_on_tray', 'tray_stable'], post=['blue_block_in_right_bin'], executors=['left', 'right'], resources=['blue_block', 'tray']
- v4: grasp(lid), pre=['lid_on_table'], post=['lid_grasped'], executors=['right'], resources=['lid']
- v5: cover(tray), pre=['red_block_in_left_bin', 'blue_block_in_right_bin', 'lid_grasped', 'tray_stable'], post=['tray_covered'], executors=['both'], resources=['tray']

## Optimized Edges
- v1 -> v2: state_support, state=tray_stable, resource=None
- v1 -> v3: state_support, state=tray_stable, resource=None
- v3 -> v5: state_support, state=blue_block_in_right_bin, resource=None
- v4 -> v5: state_support, state=lid_grasped, resource=None
- v1 -> v5: state_support, state=tray_stable, resource=None
- v2 -> v5: state_support, state=red_block_in_left_bin, resource=None
- v3 -> v5: synchronization, state=blue_block_in_right_bin, resource=None
- v4 -> v5: synchronization, state=lid_grasped, resource=None
- v2 -> v5: synchronization, state=red_block_in_left_bin, resource=None
- v1 -> v5: synchronization, state=tray_stable, resource=None
- v3 -> v2: resource_mutex, state=None, resource=tray

## Parallel Plan
- v1: 0.00 -> 1.72, executors=['left'], resources=['tray']
- v3: 1.72 -> 4.30, executors=['left'], resources=['blue_block', 'tray']
- v2: 4.30 -> 6.94, executors=['right'], resources=['red_block', 'tray']
- v4: 6.94 -> 8.96, executors=['right'], resources=['lid']
- v5: 8.96 -> 12.58, executors=['left', 'right'], resources=['tray']

Removed false-parallel pairs: []
Released parallel pairs: [('v1', 'v4'), ('v3', 'v4')]
