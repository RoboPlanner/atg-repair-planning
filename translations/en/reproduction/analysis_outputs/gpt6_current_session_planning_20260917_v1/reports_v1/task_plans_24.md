# GPT-6 conversation plans: all 24 frozen candidates

English reading translation. Candidates were written directly by the GPT-6 assistant in the original conversation. These tables transcribe the frozen JSON without changing nodes, states, resources, candidate units or edges. Duration d is symbolic input time. Each task includes its strict schedule for inspection; formal acceptance does not establish validation of real operations.

## A01 Bracket and base assembly

Prepare the base and bracket separately, then align them using both units. Tighten the two fastening points, inspect the assembly and apply a completion label. Both fastening operations use the same torque tool.

**S₀**: base_available, bracket_available, bolts_available, label_available

**Sg**: bracket_assembly_labeled

**Capacity-one resources**: base, bracket, torque_tool, label_printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | locate base | base | {base_available} | {base_located} | 2 | {base} | {L} | single |
| t2 | prepare bracket | bracket | {bracket_available} | {bracket_prepared} | 2 | {bracket} | {R} | single |
| t3 | align bracket to base | bracket assembly | {base_located, bracket_prepared} | {bracket_aligned} | 3 | {base, bracket} | {B} | cooperative |
| t4 | tighten first fastener | bracket assembly | {bracket_aligned, bolts_available} | {fastener_one_tight} | 2 | {base, torque_tool} | {L, R} | single |
| t5 | tighten second fastener | bracket assembly | {bracket_aligned, bolts_available} | {fastener_two_tight} | 2 | {base, torque_tool} | {R} | single |
| t6 | inspect assembled bracket | bracket assembly | {fastener_one_tight, fastener_two_tight} | {bracket_checked} | 2 | {base, bracket} | {L, R} | single |
| t7 | apply completion label | bracket assembly | {bracket_checked, label_available} | {bracket_assembly_labeled} | 1 | {base, label_printer} | {L} | single |

**Original typed relations**

- E_state: (t1, t3, base_located); (t2, t3, bracket_prepared); (t3, t4, bracket_aligned); (t3, t5, bracket_aligned); (t4, t6, fastener_one_tight); (t5, t6, fastener_two_tight); (t6, t7, bracket_checked)
- E_sync: (t1, t3, base_located); (t2, t3, bracket_prepared)
- E_mutex: (t4, t5, torque_tool)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L+R | 2 | 5 |
| t4 | L | 5 | 7 |
| t5 | R | 7 | 9 |
| t6 | L | 9 | 11 |
| t7 | L | 11 | 12 |

Symbolic makespan 12; fully serial time for the same nodes 14; corresponding speedup 1.1667. Original and post-processed relation sets agree using complete labelled keys.

## A02 Sensor module installation

Baseplate positioning, sensor preinspection and harness preparation can proceed separately. Install the sensor support, secure the module and connect the harness. The support and module share a fastening tool. Finish with an electrical test and sealing label.

**S₀**: plate_available, sensor_available, harness_available, seal_available

**Sg**: sensor_module_sealed

**Capacity-one resources**: plate, sensor, harness, driver, tester, label_printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | locate plate | plate | {plate_available} | {plate_located} | 2 | {plate} | {L} | single |
| t2 | precheck sensor | sensor | {sensor_available} | {sensor_prechecked} | 3 | {sensor} | {R} | single |
| t3 | prepare harness | harness | {harness_available} | {harness_prepared} | 2 | {harness} | {L, R} | single |
| t4 | fasten support | plate | {plate_located} | {support_installed} | 3 | {plate, driver} | {L} | single |
| t5 | fasten sensor module | sensor | {support_installed, sensor_prechecked} | {sensor_installed} | 3 | {sensor, plate, driver} | {R} | single |
| t6 | connect harness | sensor harness | {sensor_installed, harness_prepared} | {harness_connected} | 2 | {sensor, harness} | {L, R} | single |
| t7 | test electrical connection | sensor module | {harness_connected} | {electrical_check_complete} | 4 | {sensor, tester} | {R} | single |
| t8 | print seal record | seal | {electrical_check_complete, seal_available} | {seal_record_printed} | 1 | {label_printer} | {L} | single |
| t9 | seal checked module | sensor module | {electrical_check_complete, seal_record_printed} | {sensor_module_sealed} | 2 | {sensor} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t4, plate_located); (t4, t5, support_installed); (t2, t5, sensor_prechecked); (t5, t6, sensor_installed); (t3, t6, harness_prepared); (t6, t7, harness_connected); (t7, t8, electrical_check_complete); (t7, t9, electrical_check_complete); (t8, t9, seal_record_printed)
- E_sync: ∅
- E_mutex: ∅
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 3 |
| t3 | L | 2 | 4 |
| t4 | L | 4 | 7 |
| t5 | R | 7 | 10 |
| t6 | L | 10 | 12 |
| t7 | R | 12 | 16 |
| t8 | L | 16 | 17 |
| t9 | L | 17 | 19 |

Symbolic makespan 19; fully serial time for the same nodes 22; corresponding speedup 1.1579. Original and post-processed relation sets agree using complete labelled keys.

## A03 Sealed enclosure assembly

Clean the lower shell and inspect the cover separately. Install the seal, close the enclosure using both units, tighten the two cover positions in sequence and perform a leak check. Then transfer the enclosure to the completed-items tray using both units.

**S₀**: lower_shell_available, cover_available, gasket_available, tray_ready

**Sg**: housing_on_finished_tray

**Capacity-one resources**: lower_shell, cover, gasket, driver, leak_tester, finished_tray

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | clean lower shell | lower shell | {lower_shell_available} | {lower_shell_clean} | 3 | {lower_shell} | {L} | single |
| t2 | inspect cover | cover | {cover_available} | {cover_checked} | 2 | {cover} | {R} | single |
| t3 | prepare gasket | gasket | {gasket_available} | {gasket_prepared} | 1 | {gasket} | {R} | single |
| t4 | seat gasket | lower shell | {lower_shell_clean, gasket_prepared} | {gasket_seated} | 2 | {lower_shell, gasket} | {L} | single |
| t5 | close housing | housing | {gasket_seated, cover_checked} | {housing_closed} | 3 | {lower_shell, cover} | {B} | cooperative |
| t6 | tighten first cover position | cover | {housing_closed} | {cover_position_one_tight} | 2 | {cover, driver} | {L} | single |
| t7 | tighten second cover position | cover | {housing_closed} | {cover_position_two_tight} | 2 | {cover, driver} | {R} | single |
| t8 | check housing seal | housing | {cover_position_one_tight, cover_position_two_tight} | {housing_leak_checked} | 4 | {lower_shell, cover, leak_tester} | {L, R} | single |
| t9 | transfer housing to finished tray | housing | {housing_leak_checked, tray_ready} | {housing_on_finished_tray} | 3 | {lower_shell, cover, finished_tray} | {B} | cooperative |

**Original typed relations**

- E_state: (t1, t4, lower_shell_clean); (t3, t4, gasket_prepared); (t4, t5, gasket_seated); (t2, t5, cover_checked); (t5, t6, housing_closed); (t5, t7, housing_closed); (t6, t8, cover_position_one_tight); (t7, t8, cover_position_two_tight); (t8, t9, housing_leak_checked)
- E_sync: (t4, t5, gasket_seated); (t2, t5, cover_checked); (t8, t9, housing_leak_checked)
- E_mutex: (t6, t7, driver)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 3 |
| t2 | R | 0 | 2 |
| t3 | R | 2 | 3 |
| t4 | L | 3 | 5 |
| t5 | L+R | 5 | 8 |
| t6 | L | 8 | 10 |
| t7 | R | 10 | 12 |
| t8 | L | 12 | 16 |
| t9 | L+R | 16 | 19 |

Symbolic makespan 19; fully serial time for the same nodes 22; corresponding speedup 1.1579. Original and post-processed relation sets agree using complete labelled keys.

## A04 Two-branch harness panel assembly

Position the panel and separately prepare the left harness, right harness and label. Route both harnesses and terminate them using a shared crimping tool. Test each harness, then install the protective cover using both units. Secure the cover and apply the traceability label.

**S₀**: panel_available, left_cable_available, right_cable_available, cover_available, label_stock

**Sg**: panel_traceable

**Capacity-one resources**: panel, left_cable, right_cable, crimper, tester, cover, driver, label_printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | locate panel | panel | {panel_available} | {panel_located} | 2 | {panel} | {L} | single |
| t2 | prepare left cable | left cable | {left_cable_available} | {left_cable_prepared} | 2 | {left_cable} | {L, R} | single |
| t3 | prepare right cable | right cable | {right_cable_available} | {right_cable_prepared} | 3 | {right_cable} | {R} | single |
| t4 | prepare traceability label | label | {label_stock} | {panel_label_ready} | 1 | {label_printer} | {L, R} | single |
| t5 | route left cable | left cable | {panel_located, left_cable_prepared} | {left_cable_routed} | 2 | {panel, left_cable} | {L} | single |
| t6 | route right cable | right cable | {panel_located, right_cable_prepared} | {right_cable_routed} | 2 | {panel, right_cable} | {R} | single |
| t7 | crimp left terminals | left cable | {left_cable_routed} | {left_cable_terminated} | 3 | {left_cable, crimper} | {L} | single |
| t8 | crimp right terminals | right cable | {right_cable_routed} | {right_cable_terminated} | 3 | {right_cable, crimper} | {R} | single |
| t9 | test left branch | left cable | {left_cable_terminated} | {left_branch_tested} | 2 | {left_cable, tester} | {L, R} | single |
| t10 | test right branch | right cable | {right_cable_terminated} | {right_branch_tested} | 2 | {right_cable, tester} | {R} | single |
| t11 | place protective cover | cover | {left_branch_tested, right_branch_tested, cover_available} | {panel_cover_placed} | 3 | {panel, cover} | {B} | cooperative |
| t12 | fasten protective cover | cover | {panel_cover_placed} | {panel_cover_fastened} | 2 | {panel, cover, driver} | {R} | single |
| t13 | label completed panel | panel | {panel_cover_fastened, panel_label_ready} | {panel_traceable} | 1 | {panel} | {L} | single |

