# assemble_bracket_003

Instruction: Position the base plate, pick the bracket and screwdriver, align the bracket with both arms, fasten the screw, and inspect the assembly.

## Atomic Nodes
- v1: place(base_plate), pre=['base_plate_on_table'], post=['base_plate_positioned'], executors=['left', 'right'], resources=['base_plate']
- v2: grasp(bracket), pre=['bracket_on_table'], post=['bracket_grasped'], executors=['right'], resources=['bracket']
- v3: pick(screwdriver), pre=['screwdriver_available'], post=['screwdriver_grasped'], executors=['left', 'right'], resources=['screwdriver']
- v4: align(bracket), pre=['base_plate_positioned', 'bracket_grasped'], post=['bracket_aligned'], executors=['both'], resources=['base_plate', 'bracket']
- v5: fasten(screw), pre=['bracket_aligned', 'screwdriver_grasped'], post=['screw_fastened'], executors=['left', 'right'], resources=['screwdriver']
- v6: inspect(assembly), pre=['screw_fastened'], post=['assembly_ready'], executors=['left', 'right'], resources=['assembly']

## Optimized Edges
- v1 -> v4: state_support, state=base_plate_positioned, resource=None
- v2 -> v4: state_support, state=bracket_grasped, resource=None
- v4 -> v5: state_support, state=bracket_aligned, resource=None
- v3 -> v5: state_support, state=screwdriver_grasped, resource=None
- v5 -> v6: state_support, state=screw_fastened, resource=None
- v1 -> v4: synchronization, state=base_plate_positioned, resource=None
- v2 -> v4: synchronization, state=bracket_grasped, resource=None

## Parallel Plan
- v1: 0.00 -> 1.84, executors=['left'], resources=['base_plate']
- v2: 0.00 -> 1.75, executors=['right'], resources=['bracket']
- v3: 1.75 -> 3.34, executors=['right'], resources=['screwdriver']
- v4: 3.34 -> 8.04, executors=['left', 'right'], resources=['base_plate', 'bracket']
- v5: 8.04 -> 12.07, executors=['left'], resources=['screwdriver']
- v6: 12.07 -> 13.89, executors=['left'], resources=['assembly']

Removed false-parallel pairs: []
Released parallel pairs: [('v1', 'v2'), ('v1', 'v3'), ('v2', 'v3')]
