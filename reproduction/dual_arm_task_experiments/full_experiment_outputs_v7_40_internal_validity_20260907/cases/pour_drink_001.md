# pour_drink_001

Instruction: Use both arms to stabilize the cup, lift the kettle, pour water, add a tea bag, and stir the drink.

## Atomic Nodes
- v1: stabilize(cup), pre=['cup_on_mat'], post=['cup_stabilized'], executors=['left', 'right'], resources=['cup']
- v2: grasp(kettle), pre=['kettle_on_stand'], post=['kettle_grasped'], executors=['right'], resources=['kettle']
- v3: pour(kettle), pre=['cup_stabilized', 'kettle_grasped', 'water_in_kettle'], post=['cup_filled'], executors=['both'], resources=['cup', 'kettle']
- v4: place(kettle), pre=['kettle_grasped', 'cup_filled'], post=['kettle_returned'], executors=['right'], resources=['kettle']
- v5: insert(tea_bag), pre=['tea_bag_available', 'cup_filled'], post=['tea_bag_in_cup'], executors=['left', 'right'], resources=['tea_bag']
- v6: stir(spoon), pre=['spoon_available', 'tea_bag_in_cup'], post=['drink_ready'], executors=['left', 'right'], resources=['spoon', 'cup']

## Optimized Edges
- v1 -> v3: state_support, state=cup_stabilized, resource=None
- v2 -> v4: state_support, state=kettle_grasped, resource=None
- v3 -> v4: state_support, state=cup_filled, resource=None
- v3 -> v5: state_support, state=cup_filled, resource=None
- v5 -> v6: state_support, state=tea_bag_in_cup, resource=None
- v2 -> v3: state_support, state=kettle_grasped, resource=None
- v1 -> v3: synchronization, state=cup_stabilized, resource=None
- v2 -> v3: synchronization, state=kettle_grasped, resource=None

## Parallel Plan
- v1: 0.00 -> 1.81, executors=['left'], resources=['cup']
- v2: 0.00 -> 2.69, executors=['right'], resources=['kettle']
- v3: 2.69 -> 8.06, executors=['left', 'right'], resources=['cup', 'kettle']
- v4: 8.06 -> 9.77, executors=['right'], resources=['kettle']
- v5: 8.06 -> 9.81, executors=['left'], resources=['tea_bag']
- v6: 9.81 -> 12.49, executors=['left'], resources=['spoon', 'cup']

Removed false-parallel pairs: []
Released parallel pairs: [('v1', 'v2'), ('v4', 'v5'), ('v4', 'v6')]