**Original typed relations**

- E_state: (t1, t5, panel_located); (t2, t5, left_cable_prepared); (t1, t6, panel_located); (t3, t6, right_cable_prepared); (t5, t7, left_cable_routed); (t6, t8, right_cable_routed); (t7, t9, left_cable_terminated); (t8, t10, right_cable_terminated); (t9, t11, left_branch_tested); (t10, t11, right_branch_tested); (t11, t12, panel_cover_placed); (t12, t13, panel_cover_fastened); (t4, t13, panel_label_ready)
- E_sync: (t9, t11, left_branch_tested); (t10, t11, right_branch_tested)
- E_mutex: (t5, t6, panel); (t7, t8, crimper); (t9, t10, tester)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | R | 2 | 5 |
| t4 | L | 2 | 3 |
| t5 | L | 3 | 5 |
| t6 | R | 5 | 7 |
| t7 | L | 5 | 8 |
| t8 | R | 8 | 11 |
| t9 | L | 8 | 10 |
| t10 | R | 11 | 13 |
| t11 | L+R | 13 | 16 |
| t12 | R | 16 | 18 |
| t13 | L | 18 | 19 |

Symbolic makespan 19; fully serial time for the same nodes 28; corresponding speedup 1.4737. Original and post-processed relation sets agree using complete labelled keys.

## I01 Dimensional inspection of two parts

Prepare two parts and calibrated measuring equipment. Use the shared caliper to measure each part and record its dimensions. Print a combined inspection sheet and place both inspected parts in the completed-inspection tray.

**S₀**: part_a_available, part_b_available, caliper_calibrated, inspection_tray_ready

**Sg**: inspection_lot_documented

**Capacity-one resources**: part_a, part_b, caliper, printer, inspection_tray

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | prepare part A for measurement | part A | {part_a_available} | {part_a_positioned} | 1 | {part_a} | {L} | single |
| t2 | prepare part B for measurement | part B | {part_b_available} | {part_b_positioned} | 1 | {part_b} | {R} | single |
| t3 | measure and record part A | part A | {part_a_positioned, caliper_calibrated} | {part_a_measured} | 3 | {part_a, caliper} | {L} | single |
| t4 | measure and record part B | part B | {part_b_positioned, caliper_calibrated} | {part_b_measured} | 3 | {part_b, caliper} | {R} | single |
| t5 | print combined inspection sheet | inspection sheet | {part_a_measured, part_b_measured} | {combined_sheet_printed} | 2 | {printer} | {L, R} | single |
| t6 | place inspected part A | part A | {part_a_measured, inspection_tray_ready} | {part_a_on_inspection_tray} | 1 | {part_a, inspection_tray} | {L} | single |
| t7 | place inspected part B | part B | {part_b_measured, inspection_tray_ready} | {part_b_on_inspection_tray} | 1 | {part_b, inspection_tray} | {R} | single |
| t8 | associate sheet with inspected lot | inspection lot | {combined_sheet_printed, part_a_on_inspection_tray, part_b_on_inspection_tray} | {inspection_lot_documented} | 1 | {inspection_tray} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t3, part_a_positioned); (t2, t4, part_b_positioned); (t3, t5, part_a_measured); (t4, t5, part_b_measured); (t3, t6, part_a_measured); (t4, t7, part_b_measured); (t5, t8, combined_sheet_printed); (t6, t8, part_a_on_inspection_tray); (t7, t8, part_b_on_inspection_tray)
- E_sync: ∅
- E_mutex: (t3, t4, caliper); (t6, t7, inspection_tray)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 1 |
| t2 | R | 0 | 1 |
| t3 | L | 1 | 4 |
| t4 | R | 4 | 7 |
| t5 | L | 7 | 9 |
| t6 | L | 9 | 10 |
| t7 | R | 10 | 11 |
| t8 | L | 11 | 12 |

Symbolic makespan 12; fully serial time for the same nodes 13; corresponding speedup 1.0833. Original and post-processed relation sets agree using complete labelled keys.

## I02 Electrical module bench inspection

Confirm that the bench is ready and prepare the module and test leads. Place the module on the bench using both units, connect the leads, perform continuity and insulation tests, archive the results and move the module to the accepted-items area. The tester is a shared capacity-one resource.

**S₀**: bench_available, module_available, leads_available, test_program_available

**Sg**: module_in_pass_area

**Capacity-one resources**: bench, module, leads, tester, record_terminal, pass_tray

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | check test bench | bench | {bench_available} | {bench_checked} | 2 | {bench} | {L} | single |
| t2 | prepare module | module | {module_available} | {module_prepared} | 2 | {module} | {R} | single |
| t3 | prepare test leads | leads | {leads_available} | {leads_prepared} | 1 | {leads} | {L, R} | single |
| t4 | load test program | tester | {test_program_available} | {test_program_loaded} | 2 | {tester} | {R} | single |
| t5 | place module on bench | module | {bench_checked, module_prepared} | {module_on_bench} | 3 | {module, bench} | {B} | cooperative |
| t6 | connect test leads | module | {module_on_bench, leads_prepared} | {module_connected} | 2 | {module, bench, leads} | {L} | single |
| t7 | run continuity test | module | {module_connected, test_program_loaded} | {continuity_test_recorded} | 4 | {module, bench, tester, leads} | {R} | single |
| t8 | run insulation test | module | {module_connected, test_program_loaded} | {insulation_test_recorded} | 4 | {module, bench, tester, leads} | {R} | single |
| t9 | archive test results | test record | {continuity_test_recorded, insulation_test_recorded} | {module_test_archived} | 2 | {record_terminal} | {L} | single |
| t10 | transfer module to pass area | module | {module_test_archived} | {module_in_pass_area} | 3 | {module, bench, pass_tray} | {B} | cooperative |

**Original typed relations**

- E_state: (t1, t5, bench_checked); (t2, t5, module_prepared); (t5, t6, module_on_bench); (t3, t6, leads_prepared); (t6, t7, module_connected); (t4, t7, test_program_loaded); (t6, t8, module_connected); (t4, t8, test_program_loaded); (t7, t9, continuity_test_recorded); (t8, t9, insulation_test_recorded); (t9, t10, module_test_archived)
- E_sync: (t1, t5, bench_checked); (t2, t5, module_prepared); (t9, t10, module_test_archived)
- E_mutex: (t7, t8, tester)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L | 2 | 3 |
| t4 | R | 2 | 4 |
| t5 | L+R | 4 | 7 |
| t6 | L | 7 | 9 |
| t7 | R | 9 | 13 |
| t8 | R | 13 | 17 |
| t9 | L | 17 | 19 |
| t10 | L+R | 19 | 22 |

Symbolic makespan 22; fully serial time for the same nodes 25; corresponding speedup 1.1364. Original and post-processed relation sets agree using complete labelled keys.

## I03 Visual surface inspection of two workpieces

Prepare the left and right workpieces and the imaging settings. Use a shared camera to photograph their upper surfaces separately. Turn over the larger left workpiece using both units and photograph its back. Review both results, print labels and place the workpieces in their respective accepted-items trays.

**S₀**: large_part_available, small_part_available, camera_profile_ready, pass_tray_ready

**Sg**: both_parts_released

**Capacity-one resources**: large_part, small_part, camera, review_terminal, printer, pass_tray

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | position large part | large part | {large_part_available} | {large_part_positioned} | 2 | {large_part} | {L} | single |
| t2 | position small part | small part | {small_part_available} | {small_part_positioned} | 1 | {small_part} | {R} | single |
| t3 | configure camera | camera | {camera_profile_ready} | {camera_configured} | 2 | {camera} | {L, R} | single |
| t4 | image large part top | large part | {large_part_positioned, camera_configured} | {large_top_imaged} | 2 | {large_part, camera} | {L} | single |
| t5 | image small part | small part | {small_part_positioned, camera_configured} | {small_part_imaged} | 2 | {small_part, camera} | {R} | single |
| t6 | turn large part | large part | {large_top_imaged} | {large_part_turned} | 3 | {large_part} | {B} | cooperative |
| t7 | image large part back | large part | {large_part_turned, camera_configured} | {large_back_imaged} | 2 | {large_part, camera} | {L} | single |
| t8 | review image set | inspection images | {large_top_imaged, large_back_imaged, small_part_imaged} | {image_review_complete} | 3 | {review_terminal} | {R} | single |
| t9 | print large part label | large label | {image_review_complete} | {large_label_printed} | 1 | {printer} | {L} | single |
| t10 | print small part label | small label | {image_review_complete} | {small_label_printed} | 1 | {printer} | {R} | single |
| t11 | label and place large part | large part | {large_label_printed, pass_tray_ready} | {large_part_released} | 2 | {large_part, pass_tray} | {L} | single |
| t12 | label and place small part | small part | {small_label_printed, pass_tray_ready} | {small_part_released} | 1 | {small_part, pass_tray} | {R} | single |
| t13 | close inspection lot | inspection lot | {large_part_released, small_part_released} | {both_parts_released} | 1 | {} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t4, large_part_positioned); (t3, t4, camera_configured); (t2, t5, small_part_positioned); (t3, t5, camera_configured); (t4, t6, large_top_imaged); (t6, t7, large_part_turned); (t3, t7, camera_configured); (t4, t8, large_top_imaged); (t7, t8, large_back_imaged); (t5, t8, small_part_imaged); (t8, t9, image_review_complete); (t8, t10, image_review_complete); (t9, t11, large_label_printed); (t10, t12, small_label_printed); (t11, t13, large_part_released); (t12, t13, small_part_released)
- E_sync: (t4, t6, large_top_imaged)
- E_mutex: (t4, t5, camera); (t5, t7, camera); (t9, t10, printer); (t11, t12, pass_tray)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 1 |
| t3 | R | 1 | 3 |
| t4 | L | 3 | 5 |
| t5 | R | 5 | 7 |
| t6 | L+R | 7 | 10 |
| t7 | L | 10 | 12 |
| t8 | R | 12 | 15 |
| t9 | L | 15 | 16 |
| t10 | R | 16 | 17 |
| t11 | L | 16 | 18 |
| t12 | R | 18 | 19 |
| t13 | L | 19 | 20 |

Symbolic makespan 20; fully serial time for the same nodes 23; corresponding speedup 1.1500. Original and post-processed relation sets agree using complete labelled keys.

## I04 Assembly traceability review

Check the main assembly serial number and auxiliary module number using a shared scanner. Confirm the fastening and electrical-test records separately. Turn the assembly over using both units to inspect the rear label, combine the identity and inspection records, print a release label and transfer it to the completed-items area.

**S₀**: assembly_available, submodule_available, torque_record_available, electrical_record_available, release_tray_ready

**Sg**: assembly_released

**Capacity-one resources**: assembly, submodule, scanner, review_terminal, printer, release_tray

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | scan assembly serial | assembly | {assembly_available} | {assembly_serial_checked} | 2 | {assembly, scanner} | {L} | single |
| t2 | scan submodule serial | submodule | {submodule_available} | {submodule_serial_checked} | 1 | {submodule, scanner} | {R} | single |
| t3 | review torque record | torque record | {torque_record_available} | {torque_record_checked} | 2 | {review_terminal} | {L, R} | single |
| t4 | review electrical record | electrical record | {electrical_record_available} | {electrical_record_checked} | 2 | {review_terminal} | {R} | single |
| t5 | turn assembly for back label | assembly | {assembly_serial_checked} | {assembly_back_accessible} | 3 | {assembly} | {B} | cooperative |
| t6 | scan back label | assembly | {assembly_back_accessible} | {back_label_checked} | 1 | {assembly, scanner} | {L} | single |
| t7 | merge traceability records | release record | {assembly_serial_checked, submodule_serial_checked, torque_record_checked, electrical_record_checked, back_label_checked} | {traceability_record_complete} | 3 | {review_terminal} | {R} | single |
| t8 | print release tag | release tag | {traceability_record_complete} | {release_tag_printed} | 1 | {printer} | {L} | single |
| t9 | apply release tag | assembly | {release_tag_printed} | {assembly_tagged} | 1 | {assembly} | {L} | single |
| t10 | transfer released assembly | assembly | {assembly_tagged, release_tray_ready} | {assembly_released} | 3 | {assembly, release_tray} | {B} | cooperative |

**Original typed relations**

- E_state: (t1, t5, assembly_serial_checked); (t5, t6, assembly_back_accessible); (t1, t7, assembly_serial_checked); (t2, t7, submodule_serial_checked); (t3, t7, torque_record_checked); (t4, t7, electrical_record_checked); (t6, t7, back_label_checked); (t7, t8, traceability_record_complete); (t8, t9, release_tag_printed); (t9, t10, assembly_tagged)
- E_sync: (t1, t5, assembly_serial_checked); (t9, t10, assembly_tagged)
- E_mutex: (t1, t2, scanner); (t2, t6, scanner); (t3, t4, review_terminal)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 2 | 3 |
| t3 | L | 2 | 4 |
| t4 | R | 4 | 6 |
| t5 | L+R | 6 | 9 |
| t6 | L | 9 | 10 |
| t7 | R | 10 | 13 |
| t8 | L | 13 | 14 |
| t9 | L | 14 | 15 |
| t10 | L+R | 15 | 18 |

Symbolic makespan 18; fully serial time for the same nodes 19; corresponding speedup 1.0556. Original and post-processed relation sets agree using complete labelled keys.

## P01 Fragile instrument packing

Prepare the carton, cushioning and instrument. Arrange the cushioning, then place the instrument in the carton using both units. Insert the manual, seal the carton and apply the shipping label.

**S₀**: carton_flat, cushion_available, instrument_available, manual_available, shipping_data_ready

**Sg**: instrument_package_labeled

**Capacity-one resources**: carton, cushion, instrument, tape_dispenser, label_printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | form carton | carton | {carton_flat} | {carton_formed} | 2 | {carton} | {L} | single |
| t2 | prepare cushion | cushion | {cushion_available} | {cushion_prepared} | 1 | {cushion} | {R} | single |
| t3 | prepare instrument | instrument | {instrument_available} | {instrument_prepared} | 2 | {instrument} | {R} | single |
| t4 | line carton | carton | {carton_formed, cushion_prepared} | {carton_cushioned} | 2 | {carton, cushion} | {L} | single |
| t5 | place instrument in carton | instrument | {carton_cushioned, instrument_prepared} | {instrument_packed} | 3 | {instrument, carton} | {B} | cooperative |
| t6 | insert manual | manual | {instrument_packed, manual_available} | {manual_inserted} | 1 | {carton} | {L} | single |
| t7 | seal carton | carton | {manual_inserted} | {instrument_carton_sealed} | 2 | {carton, tape_dispenser} | {R} | single |
| t8 | print and apply shipping label | carton | {instrument_carton_sealed, shipping_data_ready} | {instrument_package_labeled} | 2 | {carton, label_printer} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t4, carton_formed); (t2, t4, cushion_prepared); (t4, t5, carton_cushioned); (t3, t5, instrument_prepared); (t5, t6, instrument_packed); (t6, t7, manual_inserted); (t7, t8, instrument_carton_sealed)
- E_sync: (t4, t5, carton_cushioned); (t3, t5, instrument_prepared)
- E_mutex: ∅
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 1 |
| t3 | R | 1 | 3 |
| t4 | L | 2 | 4 |
| t5 | L+R | 4 | 7 |
| t6 | L | 7 | 8 |
| t7 | R | 8 | 10 |
| t8 | L | 10 | 12 |

Symbolic makespan 12; fully serial time for the same nodes 15; corresponding speedup 1.2500. Original and post-processed relation sets agree using complete labelled keys.

## P02 Two-compartment spare-parts kit

Assemble the two-compartment box, check the two types of spare parts separately and place them in their respective inserts. Prepare the inventory list and load both inserts into the outer box using both units. Insert the list, seal and weigh the package, and apply a label.

**S₀**: outer_box_flat, part_a_available, part_b_available, tray_a_available, tray_b_available, order_ready

**Sg**: spare_kit_ready

**Capacity-one resources**: outer_box, part_a, part_b, tray_a, tray_b, scanner, printer, scale, tape_dispenser

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | form compartment box | outer box | {outer_box_flat} | {compartment_box_ready} | 3 | {outer_box} | {L} | single |
| t2 | check spare A | part A | {part_a_available, order_ready} | {part_a_checked} | 2 | {part_a, scanner} | {R} | single |
| t3 | check spare B | part B | {part_b_available, order_ready} | {part_b_checked} | 2 | {part_b, scanner} | {L, R} | single |
| t4 | load inner tray A | tray A | {part_a_checked, tray_a_available} | {tray_a_loaded} | 2 | {part_a, tray_a} | {L} | single |
| t5 | load inner tray B | tray B | {part_b_checked, tray_b_available} | {tray_b_loaded} | 2 | {part_b, tray_b} | {R} | single |
| t6 | print packing list | packing list | {order_ready} | {packing_list_ready} | 1 | {printer} | {L, R} | single |
| t7 | insert paired inner trays | spare kit | {compartment_box_ready, tray_a_loaded, tray_b_loaded} | {inner_trays_inserted} | 3 | {outer_box, tray_a, tray_b} | {B} | cooperative |
| t8 | insert packing list | packing list | {inner_trays_inserted, packing_list_ready} | {packing_list_inserted} | 1 | {outer_box} | {L} | single |
| t9 | seal spare kit | outer box | {packing_list_inserted} | {spare_kit_sealed} | 2 | {outer_box, tape_dispenser} | {R} | single |
| t10 | weigh kit | spare kit | {spare_kit_sealed} | {spare_kit_weighed} | 2 | {outer_box, scale} | {L, R} | single |
| t11 | label kit | spare kit | {spare_kit_weighed} | {spare_kit_ready} | 1 | {outer_box, printer} | {L} | single |

**Original typed relations**

- E_state: (t2, t4, part_a_checked); (t3, t5, part_b_checked); (t1, t7, compartment_box_ready); (t4, t7, tray_a_loaded); (t5, t7, tray_b_loaded); (t7, t8, inner_trays_inserted); (t6, t8, packing_list_ready); (t8, t9, packing_list_inserted); (t9, t10, spare_kit_sealed); (t10, t11, spare_kit_weighed)
- E_sync: (t1, t7, compartment_box_ready); (t4, t7, tray_a_loaded); (t5, t7, tray_b_loaded)
- E_mutex: (t2, t3, scanner)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 3 |
| t2 | R | 0 | 2 |
| t3 | R | 2 | 4 |
| t4 | L | 3 | 5 |
| t5 | R | 4 | 6 |
| t6 | L | 5 | 6 |
| t7 | L+R | 6 | 9 |
| t8 | L | 9 | 10 |
| t9 | R | 10 | 12 |
| t10 | L | 12 | 14 |
| t11 | L | 14 | 15 |

Symbolic makespan 15; fully serial time for the same nodes 21; corresponding speedup 1.4000. Original and post-processed relation sets agree using complete labelled keys.

## P03 Returned equipment and accessories packing

Check the main unit, power supply and cable separately using a shared scanner. Put the main unit in a protective bag and organize the accessories in an accessory bag. Load the main unit using both execution units, add the accessories and return form, then seal and label the carton.

**S₀**: return_box_ready, unit_available, adapter_available, cable_available, return_order_ready

**Sg**: return_package_identified

**Capacity-one resources**: scanner, unit, adapter, cable, accessory_bag, return_box, printer, tape_dispenser

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | scan returned unit | unit | {unit_available, return_order_ready} | {unit_identified} | 2 | {unit, scanner} | {L} | single |
| t2 | scan adapter | adapter | {adapter_available, return_order_ready} | {adapter_identified} | 1 | {adapter, scanner} | {R} | single |
| t3 | scan cable | cable | {cable_available, return_order_ready} | {cable_identified} | 1 | {cable, scanner} | {R} | single |
| t4 | bag returned unit | unit | {unit_identified} | {unit_protected} | 3 | {unit} | {L} | single |
| t5 | bag accessories | accessories | {adapter_identified, cable_identified} | {accessories_bagged} | 2 | {adapter, cable, accessory_bag} | {R} | single |
| t6 | print return form | return form | {return_order_ready} | {return_form_printed} | 1 | {printer} | {L, R} | single |
| t7 | place protected unit | unit | {unit_protected, return_box_ready} | {unit_in_return_box} | 3 | {unit, return_box} | {B} | cooperative |
| t8 | insert accessories | accessory bag | {unit_in_return_box, accessories_bagged} | {accessories_in_return_box} | 1 | {return_box, accessory_bag} | {R} | single |
| t9 | insert return form | return form | {accessories_in_return_box, return_form_printed} | {return_documents_inserted} | 1 | {return_box} | {L} | single |
| t10 | seal return carton | return box | {return_documents_inserted} | {return_box_sealed} | 2 | {return_box, tape_dispenser} | {R} | single |
| t11 | identify return package | return box | {return_box_sealed} | {return_package_identified} | 1 | {return_box, printer} | {L} | single |

**Original typed relations**

- E_state: (t1, t4, unit_identified); (t2, t5, adapter_identified); (t3, t5, cable_identified); (t4, t7, unit_protected); (t7, t8, unit_in_return_box); (t5, t8, accessories_bagged); (t8, t9, accessories_in_return_box); (t6, t9, return_form_printed); (t9, t10, return_documents_inserted); (t10, t11, return_box_sealed)
- E_sync: (t4, t7, unit_protected)
- E_mutex: (t1, t2, scanner); (t2, t3, scanner)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 2 | 3 |
| t3 | R | 3 | 4 |
| t4 | L | 2 | 5 |
| t5 | R | 4 | 6 |
| t6 | L | 5 | 6 |
| t7 | L+R | 6 | 9 |
| t8 | R | 9 | 10 |
| t9 | L | 10 | 11 |
| t10 | R | 11 | 13 |
| t11 | L | 13 | 14 |

Symbolic makespan 14; fully serial time for the same nodes 18; corresponding speedup 1.2857. Original and post-processed relation sets agree using complete labelled keys.

## P04 Insulated shipping box with two containers

Prepare the outer shipping box, two insulating liners and two sealed samples. Assemble each liner with its sample and add absorbent pads. Load the first container and then the second using both units. Add the record card, seal and weigh the box, and apply identification. The samples are already sealed; this task does not handle their contents.

**S₀**: shipper_ready, liner_a_available, liner_b_available, sealed_sample_a, sealed_sample_b, pads_available, record_data_ready

**Sg**: insulated_shipper_ready

**Capacity-one resources**: shipper, liner_a, liner_b, sample_a, sample_b, pads, printer, scale, sealer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | prepare liner A | liner A | {liner_a_available} | {liner_a_prepared} | 2 | {liner_a} | {L} | single |
| t2 | prepare liner B | liner B | {liner_b_available} | {liner_b_prepared} | 2 | {liner_b} | {R} | single |
| t3 | place sealed sample A in liner | sample A | {liner_a_prepared, sealed_sample_a} | {sample_a_in_liner} | 2 | {sample_a, liner_a} | {L} | single |
| t4 | place sealed sample B in liner | sample B | {liner_b_prepared, sealed_sample_b} | {sample_b_in_liner} | 2 | {sample_b, liner_b} | {R} | single |
| t5 | pad container A | liner A | {sample_a_in_liner, pads_available} | {container_a_complete} | 1 | {liner_a, pads} | {L} | single |
| t6 | pad container B | liner B | {sample_b_in_liner, pads_available} | {container_b_complete} | 1 | {liner_b, pads} | {R} | single |
| t7 | print record card | record card | {record_data_ready} | {record_card_ready} | 1 | {printer} | {L, R} | single |
| t8 | load first container | container A | {container_a_complete, shipper_ready} | {container_a_loaded} | 3 | {shipper, liner_a} | {B} | cooperative |
| t9 | load second container | container B | {container_a_loaded, container_b_complete} | {both_containers_loaded} | 3 | {shipper, liner_b} | {B} | cooperative |
| t10 | insert record card | shipper | {both_containers_loaded, record_card_ready} | {shipper_record_inserted} | 1 | {shipper} | {L} | single |
| t11 | seal insulated shipper | shipper | {shipper_record_inserted} | {shipper_sealed} | 2 | {shipper, sealer} | {R} | single |
| t12 | weigh insulated shipper | shipper | {shipper_sealed} | {shipper_weighed} | 2 | {shipper, scale} | {L, R} | single |
| t13 | label insulated shipper | shipper | {shipper_weighed} | {insulated_shipper_ready} | 1 | {shipper, printer} | {L} | single |

**Original typed relations**

- E_state: (t1, t3, liner_a_prepared); (t2, t4, liner_b_prepared); (t3, t5, sample_a_in_liner); (t4, t6, sample_b_in_liner); (t5, t8, container_a_complete); (t8, t9, container_a_loaded); (t6, t9, container_b_complete); (t9, t10, both_containers_loaded); (t7, t10, record_card_ready); (t10, t11, shipper_record_inserted); (t11, t12, shipper_sealed); (t12, t13, shipper_weighed)
- E_sync: (t5, t8, container_a_complete); (t8, t9, container_a_loaded); (t6, t9, container_b_complete)
- E_mutex: (t5, t6, pads)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L | 2 | 4 |
| t4 | R | 2 | 4 |
| t5 | L | 4 | 5 |
| t6 | R | 5 | 6 |
| t7 | L | 5 | 6 |
| t8 | L+R | 6 | 9 |
| t9 | L+R | 9 | 12 |
| t10 | L | 12 | 13 |
| t11 | R | 13 | 15 |
| t12 | L | 15 | 17 |
| t13 | L | 17 | 18 |

Symbolic makespan 18; fully serial time for the same nodes 23; corresponding speedup 1.2778. Original and post-processed relation sets agree using complete labelled keys.

## S01 Three-category parcel sorting

Scan parcels A, B and C separately with the same scanner and read their destination categories. Place each parcel in its target compartment. Record batch completion after all three sorting results are complete.

**S₀**: parcel_a_ready, parcel_b_ready, parcel_c_ready, bins_ready, sort_manifest_ready

**Sg**: sorting_batch_recorded

**Capacity-one resources**: parcel_a, parcel_b, parcel_c, scanner, bin_a, bin_b, bin_c, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | scan and classify parcel A | parcel A | {parcel_a_ready, sort_manifest_ready} | {parcel_a_classified} | 2 | {parcel_a, scanner} | {L} | single |
| t2 | scan and classify parcel B | parcel B | {parcel_b_ready, sort_manifest_ready} | {parcel_b_classified} | 2 | {parcel_b, scanner} | {R} | single |
| t3 | scan and classify parcel C | parcel C | {parcel_c_ready, sort_manifest_ready} | {parcel_c_classified} | 2 | {parcel_c, scanner} | {L, R} | single |
| t4 | place parcel A in assigned bin | parcel A | {parcel_a_classified, bins_ready} | {parcel_a_sorted} | 2 | {parcel_a, bin_a} | {L} | single |
| t5 | place parcel B in assigned bin | parcel B | {parcel_b_classified, bins_ready} | {parcel_b_sorted} | 2 | {parcel_b, bin_b} | {R} | single |
| t6 | place parcel C in assigned bin | parcel C | {parcel_c_classified, bins_ready} | {parcel_c_sorted} | 2 | {parcel_c, bin_c} | {L, R} | single |
| t7 | record sorted batch | sorting record | {parcel_a_sorted, parcel_b_sorted, parcel_c_sorted} | {sorting_batch_recorded} | 1 | {terminal} | {R} | single |

**Original typed relations**

- E_state: (t1, t4, parcel_a_classified); (t2, t5, parcel_b_classified); (t3, t6, parcel_c_classified); (t4, t7, parcel_a_sorted); (t5, t7, parcel_b_sorted); (t6, t7, parcel_c_sorted)
- E_sync: ∅
- E_mutex: (t1, t2, scanner); (t2, t3, scanner)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 2 | 4 |
| t3 | L | 4 | 6 |
| t4 | L | 6 | 8 |
| t5 | R | 4 | 6 |
| t6 | R | 6 | 8 |
| t7 | R | 8 | 9 |

Symbolic makespan 9; fully serial time for the same nodes 13; corresponding speedup 1.4444. Original and post-processed relation sets agree using complete labelled keys.

## S02 Routing accepted and rework parts

Prepare two parts awaiting classification and two routing trays. At the same inspection station, confirm in sequence that part A is accepted and part B requires rework. Print their labels, place them in the corresponding trays and register both transfer records.

**S₀**: item_a_available, item_b_available, pass_tray_ready, rework_tray_ready, inspection_rules_ready

**Sg**: routing_complete

**Capacity-one resources**: item_a, item_b, inspection_station, printer, pass_tray, rework_tray, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | confirm item A pass classification | item A | {item_a_available, inspection_rules_ready} | {item_a_pass_decision} | 3 | {item_a, inspection_station} | {L} | single |
| t2 | confirm item B rework classification | item B | {item_b_available, inspection_rules_ready} | {item_b_rework_decision} | 3 | {item_b, inspection_station} | {R} | single |
| t3 | print pass label | pass label | {item_a_pass_decision} | {pass_label_printed} | 1 | {printer} | {L} | single |
| t4 | print rework label | rework label | {item_b_rework_decision} | {rework_label_printed} | 1 | {printer} | {R} | single |
| t5 | label and route item A | item A | {item_a_pass_decision, pass_label_printed, pass_tray_ready} | {item_a_routed} | 2 | {item_a, pass_tray} | {L} | single |
| t6 | label and route item B | item B | {item_b_rework_decision, rework_label_printed, rework_tray_ready} | {item_b_routed} | 2 | {item_b, rework_tray} | {R} | single |
| t7 | record pass routing | pass routing record | {item_a_routed} | {pass_routing_recorded} | 1 | {terminal} | {L, R} | single |
| t8 | record rework routing | rework routing record | {item_b_routed} | {rework_routing_recorded} | 1 | {terminal} | {R} | single |
| t9 | close routing batch | routing batch | {pass_routing_recorded, rework_routing_recorded} | {routing_complete} | 1 | {terminal} | {L} | single |

**Original typed relations**

- E_state: (t1, t3, item_a_pass_decision); (t2, t4, item_b_rework_decision); (t1, t5, item_a_pass_decision); (t3, t5, pass_label_printed); (t2, t6, item_b_rework_decision); (t4, t6, rework_label_printed); (t5, t7, item_a_routed); (t6, t8, item_b_routed); (t7, t9, pass_routing_recorded); (t8, t9, rework_routing_recorded)
- E_sync: ∅
- E_mutex: (t1, t2, inspection_station); (t3, t4, printer); (t7, t8, terminal)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 3 |
| t2 | R | 3 | 6 |
| t3 | L | 3 | 4 |
| t4 | R | 6 | 7 |
| t5 | L | 4 | 6 |
| t6 | R | 7 | 9 |
| t7 | L | 6 | 7 |
| t8 | R | 9 | 10 |
| t9 | L | 10 | 11 |

Symbolic makespan 11; fully serial time for the same nodes 15; corresponding speedup 1.3636. Original and post-processed relation sets agree using complete labelled keys.

## S03 Matching three sets of fasteners

Select a bolt and nut from each of three fastener sets and verify matching specifications using the same gauge. Put each matched set in a separate bag, print a combined inventory list and load the three completed bags into a tote.

**S₀**: fastener_group_a, fastener_group_b, fastener_group_c, bags_available, tote_ready, gauge_ready

**Sg**: matched_fasteners_collected

**Capacity-one resources**: group_a, group_b, group_c, gauge, bag_a, bag_b, bag_c, printer, tote

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | select fasteners from group A | group A | {fastener_group_a} | {fasteners_a_selected} | 2 | {group_a} | {L} | single |
| t2 | select fasteners from group B | group B | {fastener_group_b} | {fasteners_b_selected} | 2 | {group_b} | {R} | single |
| t3 | select fasteners from group C | group C | {fastener_group_c} | {fasteners_c_selected} | 2 | {group_c} | {L, R} | single |
| t4 | gauge group A match | group A | {fasteners_a_selected, gauge_ready} | {fasteners_a_matched} | 3 | {group_a, gauge} | {L} | single |
| t5 | gauge group B match | group B | {fasteners_b_selected, gauge_ready} | {fasteners_b_matched} | 3 | {group_b, gauge} | {R} | single |
| t6 | gauge group C match | group C | {fasteners_c_selected, gauge_ready} | {fasteners_c_matched} | 3 | {group_c, gauge} | {L, R} | single |
| t7 | bag matched group A | bag A | {fasteners_a_matched, bags_available} | {bag_a_complete} | 1 | {group_a, bag_a} | {L} | single |
| t8 | bag matched group B | bag B | {fasteners_b_matched, bags_available} | {bag_b_complete} | 1 | {group_b, bag_b} | {R} | single |
| t9 | bag matched group C | bag C | {fasteners_c_matched, bags_available} | {bag_c_complete} | 1 | {group_c, bag_c} | {L, R} | single |
| t10 | print combined fastener list | fastener list | {bag_a_complete, bag_b_complete, bag_c_complete} | {fastener_list_printed} | 1 | {printer} | {L} | single |
| t11 | collect bags and list in tote | fastener tote | {bag_a_complete, bag_b_complete, bag_c_complete, fastener_list_printed, tote_ready} | {matched_fasteners_collected} | 2 | {bag_a, bag_b, bag_c, tote} | {R} | single |

**Original typed relations**

- E_state: (t1, t4, fasteners_a_selected); (t2, t5, fasteners_b_selected); (t3, t6, fasteners_c_selected); (t4, t7, fasteners_a_matched); (t5, t8, fasteners_b_matched); (t6, t9, fasteners_c_matched); (t7, t10, bag_a_complete); (t8, t10, bag_b_complete); (t9, t10, bag_c_complete); (t7, t11, bag_a_complete); (t8, t11, bag_b_complete); (t9, t11, bag_c_complete); (t10, t11, fastener_list_printed)
- E_sync: ∅
- E_mutex: (t4, t5, gauge); (t5, t6, gauge)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L | 2 | 4 |
| t4 | L | 4 | 7 |
| t5 | R | 7 | 10 |
| t6 | L | 10 | 13 |
| t7 | L | 13 | 14 |
| t8 | R | 10 | 11 |
| t9 | R | 13 | 14 |
| t10 | L | 14 | 15 |
| t11 | R | 15 | 17 |

Symbolic makespan 17; fully serial time for the same nodes 21; corresponding speedup 1.2353. Original and post-processed relation sets agree using complete labelled keys.

## S04 Fragile-part placement and traceability

Prepare one large part and two small parts, and identify all three using a shared scanner. Arrange the two small-part inserts separately and place the large part on the central tray using both units. Print three traceability labels with a shared printer. Label and place each part in its assigned area, then combine the batch records.

**S₀**: large_item_available, small_a_available, small_b_available, center_tray_ready, side_trays_ready, batch_record_ready

**Sg**: fragile_batch_traceable

**Capacity-one resources**: large_item, small_a, small_b, scanner, center_tray, tray_a, tray_b, printer, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | prepare large fragile item | large item | {large_item_available} | {large_item_prepared} | 2 | {large_item} | {L} | single |
| t2 | prepare small item A | small A | {small_a_available} | {small_a_prepared} | 1 | {small_a} | {R} | single |
| t3 | prepare small item B | small B | {small_b_available} | {small_b_prepared} | 1 | {small_b} | {L, R} | single |
| t4 | scan large item | large item | {large_item_prepared, batch_record_ready} | {large_item_identified} | 1 | {large_item, scanner} | {L} | single |
| t5 | scan small item A | small A | {small_a_prepared, batch_record_ready} | {small_a_identified} | 1 | {small_a, scanner} | {R} | single |
| t6 | scan small item B | small B | {small_b_prepared, batch_record_ready} | {small_b_identified} | 1 | {small_b, scanner} | {L, R} | single |
| t7 | arrange small item A in side tray | small A | {small_a_identified, side_trays_ready} | {small_a_positioned} | 2 | {small_a, tray_a} | {L} | single |
| t8 | arrange small item B in side tray | small B | {small_b_identified, side_trays_ready} | {small_b_positioned} | 2 | {small_b, tray_b} | {R} | single |
| t9 | place large item on center tray | large item | {large_item_identified, center_tray_ready} | {large_item_positioned} | 3 | {large_item, center_tray} | {B} | cooperative |
| t10 | print large item trace tag | large tag | {large_item_identified} | {large_trace_tag_ready} | 1 | {printer} | {L} | single |
| t11 | print small A trace tag | small A tag | {small_a_identified} | {small_a_tag_ready} | 1 | {printer} | {R} | single |
| t12 | print small B trace tag | small B tag | {small_b_identified} | {small_b_tag_ready} | 1 | {printer} | {L, R} | single |
| t13 | tag large item | large item | {large_item_positioned, large_trace_tag_ready} | {large_item_tagged} | 1 | {large_item, center_tray} | {L} | single |
| t14 | tag small item A | small A | {small_a_positioned, small_a_tag_ready} | {small_a_tagged} | 1 | {small_a, tray_a} | {R} | single |
| t15 | tag small item B | small B | {small_b_positioned, small_b_tag_ready} | {small_b_tagged} | 1 | {small_b, tray_b} | {L, R} | single |
| t16 | merge fragile batch record | batch record | {large_item_tagged, small_a_tagged, small_b_tagged} | {fragile_batch_traceable} | 2 | {terminal} | {R} | single |

**Original typed relations**

- E_state: (t1, t4, large_item_prepared); (t2, t5, small_a_prepared); (t3, t6, small_b_prepared); (t5, t7, small_a_identified); (t6, t8, small_b_identified); (t4, t9, large_item_identified); (t4, t10, large_item_identified); (t5, t11, small_a_identified); (t6, t12, small_b_identified); (t9, t13, large_item_positioned); (t10, t13, large_trace_tag_ready); (t7, t14, small_a_positioned); (t11, t14, small_a_tag_ready); (t8, t15, small_b_positioned); (t12, t15, small_b_tag_ready); (t13, t16, large_item_tagged); (t14, t16, small_a_tagged); (t15, t16, small_b_tagged)
- E_sync: (t4, t9, large_item_identified)
- E_mutex: (t4, t5, scanner); (t5, t6, scanner); (t10, t11, printer); (t11, t12, printer)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 1 |
| t3 | R | 1 | 2 |
| t4 | L | 2 | 3 |
| t5 | R | 3 | 4 |
| t6 | L | 4 | 5 |
| t7 | L | 5 | 7 |
| t8 | R | 5 | 7 |
| t9 | L+R | 7 | 10 |
| t10 | L | 10 | 11 |
| t11 | R | 11 | 12 |
| t12 | L | 12 | 13 |
| t13 | L | 13 | 14 |
| t14 | R | 12 | 13 |
| t15 | R | 13 | 14 |
| t16 | R | 14 | 16 |

Symbolic makespan 16; fully serial time for the same nodes 22; corresponding speedup 1.3750. Original and post-processed relation sets agree using complete labelled keys.

## T01 Locating fixture replacement

Confirm that the workbench is safe and ready, and prepare the new fixture and fasteners. Detach the old fixture and remove it using both units. Install the new fixture using both units, then use a shared tool to lock both fastening points and check the positioning.

**S₀**: workcell_safe, old_fixture_installed, new_fixture_available, fasteners_available

**Sg**: new_fixture_verified

**Capacity-one resources**: workbench, old_fixture, new_fixture, driver, gauge

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | confirm workbench readiness | workbench | {workcell_safe} | {workbench_ready} | 2 | {workbench} | {L} | single |
| t2 | prepare new fixture | new fixture | {new_fixture_available} | {new_fixture_prepared} | 3 | {new_fixture} | {R} | single |
| t3 | prepare fasteners | fasteners | {fasteners_available} | {fasteners_prepared} | 2 | {} | {L, R} | single |
| t4 | unfasten old fixture | old fixture | {old_fixture_installed, workbench_ready} | {old_fixture_unfastened} | 4 | {workbench, old_fixture, driver} | {L} | single |
| t5 | remove old fixture together | old fixture | {old_fixture_unfastened} | {old_fixture_removed} | 3 | {workbench, old_fixture} | {B} | cooperative |
| t6 | install new fixture together | new fixture | {old_fixture_removed, new_fixture_prepared} | {new_fixture_installed} | 4 | {workbench, new_fixture} | {B} | cooperative |
| t7 | lock first fixture position | new fixture | {new_fixture_installed, fasteners_prepared} | {first_fixture_lock_complete} | 3 | {workbench, new_fixture, driver} | {L} | single |
| t8 | lock second fixture position | new fixture | {new_fixture_installed, fasteners_prepared} | {second_fixture_lock_complete} | 3 | {workbench, new_fixture, driver} | {R} | single |
| t9 | verify fixture positioning | new fixture | {first_fixture_lock_complete, second_fixture_lock_complete} | {new_fixture_verified} | 3 | {workbench, new_fixture, gauge} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t4, workbench_ready); (t4, t5, old_fixture_unfastened); (t5, t6, old_fixture_removed); (t2, t6, new_fixture_prepared); (t6, t7, new_fixture_installed); (t3, t7, fasteners_prepared); (t6, t8, new_fixture_installed); (t3, t8, fasteners_prepared); (t7, t9, first_fixture_lock_complete); (t8, t9, second_fixture_lock_complete)
- E_sync: (t4, t5, old_fixture_unfastened); (t5, t6, old_fixture_removed); (t2, t6, new_fixture_prepared)
- E_mutex: (t7, t8, driver)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 3 |
| t3 | L | 2 | 4 |
| t4 | L | 4 | 8 |
| t5 | L+R | 8 | 11 |
| t6 | L+R | 11 | 15 |
| t7 | L | 15 | 18 |
| t8 | R | 18 | 21 |
| t9 | L | 21 | 24 |

Symbolic makespan 24; fully serial time for the same nodes 27; corresponding speedup 1.1250. Original and post-processed relation sets agree using complete labelled keys.

## T02 Calibration preparation for two tools

Identify the two tools separately and prepare their calibration records. Calibrate them in sequence using a shared reference standard. Apply calibration labels, organize the tool locations and finally verify that both tools and their records are ready.

**S₀**: tool_a_available, tool_b_available, standard_ready, record_template_ready, tool_rack_available

**Sg**: calibrated_tools_ready

**Capacity-one resources**: tool_a, tool_b, standard, printer, tool_rack, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | identify tool A | tool A | {tool_a_available} | {tool_a_identified} | 2 | {tool_a} | {L} | single |
| t2 | identify tool B | tool B | {tool_b_available} | {tool_b_identified} | 2 | {tool_b} | {R} | single |
| t3 | prepare calibration record | calibration record | {record_template_ready} | {calibration_record_open} | 2 | {terminal} | {L, R} | single |
| t4 | calibrate tool A | tool A | {tool_a_identified, calibration_record_open, standard_ready} | {tool_a_calibrated} | 4 | {tool_a, standard} | {L} | single |
| t5 | calibrate tool B | tool B | {tool_b_identified, calibration_record_open, standard_ready} | {tool_b_calibrated} | 4 | {tool_b, standard} | {R} | single |
| t6 | print calibration label A | label A | {tool_a_calibrated} | {calibration_label_a_ready} | 1 | {printer} | {L} | single |
| t7 | print calibration label B | label B | {tool_b_calibrated} | {calibration_label_b_ready} | 1 | {printer} | {R} | single |
| t8 | prepare tool rack | tool rack | {tool_rack_available} | {tool_rack_ready} | 2 | {tool_rack} | {L, R} | single |
| t9 | label and stow tool A | tool A | {calibration_label_a_ready, tool_rack_ready} | {tool_a_ready_in_rack} | 2 | {tool_a, tool_rack} | {L} | single |
| t10 | label and stow tool B | tool B | {calibration_label_b_ready, tool_rack_ready} | {tool_b_ready_in_rack} | 2 | {tool_b, tool_rack} | {R} | single |
| t11 | confirm calibrated tools and record | calibration record | {tool_a_ready_in_rack, tool_b_ready_in_rack, calibration_record_open} | {calibrated_tools_ready} | 2 | {terminal} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t4, tool_a_identified); (t3, t4, calibration_record_open); (t2, t5, tool_b_identified); (t3, t5, calibration_record_open); (t4, t6, tool_a_calibrated); (t5, t7, tool_b_calibrated); (t6, t9, calibration_label_a_ready); (t8, t9, tool_rack_ready); (t7, t10, calibration_label_b_ready); (t8, t10, tool_rack_ready); (t9, t11, tool_a_ready_in_rack); (t10, t11, tool_b_ready_in_rack); (t3, t11, calibration_record_open)
- E_sync: ∅
- E_mutex: (t4, t5, standard); (t6, t7, printer); (t9, t10, tool_rack)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L | 2 | 4 |
| t4 | L | 4 | 8 |
| t5 | R | 8 | 12 |
| t6 | L | 8 | 9 |
| t7 | R | 12 | 13 |
| t8 | L | 9 | 11 |
| t9 | L | 11 | 13 |
| t10 | R | 13 | 15 |
| t11 | L | 15 | 17 |

Symbolic makespan 17; fully serial time for the same nodes 24; corresponding speedup 1.4118. Original and post-processed relation sets agree using complete labelled keys.

## T03 Workstation clearance and material preparation

Collect leftover material from the left and right areas, remove the full transfer tray using both units and clean both work areas. Check two sets of new material, place them in their corresponding areas, update the workstation board and check readiness to start work.

**S₀**: left_area_idle, right_area_idle, waste_tray_available, new_material_a, new_material_b, job_data_ready

**Sg**: workcell_ready_for_job

**Capacity-one resources**: left_area, right_area, waste_tray, cleaning_kit, material_a, material_b, scanner, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | collect leftovers from left area | left area | {left_area_idle, waste_tray_available} | {left_leftovers_collected} | 3 | {left_area, waste_tray} | {L} | single |
| t2 | collect leftovers from right area | right area | {right_area_idle, waste_tray_available} | {right_leftovers_collected} | 3 | {right_area, waste_tray} | {R} | single |
| t3 | move loaded waste tray together | waste tray | {left_leftovers_collected, right_leftovers_collected} | {waste_tray_removed} | 3 | {waste_tray} | {B} | cooperative |
| t4 | clean left work area | left area | {waste_tray_removed, left_area_idle} | {left_area_clean} | 3 | {left_area, cleaning_kit} | {L} | single |
| t5 | clean right work area | right area | {waste_tray_removed, right_area_idle} | {right_area_clean} | 3 | {right_area, cleaning_kit} | {R} | single |
| t6 | check new material A | material A | {new_material_a, job_data_ready} | {material_a_verified} | 2 | {material_a, scanner} | {L} | single |
| t7 | check new material B | material B | {new_material_b, job_data_ready} | {material_b_verified} | 2 | {material_b, scanner} | {R} | single |
| t8 | place material A in left area | material A | {left_area_clean, material_a_verified} | {left_area_stocked} | 2 | {left_area, material_a} | {L} | single |
| t9 | place material B in right area | material B | {right_area_clean, material_b_verified} | {right_area_stocked} | 2 | {right_area, material_b} | {R} | single |
| t10 | update workcell job board | job board | {left_area_stocked, right_area_stocked, job_data_ready} | {job_board_updated} | 2 | {terminal} | {L, R} | single |
| t11 | confirm readiness for new job | workcell | {job_board_updated, left_area_stocked, right_area_stocked} | {workcell_ready_for_job} | 2 | {left_area, right_area} | {L, R} | single |

**Original typed relations**

- E_state: (t1, t3, left_leftovers_collected); (t2, t3, right_leftovers_collected); (t3, t4, waste_tray_removed); (t3, t5, waste_tray_removed); (t4, t8, left_area_clean); (t6, t8, material_a_verified); (t5, t9, right_area_clean); (t7, t9, material_b_verified); (t8, t10, left_area_stocked); (t9, t10, right_area_stocked); (t10, t11, job_board_updated); (t8, t11, left_area_stocked); (t9, t11, right_area_stocked)
- E_sync: (t1, t3, left_leftovers_collected); (t2, t3, right_leftovers_collected)
- E_mutex: (t1, t2, waste_tray); (t4, t5, cleaning_kit); (t6, t7, scanner)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 3 |
| t2 | R | 3 | 6 |
| t3 | L+R | 6 | 9 |
| t4 | L | 9 | 12 |
| t5 | R | 12 | 15 |
| t6 | L | 12 | 14 |
| t7 | R | 15 | 17 |
| t8 | L | 14 | 16 |
| t9 | R | 17 | 19 |
| t10 | L | 19 | 21 |
| t11 | L | 21 | 23 |

Symbolic makespan 23; fully serial time for the same nodes 27; corresponding speedup 1.1739. Original and post-processed relation sets agree using complete labelled keys.

## T04 Two-stage tooling handover

Verify the identity of the new tooling, prepare the receiving table and confirm the transport pallet. Position the support blocks, then transfer the tooling from the pallet to the table using both units. Prepare two accessory groups independently and install them using a shared tool. Inspect both groups, move the complete tooling to the handover position using both units, combine the inspection records and print the handover sheet.

**S₀**: new_tooling_available, receiving_table_available, transport_tray_ready, support_blocks_available, accessory_a_available, accessory_b_available, handover_position_ready, handover_order_ready

**Sg**: tooling_handover_documented

**Capacity-one resources**: tooling, receiving_table, transport_tray, support_blocks, accessory_a, accessory_b, driver, tester, handover_position, terminal, printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | verify new tooling identity | tooling | {new_tooling_available} | {tooling_identity_verified} | 2 | {tooling} | {L} | single |
| t2 | prepare receiving table | receiving table | {receiving_table_available} | {receiving_table_prepared} | 3 | {receiving_table} | {R} | single |
| t3 | confirm transport tray readiness | transport tray | {transport_tray_ready} | {transport_tray_confirmed} | 1 | {transport_tray} | {L, R} | single |
| t4 | place support blocks on table | support blocks | {receiving_table_prepared, support_blocks_available} | {table_supports_ready} | 2 | {receiving_table, support_blocks} | {R} | single |
| t5 | transfer tooling onto receiving table together | tooling | {tooling_identity_verified, table_supports_ready, transport_tray_confirmed} | {tooling_on_receiving_table} | 4 | {tooling, receiving_table, transport_tray, support_blocks} | {B} | cooperative |
| t6 | prepare accessory group A | accessory A | {accessory_a_available} | {accessory_a_prepared} | 2 | {accessory_a} | {L} | single |
| t7 | prepare accessory group B | accessory B | {accessory_b_available} | {accessory_b_prepared} | 2 | {accessory_b} | {R} | single |
| t8 | install accessory group A | accessory A | {tooling_on_receiving_table, accessory_a_prepared} | {accessory_a_installed} | 3 | {tooling, accessory_a, driver} | {L} | single |
| t9 | install accessory group B | accessory B | {tooling_on_receiving_table, accessory_b_prepared} | {accessory_b_installed} | 3 | {tooling, accessory_b, driver} | {R} | single |
| t10 | test accessory group A | accessory A | {accessory_a_installed} | {accessory_a_tested} | 3 | {tooling, accessory_a, tester} | {L} | single |
| t11 | test accessory group B | accessory B | {accessory_b_installed} | {accessory_b_tested} | 3 | {tooling, accessory_b, tester} | {R} | single |
| t12 | move completed tooling to handover position together | tooling | {accessory_a_tested, accessory_b_tested, handover_position_ready} | {tooling_at_handover} | 4 | {tooling, receiving_table, handover_position} | {B} | cooperative |
| t13 | merge tooling test and transfer records | handover record | {accessory_a_tested, accessory_b_tested, tooling_at_handover, handover_order_ready} | {handover_record_complete} | 2 | {terminal} | {L, R} | single |
| t14 | print tooling handover document | handover document | {handover_record_complete} | {tooling_handover_documented} | 1 | {printer} | {R} | single |

**Original typed relations**

- E_state: (t2, t4, receiving_table_prepared); (t1, t5, tooling_identity_verified); (t4, t5, table_supports_ready); (t3, t5, transport_tray_confirmed); (t5, t8, tooling_on_receiving_table); (t6, t8, accessory_a_prepared); (t5, t9, tooling_on_receiving_table); (t7, t9, accessory_b_prepared); (t8, t10, accessory_a_installed); (t9, t11, accessory_b_installed); (t10, t12, accessory_a_tested); (t11, t12, accessory_b_tested); (t10, t13, accessory_a_tested); (t11, t13, accessory_b_tested); (t12, t13, tooling_at_handover); (t13, t14, handover_record_complete)
- E_sync: (t1, t5, tooling_identity_verified); (t4, t5, table_supports_ready); (t3, t5, transport_tray_confirmed); (t10, t12, accessory_a_tested); (t11, t12, accessory_b_tested)
- E_mutex: (t8, t9, driver); (t9, t10, tooling); (t10, t11, tester)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 3 |
| t3 | L | 2 | 3 |
| t4 | R | 3 | 5 |
| t5 | L+R | 5 | 9 |
| t6 | L | 9 | 11 |
| t7 | R | 9 | 11 |
| t8 | L | 11 | 14 |
| t9 | R | 14 | 17 |
| t10 | L | 17 | 20 |
| t11 | R | 20 | 23 |
| t12 | L+R | 23 | 27 |
| t13 | L | 27 | 29 |
| t14 | R | 29 | 30 |

Symbolic makespan 30; fully serial time for the same nodes 35; corresponding speedup 1.1667. Original and post-processed relation sets agree using complete labelled keys.

## W01 Consolidating two totes

Scan the two source totes and prepare the left and right areas of the destination tote separately. Transfer the left tote contents into the destination tote using both units, then transfer the right tote contents. Finally, check the consolidated quantity and apply identification.

**S₀**: source_a_ready, source_b_ready, target_tote_empty, manifest_ready

**Sg**: consolidated_tote_labeled

**Capacity-one resources**: source_a, source_b, target_tote, scanner, printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | scan source tote A | source A | {source_a_ready, manifest_ready} | {source_a_identified} | 1 | {source_a, scanner} | {L} | single |
| t2 | scan source tote B | source B | {source_b_ready, manifest_ready} | {source_b_identified} | 1 | {source_b, scanner} | {R} | single |
| t3 | prepare target left region | target tote | {target_tote_empty} | {target_left_prepared} | 2 | {target_tote} | {L} | single |
| t4 | prepare target right region | target tote | {target_tote_empty} | {target_right_prepared} | 2 | {target_tote} | {R} | single |
| t5 | transfer contents of source A | source A contents | {source_a_identified, target_left_prepared} | {source_a_transferred} | 3 | {source_a, target_tote} | {B} | cooperative |
| t6 | transfer contents of source B | source B contents | {source_b_identified, target_right_prepared, source_a_transferred} | {both_sources_transferred} | 3 | {source_b, target_tote} | {B} | cooperative |
| t7 | verify consolidated quantity | target tote | {both_sources_transferred, manifest_ready} | {consolidation_verified} | 2 | {target_tote} | {L, R} | single |
| t8 | label consolidated tote | target tote | {consolidation_verified} | {consolidated_tote_labeled} | 1 | {target_tote, printer} | {R} | single |

**Original typed relations**

- E_state: (t1, t5, source_a_identified); (t3, t5, target_left_prepared); (t2, t6, source_b_identified); (t4, t6, target_right_prepared); (t5, t6, source_a_transferred); (t6, t7, both_sources_transferred); (t7, t8, consolidation_verified)
- E_sync: (t1, t5, source_a_identified); (t3, t5, target_left_prepared); (t2, t6, source_b_identified); (t4, t6, target_right_prepared); (t5, t6, source_a_transferred)
- E_mutex: (t1, t2, scanner); (t3, t4, target_tote); (t4, t5, target_tote)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 1 |
| t2 | R | 1 | 2 |
| t3 | L | 1 | 3 |
| t4 | R | 3 | 5 |
| t5 | L+R | 5 | 8 |
| t6 | L+R | 8 | 11 |
| t7 | L | 11 | 13 |
| t8 | R | 13 | 14 |

Symbolic makespan 14; fully serial time for the same nodes 15; corresponding speedup 1.0714. Original and post-processed relation sets agree using complete labelled keys.

## W02 Replenishing two storage locations

Confirm available space at both storage locations, then scan the two replenishment batches. Deliver each batch of boxes to its corresponding location and check the quantity. Close the work order after both location records are complete. The scanner and registration terminal are shared.

**S₀**: bin_a_available, bin_b_available, carton_a_available, carton_b_available, replenishment_order_ready

**Sg**: replenishment_order_closed

**Capacity-one resources**: bin_a, bin_b, carton_a, carton_b, scanner, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | check bin A capacity | bin A | {bin_a_available} | {bin_a_checked} | 1 | {bin_a} | {L} | single |
| t2 | check bin B capacity | bin B | {bin_b_available} | {bin_b_checked} | 1 | {bin_b} | {R} | single |
| t3 | scan replenishment carton A | carton A | {carton_a_available, replenishment_order_ready} | {carton_a_scanned} | 2 | {carton_a, scanner} | {L} | single |
| t4 | scan replenishment carton B | carton B | {carton_b_available, replenishment_order_ready} | {carton_b_scanned} | 2 | {carton_b, scanner} | {R} | single |
| t5 | place carton A in bin A | carton A | {bin_a_checked, carton_a_scanned} | {bin_a_replenished} | 3 | {bin_a, carton_a} | {L} | single |
| t6 | place carton B in bin B | carton B | {bin_b_checked, carton_b_scanned} | {bin_b_replenished} | 3 | {bin_b, carton_b} | {R} | single |
| t7 | record bin A quantity | bin A record | {bin_a_replenished} | {bin_a_recorded} | 2 | {terminal} | {L, R} | single |
| t8 | record bin B quantity | bin B record | {bin_b_replenished} | {bin_b_recorded} | 2 | {terminal} | {R} | single |
| t9 | close replenishment order | replenishment order | {bin_a_recorded, bin_b_recorded, replenishment_order_ready} | {replenishment_order_closed} | 1 | {terminal} | {L} | single |

**Original typed relations**

- E_state: (t1, t5, bin_a_checked); (t3, t5, carton_a_scanned); (t2, t6, bin_b_checked); (t4, t6, carton_b_scanned); (t5, t7, bin_a_replenished); (t6, t8, bin_b_replenished); (t7, t9, bin_a_recorded); (t8, t9, bin_b_recorded)
- E_sync: ∅
- E_mutex: (t3, t4, scanner); (t7, t8, terminal)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 1 |
| t2 | R | 0 | 1 |
| t3 | L | 1 | 3 |
| t4 | R | 3 | 5 |
| t5 | L | 3 | 6 |
| t6 | R | 5 | 8 |
| t7 | L | 6 | 8 |
| t8 | R | 8 | 10 |
| t9 | L | 10 | 11 |

Symbolic makespan 11; fully serial time for the same nodes 17; corresponding speedup 1.5455. Original and post-processed relation sets agree using complete labelled keys.

## W03 Securing a large item on a pallet

Inspect the pallet and prepare the large item and corner protectors. Place the large item using both units and install both sets of corner protectors. Thread the left and right straps separately, secure them using a shared tensioning tool, inspect the result and apply the pallet identification label.

**S₀**: pallet_available, load_available, corners_available, strap_left_available, strap_right_available, shipping_record_ready

**Sg**: pallet_identified

**Capacity-one resources**: pallet, load, corners, strap_left, strap_right, tensioner, printer

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | inspect pallet | pallet | {pallet_available} | {pallet_checked} | 2 | {pallet} | {L} | single |
| t2 | prepare large load | load | {load_available} | {load_prepared} | 3 | {load} | {R} | single |
| t3 | prepare corner protectors | corners | {corners_available} | {corners_prepared} | 1 | {corners} | {L, R} | single |
| t4 | prepare left strap | left strap | {strap_left_available} | {left_strap_prepared} | 1 | {strap_left} | {L} | single |
| t5 | prepare right strap | right strap | {strap_right_available} | {right_strap_prepared} | 1 | {strap_right} | {R} | single |
| t6 | place load on pallet | load | {pallet_checked, load_prepared} | {load_on_pallet} | 4 | {pallet, load} | {B} | cooperative |
| t7 | fit left corner protectors | load left corners | {load_on_pallet, corners_prepared} | {left_corners_fitted} | 2 | {pallet, load, corners} | {L} | single |
| t8 | fit right corner protectors | load right corners | {load_on_pallet, corners_prepared} | {right_corners_fitted} | 2 | {pallet, load, corners} | {R} | single |
| t9 | thread left strap | left strap | {left_corners_fitted, left_strap_prepared} | {left_strap_threaded} | 2 | {pallet, strap_left} | {L} | single |
| t10 | thread right strap | right strap | {right_corners_fitted, right_strap_prepared} | {right_strap_threaded} | 2 | {pallet, strap_right} | {R} | single |
| t11 | tension left strap | left strap | {left_strap_threaded} | {left_strap_tensioned} | 2 | {pallet, strap_left, tensioner} | {L} | single |
| t12 | tension right strap | right strap | {right_strap_threaded} | {right_strap_tensioned} | 2 | {pallet, strap_right, tensioner} | {R} | single |
| t13 | verify pallet restraint | pallet load | {left_strap_tensioned, right_strap_tensioned} | {pallet_restraint_verified} | 2 | {pallet, load} | {L, R} | single |
| t14 | apply pallet identity | pallet | {pallet_restraint_verified, shipping_record_ready} | {pallet_identified} | 1 | {pallet, printer} | {L} | single |

**Original typed relations**

- E_state: (t1, t6, pallet_checked); (t2, t6, load_prepared); (t6, t7, load_on_pallet); (t3, t7, corners_prepared); (t6, t8, load_on_pallet); (t3, t8, corners_prepared); (t7, t9, left_corners_fitted); (t4, t9, left_strap_prepared); (t8, t10, right_corners_fitted); (t5, t10, right_strap_prepared); (t9, t11, left_strap_threaded); (t10, t12, right_strap_threaded); (t11, t13, left_strap_tensioned); (t12, t13, right_strap_tensioned); (t13, t14, pallet_restraint_verified)
- E_sync: (t1, t6, pallet_checked); (t2, t6, load_prepared)
- E_mutex: (t7, t8, pallet); (t8, t9, pallet); (t9, t10, pallet); (t10, t11, pallet); (t11, t12, tensioner)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 3 |
| t3 | L | 2 | 3 |
| t4 | L | 3 | 4 |
| t5 | R | 3 | 4 |
| t6 | L+R | 4 | 8 |
| t7 | L | 8 | 10 |
| t8 | R | 10 | 12 |
| t9 | L | 12 | 14 |
| t10 | R | 14 | 16 |
| t11 | L | 16 | 18 |
| t12 | R | 18 | 20 |
| t13 | L | 20 | 22 |
| t14 | L | 22 | 23 |

Symbolic makespan 23; fully serial time for the same nodes 27; corresponding speedup 1.1739. Original and post-processed relation sets agree using complete labelled keys.

## W04 Order kitting from three sources

Retrieve components A, B and C from three separate sources and verify them using a shared scanner. Prepare the order tote and place the three components in their assigned compartments. Check kit completeness, transfer the tote using both units and register completion.

**S₀**: stock_a_ready, stock_b_ready, stock_c_ready, order_tote_empty, pick_order_ready, dispatch_area_ready

**Sg**: kit_dispatch_recorded

**Capacity-one resources**: stock_a, stock_b, stock_c, scanner, order_tote, terminal

| id | action | object | Pre | Post | d | Res | Cand | mode |
|---|---|---|---|---|---:|---|---|---|
| t1 | pick component A | component A | {stock_a_ready, pick_order_ready} | {component_a_picked} | 2 | {stock_a} | {L} | single |
| t2 | pick component B | component B | {stock_b_ready, pick_order_ready} | {component_b_picked} | 2 | {stock_b} | {R} | single |
| t3 | pick component C | component C | {stock_c_ready, pick_order_ready} | {component_c_picked} | 3 | {stock_c} | {L, R} | single |
| t4 | verify component A code | component A | {component_a_picked} | {component_a_verified} | 1 | {scanner} | {L} | single |
| t5 | verify component B code | component B | {component_b_picked} | {component_b_verified} | 1 | {scanner} | {R} | single |
| t6 | verify component C code | component C | {component_c_picked} | {component_c_verified} | 1 | {scanner} | {L, R} | single |
| t7 | prepare order tote | order tote | {order_tote_empty} | {order_tote_prepared} | 2 | {order_tote} | {L} | single |
| t8 | load component A | order tote | {component_a_verified, order_tote_prepared} | {component_a_loaded} | 1 | {order_tote} | {L} | single |
| t9 | load component B | order tote | {component_b_verified, order_tote_prepared} | {component_b_loaded} | 1 | {order_tote} | {R} | single |
| t10 | load component C | order tote | {component_c_verified, order_tote_prepared} | {component_c_loaded} | 1 | {order_tote} | {L, R} | single |
| t11 | verify complete kit | order tote | {component_a_loaded, component_b_loaded, component_c_loaded} | {order_kit_complete} | 2 | {order_tote} | {L} | single |
| t12 | transfer complete tote | order tote | {order_kit_complete, dispatch_area_ready} | {kit_at_dispatch} | 3 | {order_tote} | {B} | cooperative |
| t13 | record kit dispatch | dispatch record | {kit_at_dispatch, pick_order_ready} | {kit_dispatch_recorded} | 1 | {terminal} | {R} | single |

**Original typed relations**

- E_state: (t1, t4, component_a_picked); (t2, t5, component_b_picked); (t3, t6, component_c_picked); (t4, t8, component_a_verified); (t7, t8, order_tote_prepared); (t5, t9, component_b_verified); (t7, t9, order_tote_prepared); (t6, t10, component_c_verified); (t7, t10, order_tote_prepared); (t8, t11, component_a_loaded); (t9, t11, component_b_loaded); (t10, t11, component_c_loaded); (t11, t12, order_kit_complete); (t12, t13, kit_at_dispatch)
- E_sync: (t11, t12, order_kit_complete)
- E_mutex: (t4, t5, scanner); (t5, t6, scanner); (t8, t9, order_tote); (t9, t10, order_tote)
- E_order: ∅

**Strict schedule output** (half-open intervals [start, finish))

| Node | Occupancy | Start | Finish |
|---|---|---:|---:|
| t1 | L | 0 | 2 |
| t2 | R | 0 | 2 |
| t3 | L | 2 | 5 |
| t4 | L | 5 | 6 |
| t5 | R | 6 | 7 |
| t6 | L | 7 | 8 |
| t7 | L | 8 | 10 |
| t8 | L | 10 | 11 |
| t9 | R | 11 | 12 |
| t10 | L | 12 | 13 |
| t11 | L | 13 | 15 |
| t12 | L+R | 15 | 18 |
| t13 | R | 18 | 19 |

Symbolic makespan 19; fully serial time for the same nodes 21; corresponding speedup 1.1053. Original and post-processed relation sets agree using complete labelled keys.
