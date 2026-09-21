window.ATG_REPLAYS = {
  "version": "v7_70",
  "playback_seconds_per_cycle": 14,
  "cases": [
    {
      "id": "controlled-pour",
      "title": "Controlled drink preparation",
      "record_id": "pour_drink_001",
      "subtitle": "Controlled record pour_drink_001 · 6 nodes · 1 cooperative task",
      "note": "This is the six-node controlled experiment, not the five-node tea illustration. The raw candidate was rejected; the animation shows only the accepted full-method schedule.",
      "plans": [
        {
          "method": "full",
          "label": "Full method",
          "graph": {
            "nodes": [
              {
                "id": "v1",
                "action": "stabilize",
                "object": "cup",
                "pre_state": [
                  "cup_on_mat"
                ],
                "post_state": [
                  "cup_stabilized"
                ],
                "duration": 1.81,
                "resource": [
                  "cup"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "v2",
                "action": "grasp",
                "object": "kettle",
                "pre_state": [
                  "kettle_on_stand"
                ],
                "post_state": [
                  "kettle_grasped"
                ],
                "duration": 2.69,
                "resource": [
                  "kettle"
                ],
                "candidate_arm": [
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "v3",
                "action": "pour",
                "object": "kettle",
                "pre_state": [
                  "cup_stabilized",
                  "kettle_grasped",
                  "water_in_kettle"
                ],
                "post_state": [
                  "cup_filled"
                ],
                "duration": 5.37,
                "resource": [
                  "cup",
                  "kettle"
                ],
                "candidate_arm": [
                  "both"
                ],
                "mode": "cooperative",
                "workspace": "shared",
                "target": "cup"
              },
              {
                "id": "v4",
                "action": "place",
                "object": "kettle",
                "pre_state": [
                  "kettle_grasped",
                  "cup_filled"
                ],
                "post_state": [
                  "kettle_returned"
                ],
                "duration": 1.71,
                "resource": [
                  "kettle"
                ],
                "candidate_arm": [
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "v5",
                "action": "insert",
                "object": "tea_bag",
                "pre_state": [
                  "tea_bag_available",
                  "cup_filled"
                ],
                "post_state": [
                  "tea_bag_in_cup"
                ],
                "duration": 1.75,
                "resource": [
                  "tea_bag"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "v6",
                "action": "stir",
                "object": "spoon",
                "pre_state": [
                  "spoon_available",
                  "tea_bag_in_cup"
                ],
                "post_state": [
                  "drink_ready"
                ],
                "duration": 2.68,
                "resource": [
                  "spoon",
                  "cup"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              }
            ],
            "edges": [
              {
                "source": "v1",
                "target": "v3",
                "type": "state_support",
                "reason": "v1 produces cup_stabilized for v3",
                "state": "cup_stabilized"
              },
              {
                "source": "v2",
                "target": "v4",
                "type": "state_support",
                "reason": "v2 produces kettle_grasped for v4",
                "state": "kettle_grasped"
              },
              {
                "source": "v3",
                "target": "v4",
                "type": "state_support",
                "reason": "v3 produces cup_filled for v4",
                "state": "cup_filled"
              },
              {
                "source": "v3",
                "target": "v5",
                "type": "state_support",
                "reason": "v3 produces cup_filled for v5",
                "state": "cup_filled"
              },
              {
                "source": "v5",
                "target": "v6",
                "type": "state_support",
                "reason": "v5 produces tea_bag_in_cup for v6",
                "state": "tea_bag_in_cup"
              },
              {
                "source": "v2",
                "target": "v3",
                "type": "state_support",
                "reason": "repaired explicit support for kettle_grasped",
                "state": "kettle_grasped"
              },
              {
                "source": "v1",
                "target": "v3",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "cup_stabilized"
              },
              {
                "source": "v2",
                "target": "v3",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "kettle_grasped"
              }
            ]
          },
          "schedule": {
            "estimated_makespan": 12.49,
            "waiting_time": 0.88,
            "executor_utilization": 0.8559,
            "sync_stability": 1.0,
            "verification": {
              "valid": true,
              "violations": []
            },
            "items": [
              {
                "node_id": "v1",
                "action": "stabilize",
                "object": "cup",
                "start": 0.0,
                "finish": 1.81,
                "executors": [
                  "left"
                ],
                "resources": [
                  "cup"
                ]
              },
              {
                "node_id": "v2",
                "action": "grasp",
                "object": "kettle",
                "start": 0.0,
                "finish": 2.69,
                "executors": [
                  "right"
                ],
                "resources": [
                  "kettle"
                ]
              },
              {
                "node_id": "v3",
                "action": "pour",
                "object": "kettle",
                "start": 2.69,
                "finish": 8.06,
                "executors": [
                  "left",
                  "right"
                ],
                "resources": [
                  "cup",
                  "kettle"
                ]
              },
              {
                "node_id": "v4",
                "action": "place",
                "object": "kettle",
                "start": 8.06,
                "finish": 9.77,
                "executors": [
                  "right"
                ],
                "resources": [
                  "kettle"
                ]
              },
              {
                "node_id": "v5",
                "action": "insert",
                "object": "tea_bag",
                "start": 8.06,
                "finish": 9.81,
                "executors": [
                  "left"
                ],
                "resources": [
                  "tea_bag"
                ]
              },
              {
                "node_id": "v6",
                "action": "stir",
                "object": "spoon",
                "start": 9.81,
                "finish": 12.49,
                "executors": [
                  "left"
                ],
                "resources": [
                  "spoon",
                  "cup"
                ]
              }
            ]
          },
          "metrics": {
            "id": "pour_drink_001",
            "group": "controlled160",
            "method": "full",
            "accepted": true,
            "edge_f1": 1.0,
            "makespan": 12.49,
            "speedup": 1.2818254603682948,
            "net_added": 1,
            "net_removed": 3
          }
        }
      ],
      "sources": [
        {
          "path": "reproduction/results/fair_comparison/comparison_details.jsonl",
          "sha256": "7d8ef2c8ecb8e7a28b72f6339fef5ef5a8e46222115ff4a7829f7aad0d527dcd",
          "record_id": "pour_drink_001",
          "method": "full"
        },
        {
          "path": "reproduction/results/fair_comparison/frozen_comparison_inputs.jsonl",
          "sha256": "526df055becd04614cbb0ac7764a19ebce9cf765e853c1e4d9dd5401f9450919",
          "record_id": "pour_drink_001"
        }
      ],
      "horizon": 12.49,
      "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1040 492\" role=\"img\" aria-labelledby=\"replay-svg-title replay-svg-desc\"><title id=\"replay-svg-title\">Controlled drink preparation</title><desc id=\"replay-svg-desc\">Replay of archived accepted schedules. Time is symbolic. Purple joint tasks occupy both L and R. Rectangles show exact stored start and finish times.</desc><style>text{font-family:Arial,sans-serif;fill:#26384d}.label{font-size:13px}.tiny{font-size:11px}.clock{stroke:#d76c40;stroke-width:2}.task-progress{pointer-events:none}.node-id{font-weight:700;font-size:14px}.node-action{font-size:11px}.graph-edge{fill:none;stroke:#99aac0;stroke-width:1.4}</style><defs><marker id=\"replay-arrow\" markerWidth=\"7\" markerHeight=\"7\" refX=\"6\" refY=\"3.5\" orient=\"auto\"><path d=\"M0,0 L7,3.5 L0,7\" fill=\"#99aac0\"/></marker></defs><rect width=\"1040\" height=\"492\" rx=\"8\" fill=\"white\"/><text x=\"68\" y=\"299\" font-size=\"15\" font-weight=\"700\">Full method</text><text x=\"992\" y=\"299\" text-anchor=\"end\" class=\"label\">Makespan 12.49</text><text x=\"35\" y=\"350\" font-size=\"16\" font-weight=\"700\">L</text><rect x=\"68\" y=\"322\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><text x=\"35\" y=\"398\" font-size=\"16\" font-weight=\"700\">R</text><rect x=\"68\" y=\"370\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><line x1=\"68.00000\" x2=\"68.00000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"68.00000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">0</text><line x1=\"252.80000\" x2=\"252.80000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"252.80000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">2.498</text><line x1=\"437.60000\" x2=\"437.60000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"437.60000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">4.996</text><line x1=\"622.40000\" x2=\"622.40000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"622.40000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">7.494</text><line x1=\"807.20000\" x2=\"807.20000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"807.20000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">9.992</text><line x1=\"992.00000\" x2=\"992.00000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"992.00000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">12.49</text><g data-task=\"v1\" data-plan=\"0\"><title>v1 · stabilize · cup | [0, 1.81) | units: left | resources: cup</title><rect x=\"68.00000\" y=\"322\" width=\"133.90232\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v1\" data-plan=\"0\" x=\"68.00000\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"134.95116\" y=\"348.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v1</text></g><g data-task=\"v2\" data-plan=\"0\"><title>v2 · grasp · kettle | [0, 2.69) | units: right | resources: kettle</title><rect x=\"68.00000\" y=\"370\" width=\"199.00400\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v2\" data-plan=\"0\" x=\"68.00000\" y=\"370\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"167.50200\" y=\"396.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v2</text></g><g data-task=\"v3\" data-plan=\"0\"><title>v3 · pour · kettle | [2.69, 8.06) | units: left, right | resources: cup, kettle</title><rect x=\"267.00400\" y=\"322\" width=\"397.26821\" height=\"90\" rx=\"3\" fill=\"#8056a9\" fill-opacity=\".13\" stroke=\"#8056a9\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v3\" data-plan=\"0\" x=\"267.00400\" y=\"322\" width=\"0\" height=\"90\" rx=\"3\" fill=\"#8056a9\" fill-opacity=\".72\"></rect><text x=\"465.63811\" y=\"372.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v3 · B</text></g><g data-task=\"v4\" data-plan=\"0\"><title>v4 · place · kettle | [8.06, 9.77) | units: right | resources: kettle</title><rect x=\"664.27222\" y=\"370\" width=\"126.50440\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v4\" data-plan=\"0\" x=\"664.27222\" y=\"370\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"727.52442\" y=\"396.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v4</text></g><g data-task=\"v5\" data-plan=\"0\"><title>v5 · insert · tea_bag | [8.06, 9.81) | units: left | resources: tea_bag</title><rect x=\"664.27222\" y=\"322\" width=\"129.46357\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v5\" data-plan=\"0\" x=\"664.27222\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"729.00400\" y=\"348.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v5</text></g><g data-task=\"v6\" data-plan=\"0\"><title>v6 · stir · spoon | [9.81, 12.49) | units: left | resources: spoon, cup</title><rect x=\"793.73579\" y=\"322\" width=\"198.26421\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"v6\" data-plan=\"0\" x=\"793.73579\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"892.86789\" y=\"348.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">v6</text></g><line class=\"clock\" data-clock=\"0\" x1=\"68\" x2=\"68\" y1=\"317\" y2=\"416\"></line><text x=\"68\" y=\"26\" class=\"label\">Accepted state-support projection</text><text x=\"992\" y=\"26\" text-anchor=\"end\" class=\"tiny\">All accepted relation types constrain the schedule.</text><path class=\"graph-edge\" d=\"M141.0,58.0 C186.0,58.0 307.3333333333333,117.0 350.3333333333333,117.0\" marker-end=\"url(#replay-arrow)\"><title>v1 → v3 | cup_stabilized</title></path><path class=\"graph-edge\" d=\"M141.0,176.0 C186.0,231.0 580.6666666666666,113.0 623.6666666666666,58.0\" marker-end=\"url(#replay-arrow)\"><title>v2 → v4 | kettle_grasped</title></path><path class=\"graph-edge\" d=\"M414.3333333333333,117.0 C459.3333333333333,117.0 580.6666666666666,58.0 623.6666666666666,58.0\" marker-end=\"url(#replay-arrow)\"><title>v3 → v4 | cup_filled</title></path><path class=\"graph-edge\" d=\"M414.3333333333333,117.0 C459.3333333333333,117.0 580.6666666666666,176.0 623.6666666666666,176.0\" marker-end=\"url(#replay-arrow)\"><title>v3 → v5 | cup_filled</title></path><path class=\"graph-edge\" d=\"M687.6666666666666,176.0 C732.6666666666666,176.0 854.0,117.0 897.0,117.0\" marker-end=\"url(#replay-arrow)\"><title>v5 → v6 | tea_bag_in_cup</title></path><path class=\"graph-edge\" d=\"M141.0,176.0 C186.0,176.0 307.3333333333333,117.0 350.3333333333333,117.0\" marker-end=\"url(#replay-arrow)\"><title>v2 → v3 | kettle_grasped</title></path><g><title>v1: stabilize cup</title><circle data-node=\"v1\" cx=\"110.0\" cy=\"58.0\" r=\"31\" fill=\"#376eaa\" fill-opacity=\".12\" stroke=\"#376eaa\" stroke-width=\"1.5\"></circle><text x=\"110.0\" y=\"62.0\" text-anchor=\"middle\" class=\"node-id\">v1</text><text x=\"110.0\" y=\"109.0\" text-anchor=\"middle\" class=\"node-action\">stabilize cup</text></g><g><title>v2: grasp kettle</title><circle data-node=\"v2\" cx=\"110.0\" cy=\"176.0\" r=\"31\" fill=\"#388b82\" fill-opacity=\".12\" stroke=\"#388b82\" stroke-width=\"1.5\"></circle><text x=\"110.0\" y=\"180.0\" text-anchor=\"middle\" class=\"node-id\">v2</text><text x=\"110.0\" y=\"227.0\" text-anchor=\"middle\" class=\"node-action\">grasp kettle</text></g><g><title>v3: pour kettle</title><circle data-node=\"v3\" cx=\"383.3333333333333\" cy=\"117.0\" r=\"31\" fill=\"#8056a9\" fill-opacity=\".12\" stroke=\"#8056a9\" stroke-width=\"1.5\"></circle><text x=\"383.3333333333333\" y=\"121.0\" text-anchor=\"middle\" class=\"node-id\">v3</text><text x=\"383.3333333333333\" y=\"168.0\" text-anchor=\"middle\" class=\"node-action\">pour kettle</text></g><g><title>v4: place kettle</title><circle data-node=\"v4\" cx=\"656.6666666666666\" cy=\"58.0\" r=\"31\" fill=\"#388b82\" fill-opacity=\".12\" stroke=\"#388b82\" stroke-width=\"1.5\"></circle><text x=\"656.6666666666666\" y=\"62.0\" text-anchor=\"middle\" class=\"node-id\">v4</text><text x=\"656.6666666666666\" y=\"109.0\" text-anchor=\"middle\" class=\"node-action\">place kettle</text></g><g><title>v5: insert tea_bag</title><circle data-node=\"v5\" cx=\"656.6666666666666\" cy=\"176.0\" r=\"31\" fill=\"#376eaa\" fill-opacity=\".12\" stroke=\"#376eaa\" stroke-width=\"1.5\"></circle><text x=\"656.6666666666666\" y=\"180.0\" text-anchor=\"middle\" class=\"node-id\">v5</text><text x=\"656.6666666666666\" y=\"227.0\" text-anchor=\"middle\" class=\"node-action\">insert tea_bag</text></g><g><title>v6: stir spoon</title><circle data-node=\"v6\" cx=\"930.0\" cy=\"117.0\" r=\"31\" fill=\"#376eaa\" fill-opacity=\".12\" stroke=\"#376eaa\" stroke-width=\"1.5\"></circle><text x=\"930.0\" y=\"121.0\" text-anchor=\"middle\" class=\"node-id\">v6</text><text x=\"930.0\" y=\"168.0\" text-anchor=\"middle\" class=\"node-action\">stir spoon</text></g><text x=\"68\" y=\"479\" class=\"tiny\">Time: symbolic input units · visual playback speed is arbitrary · archived schedules, not hardware footage</text></svg>"
    },
    {
      "id": "public-cooperation",
      "title": "Public parallel assembly",
      "record_id": "parallel_branch_light",
      "subtitle": "AssemblyGrid parallel_branch_light · 3 operations · source-checked",
      "note": "Two preparation operations run in parallel, then the cooperative join occupies both units. This replays the retained planning projection, not the original geometric simulator.",
      "plans": [
        {
          "method": "full",
          "label": "Full method",
          "graph": {
            "nodes": [
              {
                "id": "prepare_a",
                "action": "prepare",
                "object": "PA",
                "pre_state": [
                  "material:A"
                ],
                "post_state": [
                  "material:PA",
                  "completed:prepare_a"
                ],
                "duration": 3.0,
                "resource": [],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "prepare_b",
                "action": "prepare",
                "object": "PB",
                "pre_state": [
                  "material:B"
                ],
                "post_state": [
                  "material:PB",
                  "completed:prepare_b"
                ],
                "duration": 3.0,
                "resource": [],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "join_branches",
                "action": "assemble",
                "object": "FINAL",
                "pre_state": [
                  "material:PA",
                  "material:PB",
                  "completed:prepare_a",
                  "completed:prepare_b"
                ],
                "post_state": [
                  "material:FINAL",
                  "completed:join_branches"
                ],
                "duration": 4.0,
                "resource": [],
                "candidate_arm": [
                  "both"
                ],
                "mode": "cooperative",
                "workspace": "shared"
              }
            ],
            "edges": [
              {
                "source": "prepare_a",
                "target": "join_branches",
                "type": "state_support",
                "reason": "",
                "state": "completed:prepare_a"
              },
              {
                "source": "prepare_b",
                "target": "join_branches",
                "type": "state_support",
                "reason": "",
                "state": "completed:prepare_b"
              },
              {
                "source": "prepare_a",
                "target": "join_branches",
                "type": "state_support",
                "reason": "repaired explicit support for material:PA",
                "state": "material:PA"
              },
              {
                "source": "prepare_b",
                "target": "join_branches",
                "type": "state_support",
                "reason": "repaired explicit support for material:PB",
                "state": "material:PB"
              },
              {
                "source": "prepare_a",
                "target": "join_branches",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "completed:prepare_a"
              },
              {
                "source": "prepare_b",
                "target": "join_branches",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "completed:prepare_b"
              },
              {
                "source": "prepare_a",
                "target": "join_branches",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "material:PA"
              },
              {
                "source": "prepare_b",
                "target": "join_branches",
                "type": "synchronization",
                "reason": "cooperative action requires synchronized input states",
                "state": "material:PB"
              }
            ]
          },
          "schedule": {
            "estimated_makespan": 7.0,
            "waiting_time": 0.0,
            "executor_utilization": 1.0,
            "sync_stability": 1.0,
            "verification": {
              "valid": true,
              "violations": []
            },
            "items": [
              {
                "node_id": "prepare_a",
                "action": "prepare",
                "object": "PA",
                "start": 0.0,
                "finish": 3.0,
                "executors": [
                  "left"
                ],
                "resources": []
              },
              {
                "node_id": "prepare_b",
                "action": "prepare",
                "object": "PB",
                "start": 0.0,
                "finish": 3.0,
                "executors": [
                  "right"
                ],
                "resources": []
              },
              {
                "node_id": "join_branches",
                "action": "assemble",
                "object": "FINAL",
                "start": 3.0,
                "finish": 7.0,
                "executors": [
                  "left",
                  "right"
                ],
                "resources": []
              }
            ]
          },
          "metrics": {
            "id": "parallel_branch_light",
            "group": "public_recipe",
            "method": "full",
            "nodes": 3,
            "B_nodes": 1,
            "resource_labels": 0,
            "accepted": true,
            "source_semantics_valid": true,
            "makespan": 7.0,
            "speedup": 1.4285714285714286
          }
        }
      ],
      "sources": [
        {
          "path": "reproduction/results/external_discrete_run01/details.jsonl",
          "sha256": "53f850e04e019baaaf34c9090dbdd2afe45302689f136f37c45eaeeacdf4e237",
          "record_id": "parallel_branch_light",
          "method": "full"
        },
        {
          "path": "reproduction/results/external_discrete_run01/frozen_cases.json",
          "sha256": "095fef49c96a559d91217736c46646effbe90f7939ead37082e80df61280ddc3",
          "record_id": "parallel_branch_light"
        }
      ],
      "horizon": 7.0,
      "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1040 492\" role=\"img\" aria-labelledby=\"replay-svg-title replay-svg-desc\"><title id=\"replay-svg-title\">Public parallel assembly</title><desc id=\"replay-svg-desc\">Replay of archived accepted schedules. Time is symbolic. Purple joint tasks occupy both L and R. Rectangles show exact stored start and finish times.</desc><style>text{font-family:Arial,sans-serif;fill:#26384d}.label{font-size:13px}.tiny{font-size:11px}.clock{stroke:#d76c40;stroke-width:2}.task-progress{pointer-events:none}.node-id{font-weight:700;font-size:14px}.node-action{font-size:11px}.graph-edge{fill:none;stroke:#99aac0;stroke-width:1.4}</style><defs><marker id=\"replay-arrow\" markerWidth=\"7\" markerHeight=\"7\" refX=\"6\" refY=\"3.5\" orient=\"auto\"><path d=\"M0,0 L7,3.5 L0,7\" fill=\"#99aac0\"/></marker></defs><rect width=\"1040\" height=\"492\" rx=\"8\" fill=\"white\"/><text x=\"68\" y=\"299\" font-size=\"15\" font-weight=\"700\">Full method</text><text x=\"992\" y=\"299\" text-anchor=\"end\" class=\"label\">Makespan 7</text><text x=\"35\" y=\"350\" font-size=\"16\" font-weight=\"700\">L</text><rect x=\"68\" y=\"322\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><text x=\"35\" y=\"398\" font-size=\"16\" font-weight=\"700\">R</text><rect x=\"68\" y=\"370\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><line x1=\"68.00000\" x2=\"68.00000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"68.00000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">0</text><line x1=\"252.80000\" x2=\"252.80000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"252.80000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">1.4</text><line x1=\"437.60000\" x2=\"437.60000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"437.60000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">2.8</text><line x1=\"622.40000\" x2=\"622.40000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"622.40000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">4.2</text><line x1=\"807.20000\" x2=\"807.20000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"807.20000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">5.6</text><line x1=\"992.00000\" x2=\"992.00000\" y1=\"322\" y2=\"412\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"992.00000\" y=\"434\" text-anchor=\"middle\" class=\"tiny\">7</text><g data-task=\"prepare_a\" data-plan=\"0\"><title>prepare_a · prepare · PA | [0, 3) | units: left | resources: none declared</title><rect x=\"68.00000\" y=\"322\" width=\"396.00000\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"prepare_a\" data-plan=\"0\" x=\"68.00000\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"266.00000\" y=\"348.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">prepare_a</text></g><g data-task=\"prepare_b\" data-plan=\"0\"><title>prepare_b · prepare · PB | [0, 3) | units: right | resources: none declared</title><rect x=\"68.00000\" y=\"370\" width=\"396.00000\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"prepare_b\" data-plan=\"0\" x=\"68.00000\" y=\"370\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"266.00000\" y=\"396.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">prepare_b</text></g><g data-task=\"join_branches\" data-plan=\"0\"><title>join_branches · assemble · FINAL | [3, 7) | units: left, right | resources: none declared</title><rect x=\"464.00000\" y=\"322\" width=\"528.00000\" height=\"90\" rx=\"3\" fill=\"#8056a9\" fill-opacity=\".13\" stroke=\"#8056a9\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"join_branches\" data-plan=\"0\" x=\"464.00000\" y=\"322\" width=\"0\" height=\"90\" rx=\"3\" fill=\"#8056a9\" fill-opacity=\".72\"></rect><text x=\"728.00000\" y=\"372.0\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"600\">join_branches · B</text></g><line class=\"clock\" data-clock=\"0\" x1=\"68\" x2=\"68\" y1=\"317\" y2=\"416\"></line><text x=\"68\" y=\"26\" class=\"label\">Accepted state-support projection</text><text x=\"992\" y=\"26\" text-anchor=\"end\" class=\"tiny\">All accepted relation types constrain the schedule.</text><path class=\"graph-edge\" d=\"M141.0,58.0 C186.0,58.0 854.0,117.0 897.0,117.0\" marker-end=\"url(#replay-arrow)\"><title>prepare_a → join_branches | completed:prepare_a, material:PA</title></path><path class=\"graph-edge\" d=\"M141.0,176.0 C186.0,176.0 854.0,117.0 897.0,117.0\" marker-end=\"url(#replay-arrow)\"><title>prepare_b → join_branches | completed:prepare_b, material:PB</title></path><g><title>prepare_a: prepare PA</title><circle data-node=\"prepare_a\" cx=\"110.0\" cy=\"58.0\" r=\"31\" fill=\"#376eaa\" fill-opacity=\".12\" stroke=\"#376eaa\" stroke-width=\"1.5\"></circle><text x=\"110.0\" y=\"54.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\"><tspan x=\"110.0\">prepare</tspan><tspan x=\"110.0\" dy=\"14\">a</tspan></text><text x=\"110.0\" y=\"109.0\" text-anchor=\"middle\" class=\"node-action\">prepare PA</text></g><g><title>prepare_b: prepare PB</title><circle data-node=\"prepare_b\" cx=\"110.0\" cy=\"176.0\" r=\"31\" fill=\"#388b82\" fill-opacity=\".12\" stroke=\"#388b82\" stroke-width=\"1.5\"></circle><text x=\"110.0\" y=\"172.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\"><tspan x=\"110.0\">prepare</tspan><tspan x=\"110.0\" dy=\"14\">b</tspan></text><text x=\"110.0\" y=\"227.0\" text-anchor=\"middle\" class=\"node-action\">prepare PB</text></g><g><title>join_branches: assemble FINAL</title><circle data-node=\"join_branches\" cx=\"930.0\" cy=\"117.0\" r=\"31\" fill=\"#8056a9\" fill-opacity=\".12\" stroke=\"#8056a9\" stroke-width=\"1.5\"></circle><text x=\"930.0\" y=\"113.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\"><tspan x=\"930.0\">join</tspan><tspan x=\"930.0\" dy=\"14\">branches</tspan></text><text x=\"930.0\" y=\"168.0\" text-anchor=\"middle\" class=\"node-action\">assemble FINAL</text></g><text x=\"68\" y=\"479\" class=\"tiny\">Time: symbolic input units · visual playback speed is arbitrary · archived schedules, not hardware footage</text></svg>"
    },
    {
      "id": "resource-comparison",
      "title": "Resource-ordering comparison",
      "record_id": "ft06",
      "subtitle": "OR-Library ft06 two-unit projection · 36 operations · 6 resources",
      "note": "The two methods receive the same input and share order compression. Both accepted schedules passed independent source checks. This single instance illustrates a resource-ordering difference, not general superiority or the original job-shop optimum.",
      "plans": [
        {
          "method": "field_match_compressed",
          "label": "Field matching + shared compression",
          "graph": {
            "nodes": [
              {
                "id": "j00_o00",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_ready"
                ],
                "post_state": [
                  "j00_done00"
                ],
                "duration": 1.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o01",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done00"
                ],
                "post_state": [
                  "j00_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o02",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done01"
                ],
                "post_state": [
                  "j00_done02"
                ],
                "duration": 6.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o03",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done02"
                ],
                "post_state": [
                  "j00_done03"
                ],
                "duration": 7.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o04",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done03"
                ],
                "post_state": [
                  "j00_done04"
                ],
                "duration": 3.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o05",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done04"
                ],
                "post_state": [
                  "j00_done05"
                ],
                "duration": 6.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o00",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_ready"
                ],
                "post_state": [
                  "j01_done00"
                ],
                "duration": 8.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o01",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done00"
                ],
                "post_state": [
                  "j01_done01"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o02",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done01"
                ],
                "post_state": [
                  "j01_done02"
                ],
                "duration": 10.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o03",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done02"
                ],
                "post_state": [
                  "j01_done03"
                ],
                "duration": 10.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o04",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done03"
                ],
                "post_state": [
                  "j01_done04"
                ],
                "duration": 10.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o05",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done04"
                ],
                "post_state": [
                  "j01_done05"
                ],
                "duration": 4.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o00",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_ready"
                ],
                "post_state": [
                  "j02_done00"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o01",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done00"
                ],
                "post_state": [
                  "j02_done01"
                ],
                "duration": 4.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o02",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done01"
                ],
                "post_state": [
                  "j02_done02"
                ],
                "duration": 8.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o03",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done02"
                ],
                "post_state": [
                  "j02_done03"
                ],
                "duration": 9.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o04",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done03"
                ],
                "post_state": [
                  "j02_done04"
                ],
                "duration": 1.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o05",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done04"
                ],
                "post_state": [
                  "j02_done05"
                ],
                "duration": 7.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o00",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_ready"
                ],
                "post_state": [
                  "j03_done00"
                ],
                "duration": 5.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o01",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done00"
                ],
                "post_state": [
                  "j03_done01"
                ],
                "duration": 5.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o02",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done01"
                ],
                "post_state": [
                  "j03_done02"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o03",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done02"
                ],
                "post_state": [
                  "j03_done03"
                ],
                "duration": 3.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o04",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done03"
                ],
                "post_state": [
                  "j03_done04"
                ],
                "duration": 8.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o05",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done04"
                ],
                "post_state": [
                  "j03_done05"
                ],
                "duration": 9.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o00",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_ready"
                ],
                "post_state": [
                  "j04_done00"
                ],
                "duration": 9.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o01",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done00"
                ],
                "post_state": [
                  "j04_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o02",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done01"
                ],
                "post_state": [
                  "j04_done02"
                ],
                "duration": 5.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o03",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done02"
                ],
                "post_state": [
                  "j04_done03"
                ],
                "duration": 4.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o04",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done03"
                ],
                "post_state": [
                  "j04_done04"
                ],
                "duration": 3.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o05",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done04"
                ],
                "post_state": [
                  "j04_done05"
                ],
                "duration": 1.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o00",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_ready"
                ],
                "post_state": [
                  "j05_done00"
                ],
                "duration": 3.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o01",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done00"
                ],
                "post_state": [
                  "j05_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o02",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done01"
                ],
                "post_state": [
                  "j05_done02"
                ],
                "duration": 9.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o03",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done02"
                ],
                "post_state": [
                  "j05_done03"
                ],
                "duration": 10.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o04",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done03"
                ],
                "post_state": [
                  "j05_done04"
                ],
                "duration": 4.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o05",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done04"
                ],
                "post_state": [
                  "j05_done05"
                ],
                "duration": 1.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              }
            ],
            "edges": [
              {
                "source": "j00_o00",
                "target": "j00_o01",
                "type": "state_support",
                "reason": "",
                "state": "j00_done00"
              },
              {
                "source": "j00_o01",
                "target": "j00_o02",
                "type": "state_support",
                "reason": "",
                "state": "j00_done01"
              },
              {
                "source": "j00_o02",
                "target": "j00_o03",
                "type": "state_support",
                "reason": "",
                "state": "j00_done02"
              },
              {
                "source": "j00_o03",
                "target": "j00_o04",
                "type": "state_support",
                "reason": "",
                "state": "j00_done03"
              },
              {
                "source": "j00_o04",
                "target": "j00_o05",
                "type": "state_support",
                "reason": "",
                "state": "j00_done04"
              },
              {
                "source": "j01_o00",
                "target": "j01_o01",
                "type": "state_support",
                "reason": "",
                "state": "j01_done00"
              },
              {
                "source": "j01_o01",
                "target": "j01_o02",
                "type": "state_support",
                "reason": "",
                "state": "j01_done01"
              },
              {
                "source": "j01_o02",
                "target": "j01_o03",
                "type": "state_support",
                "reason": "",
                "state": "j01_done02"
              },
              {
                "source": "j01_o03",
                "target": "j01_o04",
                "type": "state_support",
                "reason": "",
                "state": "j01_done03"
              },
              {
                "source": "j01_o04",
                "target": "j01_o05",
                "type": "state_support",
                "reason": "",
                "state": "j01_done04"
              },
              {
                "source": "j02_o00",
                "target": "j02_o01",
                "type": "state_support",
                "reason": "",
                "state": "j02_done00"
              },
              {
                "source": "j02_o01",
                "target": "j02_o02",
                "type": "state_support",
                "reason": "",
                "state": "j02_done01"
              },
              {
                "source": "j02_o02",
                "target": "j02_o03",
                "type": "state_support",
                "reason": "",
                "state": "j02_done02"
              },
              {
                "source": "j02_o03",
                "target": "j02_o04",
                "type": "state_support",
                "reason": "",
                "state": "j02_done03"
              },
              {
                "source": "j02_o04",
                "target": "j02_o05",
                "type": "state_support",
                "reason": "",
                "state": "j02_done04"
              },
              {
                "source": "j03_o00",
                "target": "j03_o01",
                "type": "state_support",
                "reason": "",
                "state": "j03_done00"
              },
              {
                "source": "j03_o01",
                "target": "j03_o02",
                "type": "state_support",
                "reason": "",
                "state": "j03_done01"
              },
              {
                "source": "j03_o02",
                "target": "j03_o03",
                "type": "state_support",
                "reason": "",
                "state": "j03_done02"
              },
              {
                "source": "j03_o03",
                "target": "j03_o04",
                "type": "state_support",
                "reason": "",
                "state": "j03_done03"
              },
              {
                "source": "j03_o04",
                "target": "j03_o05",
                "type": "state_support",
                "reason": "",
                "state": "j03_done04"
              },
              {
                "source": "j04_o00",
                "target": "j04_o01",
                "type": "state_support",
                "reason": "",
                "state": "j04_done00"
              },
              {
                "source": "j04_o01",
                "target": "j04_o02",
                "type": "state_support",
                "reason": "",
                "state": "j04_done01"
              },
              {
                "source": "j04_o02",
                "target": "j04_o03",
                "type": "state_support",
                "reason": "",
                "state": "j04_done02"
              },
              {
                "source": "j04_o03",
                "target": "j04_o04",
                "type": "state_support",
                "reason": "",
                "state": "j04_done03"
              },
              {
                "source": "j04_o04",
                "target": "j04_o05",
                "type": "state_support",
                "reason": "",
                "state": "j04_done04"
              },
              {
                "source": "j05_o00",
                "target": "j05_o01",
                "type": "state_support",
                "reason": "",
                "state": "j05_done00"
              },
              {
                "source": "j05_o01",
                "target": "j05_o02",
                "type": "state_support",
                "reason": "",
                "state": "j05_done01"
              },
              {
                "source": "j05_o02",
                "target": "j05_o03",
                "type": "state_support",
                "reason": "",
                "state": "j05_done02"
              },
              {
                "source": "j05_o03",
                "target": "j05_o04",
                "type": "state_support",
                "reason": "",
                "state": "j05_done03"
              },
              {
                "source": "j05_o04",
                "target": "j05_o05",
                "type": "state_support",
                "reason": "",
                "state": "j05_done04"
              },
              {
                "source": "j00_o00",
                "target": "j01_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j02_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j03_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j00_o01",
                "target": "j01_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j02_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j03_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j00_o02",
                "target": "j01_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j02_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j03_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j00_o03",
                "target": "j01_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j02_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j03_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j00_o04",
                "target": "j01_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j02_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j03_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j04_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j00_o05",
                "target": "j01_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j00_o05",
                "target": "j02_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j00_o05",
                "target": "j03_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j00_o05",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j00_o05",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j01_o00",
                "target": "j02_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j01_o00",
                "target": "j03_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j01_o00",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j01_o00",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j01_o01",
                "target": "j02_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j01_o01",
                "target": "j03_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j01_o01",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j01_o01",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j01_o02",
                "target": "j02_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j01_o02",
                "target": "j03_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j01_o02",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j01_o02",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j01_o03",
                "target": "j02_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j01_o03",
                "target": "j03_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j01_o03",
                "target": "j04_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j01_o03",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j01_o04",
                "target": "j02_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j01_o04",
                "target": "j03_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j01_o04",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j01_o04",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j01_o05",
                "target": "j02_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j01_o05",
                "target": "j03_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j01_o05",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j01_o05",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j02_o00",
                "target": "j03_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j02_o00",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j02_o00",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j02_o01",
                "target": "j03_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j02_o01",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j02_o01",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j02_o02",
                "target": "j03_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j02_o02",
                "target": "j04_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j02_o02",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j02_o03",
                "target": "j03_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j02_o03",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j02_o03",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j02_o04",
                "target": "j03_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j02_o04",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j02_o04",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j02_o05",
                "target": "j03_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j02_o05",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j02_o05",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j03_o00",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j03_o00",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j03_o01",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j03_o01",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j03_o02",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j03_o02",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j03_o03",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j03_o03",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              },
              {
                "source": "j03_o04",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j03_o04",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j03_o05",
                "target": "j04_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j03_o05",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j04_o00",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine2"
              },
              {
                "source": "j04_o01",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine1"
              },
              {
                "source": "j04_o02",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine4"
              },
              {
                "source": "j04_o03",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine5"
              },
              {
                "source": "j04_o04",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine0"
              },
              {
                "source": "j04_o05",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "",
                "resource": "machine3"
              }
            ]
          },
          "schedule": {
            "estimated_makespan": 152.0,
            "waiting_time": 72.0,
            "executor_utilization": 0.648,
            "sync_stability": 1.0,
            "verification": {
              "valid": true,
              "violations": []
            },
            "items": [
              {
                "node_id": "j00_o00",
                "action": "process",
                "object": "job0",
                "start": 0.0,
                "finish": 1.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j00_o01",
                "action": "process",
                "object": "job0",
                "start": 1.0,
                "finish": 4.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j00_o02",
                "action": "process",
                "object": "job0",
                "start": 4.0,
                "finish": 10.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j00_o03",
                "action": "process",
                "object": "job0",
                "start": 10.0,
                "finish": 17.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j00_o04",
                "action": "process",
                "object": "job0",
                "start": 17.0,
                "finish": 20.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j00_o05",
                "action": "process",
                "object": "job0",
                "start": 20.0,
                "finish": 26.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j01_o00",
                "action": "process",
                "object": "job1",
                "start": 10.0,
                "finish": 18.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j01_o01",
                "action": "process",
                "object": "job1",
                "start": 18.0,
                "finish": 23.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j01_o02",
                "action": "process",
                "object": "job1",
                "start": 26.0,
                "finish": 36.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j01_o03",
                "action": "process",
                "object": "job1",
                "start": 36.0,
                "finish": 46.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j01_o04",
                "action": "process",
                "object": "job1",
                "start": 46.0,
                "finish": 56.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j01_o05",
                "action": "process",
                "object": "job1",
                "start": 56.0,
                "finish": 60.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j02_o00",
                "action": "process",
                "object": "job2",
                "start": 23.0,
                "finish": 28.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j02_o01",
                "action": "process",
                "object": "job2",
                "start": 60.0,
                "finish": 64.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j02_o02",
                "action": "process",
                "object": "job2",
                "start": 64.0,
                "finish": 72.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j02_o03",
                "action": "process",
                "object": "job2",
                "start": 72.0,
                "finish": 81.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j02_o04",
                "action": "process",
                "object": "job2",
                "start": 81.0,
                "finish": 82.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j02_o05",
                "action": "process",
                "object": "job2",
                "start": 82.0,
                "finish": 89.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j03_o00",
                "action": "process",
                "object": "job3",
                "start": 82.0,
                "finish": 87.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j03_o01",
                "action": "process",
                "object": "job3",
                "start": 87.0,
                "finish": 92.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j03_o02",
                "action": "process",
                "object": "job3",
                "start": 92.0,
                "finish": 97.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j03_o03",
                "action": "process",
                "object": "job3",
                "start": 97.0,
                "finish": 100.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j03_o04",
                "action": "process",
                "object": "job3",
                "start": 100.0,
                "finish": 108.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j03_o05",
                "action": "process",
                "object": "job3",
                "start": 108.0,
                "finish": 117.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j04_o00",
                "action": "process",
                "object": "job4",
                "start": 97.0,
                "finish": 106.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j04_o01",
                "action": "process",
                "object": "job4",
                "start": 106.0,
                "finish": 109.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j04_o02",
                "action": "process",
                "object": "job4",
                "start": 109.0,
                "finish": 114.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j04_o03",
                "action": "process",
                "object": "job4",
                "start": 117.0,
                "finish": 121.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j04_o04",
                "action": "process",
                "object": "job4",
                "start": 121.0,
                "finish": 124.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j04_o05",
                "action": "process",
                "object": "job4",
                "start": 124.0,
                "finish": 125.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j05_o00",
                "action": "process",
                "object": "job5",
                "start": 114.0,
                "finish": 117.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j05_o01",
                "action": "process",
                "object": "job5",
                "start": 125.0,
                "finish": 128.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j05_o02",
                "action": "process",
                "object": "job5",
                "start": 128.0,
                "finish": 137.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j05_o03",
                "action": "process",
                "object": "job5",
                "start": 137.0,
                "finish": 147.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j05_o04",
                "action": "process",
                "object": "job5",
                "start": 147.0,
                "finish": 151.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j05_o05",
                "action": "process",
                "object": "job5",
                "start": 151.0,
                "finish": 152.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              }
            ]
          },
          "metrics": {
            "id": "ft06",
            "group": "public_jobshop_projection",
            "method": "field_match_compressed",
            "nodes": 36,
            "B_nodes": 0,
            "resource_labels": 6,
            "accepted": true,
            "source_semantics_valid": true,
            "makespan": 152.0,
            "speedup": 1.2960526315789473
          }
        },
        {
          "method": "full",
          "label": "Full method",
          "graph": {
            "nodes": [
              {
                "id": "j00_o00",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_ready"
                ],
                "post_state": [
                  "j00_done00"
                ],
                "duration": 1.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o01",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done00"
                ],
                "post_state": [
                  "j00_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o02",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done01"
                ],
                "post_state": [
                  "j00_done02"
                ],
                "duration": 6.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o03",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done02"
                ],
                "post_state": [
                  "j00_done03"
                ],
                "duration": 7.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o04",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done03"
                ],
                "post_state": [
                  "j00_done04"
                ],
                "duration": 3.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j00_o05",
                "action": "process",
                "object": "job0",
                "pre_state": [
                  "j00_done04"
                ],
                "post_state": [
                  "j00_done05"
                ],
                "duration": 6.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o00",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_ready"
                ],
                "post_state": [
                  "j01_done00"
                ],
                "duration": 8.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o01",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done00"
                ],
                "post_state": [
                  "j01_done01"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o02",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done01"
                ],
                "post_state": [
                  "j01_done02"
                ],
                "duration": 10.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o03",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done02"
                ],
                "post_state": [
                  "j01_done03"
                ],
                "duration": 10.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o04",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done03"
                ],
                "post_state": [
                  "j01_done04"
                ],
                "duration": 10.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j01_o05",
                "action": "process",
                "object": "job1",
                "pre_state": [
                  "j01_done04"
                ],
                "post_state": [
                  "j01_done05"
                ],
                "duration": 4.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o00",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_ready"
                ],
                "post_state": [
                  "j02_done00"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o01",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done00"
                ],
                "post_state": [
                  "j02_done01"
                ],
                "duration": 4.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o02",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done01"
                ],
                "post_state": [
                  "j02_done02"
                ],
                "duration": 8.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o03",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done02"
                ],
                "post_state": [
                  "j02_done03"
                ],
                "duration": 9.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o04",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done03"
                ],
                "post_state": [
                  "j02_done04"
                ],
                "duration": 1.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j02_o05",
                "action": "process",
                "object": "job2",
                "pre_state": [
                  "j02_done04"
                ],
                "post_state": [
                  "j02_done05"
                ],
                "duration": 7.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o00",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_ready"
                ],
                "post_state": [
                  "j03_done00"
                ],
                "duration": 5.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o01",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done00"
                ],
                "post_state": [
                  "j03_done01"
                ],
                "duration": 5.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o02",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done01"
                ],
                "post_state": [
                  "j03_done02"
                ],
                "duration": 5.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o03",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done02"
                ],
                "post_state": [
                  "j03_done03"
                ],
                "duration": 3.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o04",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done03"
                ],
                "post_state": [
                  "j03_done04"
                ],
                "duration": 8.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j03_o05",
                "action": "process",
                "object": "job3",
                "pre_state": [
                  "j03_done04"
                ],
                "post_state": [
                  "j03_done05"
                ],
                "duration": 9.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o00",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_ready"
                ],
                "post_state": [
                  "j04_done00"
                ],
                "duration": 9.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o01",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done00"
                ],
                "post_state": [
                  "j04_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o02",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done01"
                ],
                "post_state": [
                  "j04_done02"
                ],
                "duration": 5.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o03",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done02"
                ],
                "post_state": [
                  "j04_done03"
                ],
                "duration": 4.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o04",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done03"
                ],
                "post_state": [
                  "j04_done04"
                ],
                "duration": 3.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j04_o05",
                "action": "process",
                "object": "job4",
                "pre_state": [
                  "j04_done04"
                ],
                "post_state": [
                  "j04_done05"
                ],
                "duration": 1.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o00",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_ready"
                ],
                "post_state": [
                  "j05_done00"
                ],
                "duration": 3.0,
                "resource": [
                  "machine1"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o01",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done00"
                ],
                "post_state": [
                  "j05_done01"
                ],
                "duration": 3.0,
                "resource": [
                  "machine3"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o02",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done01"
                ],
                "post_state": [
                  "j05_done02"
                ],
                "duration": 9.0,
                "resource": [
                  "machine5"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o03",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done02"
                ],
                "post_state": [
                  "j05_done03"
                ],
                "duration": 10.0,
                "resource": [
                  "machine0"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o04",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done03"
                ],
                "post_state": [
                  "j05_done04"
                ],
                "duration": 4.0,
                "resource": [
                  "machine4"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              },
              {
                "id": "j05_o05",
                "action": "process",
                "object": "job5",
                "pre_state": [
                  "j05_done04"
                ],
                "post_state": [
                  "j05_done05"
                ],
                "duration": 1.0,
                "resource": [
                  "machine2"
                ],
                "candidate_arm": [
                  "left",
                  "right"
                ],
                "mode": "single",
                "workspace": "shared"
              }
            ],
            "edges": [
              {
                "source": "j00_o00",
                "target": "j00_o01",
                "type": "state_support",
                "reason": "",
                "state": "j00_done00"
              },
              {
                "source": "j00_o01",
                "target": "j00_o02",
                "type": "state_support",
                "reason": "",
                "state": "j00_done01"
              },
              {
                "source": "j00_o02",
                "target": "j00_o03",
                "type": "state_support",
                "reason": "",
                "state": "j00_done02"
              },
              {
                "source": "j00_o03",
                "target": "j00_o04",
                "type": "state_support",
                "reason": "",
                "state": "j00_done03"
              },
              {
                "source": "j00_o04",
                "target": "j00_o05",
                "type": "state_support",
                "reason": "",
                "state": "j00_done04"
              },
              {
                "source": "j01_o00",
                "target": "j01_o01",
                "type": "state_support",
                "reason": "",
                "state": "j01_done00"
              },
              {
                "source": "j01_o01",
                "target": "j01_o02",
                "type": "state_support",
                "reason": "",
                "state": "j01_done01"
              },
              {
                "source": "j01_o02",
                "target": "j01_o03",
                "type": "state_support",
                "reason": "",
                "state": "j01_done02"
              },
              {
                "source": "j01_o03",
                "target": "j01_o04",
                "type": "state_support",
                "reason": "",
                "state": "j01_done03"
              },
              {
                "source": "j01_o04",
                "target": "j01_o05",
                "type": "state_support",
                "reason": "",
                "state": "j01_done04"
              },
              {
                "source": "j02_o00",
                "target": "j02_o01",
                "type": "state_support",
                "reason": "",
                "state": "j02_done00"
              },
              {
                "source": "j02_o01",
                "target": "j02_o02",
                "type": "state_support",
                "reason": "",
                "state": "j02_done01"
              },
              {
                "source": "j02_o02",
                "target": "j02_o03",
                "type": "state_support",
                "reason": "",
                "state": "j02_done02"
              },
              {
                "source": "j02_o03",
                "target": "j02_o04",
                "type": "state_support",
                "reason": "",
                "state": "j02_done03"
              },
              {
                "source": "j02_o04",
                "target": "j02_o05",
                "type": "state_support",
                "reason": "",
                "state": "j02_done04"
              },
              {
                "source": "j03_o00",
                "target": "j03_o01",
                "type": "state_support",
                "reason": "",
                "state": "j03_done00"
              },
              {
                "source": "j03_o01",
                "target": "j03_o02",
                "type": "state_support",
                "reason": "",
                "state": "j03_done01"
              },
              {
                "source": "j03_o02",
                "target": "j03_o03",
                "type": "state_support",
                "reason": "",
                "state": "j03_done02"
              },
              {
                "source": "j03_o03",
                "target": "j03_o04",
                "type": "state_support",
                "reason": "",
                "state": "j03_done03"
              },
              {
                "source": "j03_o04",
                "target": "j03_o05",
                "type": "state_support",
                "reason": "",
                "state": "j03_done04"
              },
              {
                "source": "j04_o00",
                "target": "j04_o01",
                "type": "state_support",
                "reason": "",
                "state": "j04_done00"
              },
              {
                "source": "j04_o01",
                "target": "j04_o02",
                "type": "state_support",
                "reason": "",
                "state": "j04_done01"
              },
              {
                "source": "j04_o02",
                "target": "j04_o03",
                "type": "state_support",
                "reason": "",
                "state": "j04_done02"
              },
              {
                "source": "j04_o03",
                "target": "j04_o04",
                "type": "state_support",
                "reason": "",
                "state": "j04_done03"
              },
              {
                "source": "j04_o04",
                "target": "j04_o05",
                "type": "state_support",
                "reason": "",
                "state": "j04_done04"
              },
              {
                "source": "j05_o00",
                "target": "j05_o01",
                "type": "state_support",
                "reason": "",
                "state": "j05_done00"
              },
              {
                "source": "j05_o01",
                "target": "j05_o02",
                "type": "state_support",
                "reason": "",
                "state": "j05_done01"
              },
              {
                "source": "j05_o02",
                "target": "j05_o03",
                "type": "state_support",
                "reason": "",
                "state": "j05_done02"
              },
              {
                "source": "j05_o03",
                "target": "j05_o04",
                "type": "state_support",
                "reason": "",
                "state": "j05_done03"
              },
              {
                "source": "j05_o04",
                "target": "j05_o05",
                "type": "state_support",
                "reason": "",
                "state": "j05_done04"
              },
              {
                "source": "j00_o00",
                "target": "j01_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j02_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j03_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j00_o00",
                "target": "j05_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j00_o01",
                "target": "j01_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j02_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j03_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j00_o01",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j01_o00",
                "target": "j00_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j02_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j03_o00",
                "target": "j00_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j00_o02",
                "target": "j05_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j00_o03",
                "target": "j01_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j02_o01",
                "target": "j00_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j03_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j00_o03",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j05_o01",
                "target": "j00_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j01_o03",
                "target": "j00_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j02_o02",
                "target": "j00_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j03_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j00_o04",
                "target": "j04_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j05_o02",
                "target": "j00_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j02_o05",
                "target": "j00_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j03_o04",
                "target": "j00_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j04_o02",
                "target": "j00_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j00_o05",
                "target": "j05_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j01_o00",
                "target": "j03_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j02_o00",
                "target": "j01_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j01_o01",
                "target": "j03_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j01_o01",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j01_o02",
                "target": "j02_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j01_o02",
                "target": "j03_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j01_o02",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j02_o02",
                "target": "j01_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j01_o03",
                "target": "j05_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j02_o03",
                "target": "j01_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j03_o01",
                "target": "j01_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j01_o04",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j01_o04",
                "target": "j05_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j03_o03",
                "target": "j01_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j01_o05",
                "target": "j04_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j02_o01",
                "target": "j05_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine3",
                "resource": "machine3"
              },
              {
                "source": "j03_o01",
                "target": "j02_o03",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              },
              {
                "source": "j02_o04",
                "target": "j04_o01",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j05_o00",
                "target": "j02_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine1",
                "resource": "machine1"
              },
              {
                "source": "j02_o05",
                "target": "j03_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j02_o05",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j03_o02",
                "target": "j04_o00",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine2",
                "resource": "machine2"
              },
              {
                "source": "j03_o04",
                "target": "j04_o02",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine4",
                "resource": "machine4"
              },
              {
                "source": "j04_o03",
                "target": "j03_o05",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine5",
                "resource": "machine5"
              },
              {
                "source": "j05_o03",
                "target": "j04_o04",
                "type": "resource_mutex",
                "reason": "minimum-critical-path orientation for shared resource machine0",
                "resource": "machine0"
              }
            ]
          },
          "schedule": {
            "estimated_makespan": 113.0,
            "waiting_time": 28.0,
            "executor_utilization": 0.8717,
            "sync_stability": 1.0,
            "verification": {
              "valid": true,
              "violations": []
            },
            "items": [
              {
                "node_id": "j00_o00",
                "action": "process",
                "object": "job0",
                "start": 0.0,
                "finish": 1.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j00_o01",
                "action": "process",
                "object": "job0",
                "start": 1.0,
                "finish": 4.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j01_o00",
                "action": "process",
                "object": "job1",
                "start": 0.0,
                "finish": 8.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j02_o00",
                "action": "process",
                "object": "job2",
                "start": 4.0,
                "finish": 9.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j01_o01",
                "action": "process",
                "object": "job1",
                "start": 9.0,
                "finish": 14.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j01_o02",
                "action": "process",
                "object": "job1",
                "start": 14.0,
                "finish": 24.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j02_o01",
                "action": "process",
                "object": "job2",
                "start": 9.0,
                "finish": 13.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j02_o02",
                "action": "process",
                "object": "job2",
                "start": 13.0,
                "finish": 21.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j01_o03",
                "action": "process",
                "object": "job1",
                "start": 24.0,
                "finish": 34.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j03_o00",
                "action": "process",
                "object": "job3",
                "start": 21.0,
                "finish": 26.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j00_o02",
                "action": "process",
                "object": "job0",
                "start": 26.0,
                "finish": 32.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j03_o01",
                "action": "process",
                "object": "job3",
                "start": 32.0,
                "finish": 37.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j02_o03",
                "action": "process",
                "object": "job2",
                "start": 37.0,
                "finish": 46.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j01_o04",
                "action": "process",
                "object": "job1",
                "start": 46.0,
                "finish": 56.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j03_o02",
                "action": "process",
                "object": "job3",
                "start": 37.0,
                "finish": 42.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j04_o00",
                "action": "process",
                "object": "job4",
                "start": 42.0,
                "finish": 51.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine2"
                ]
              },
              {
                "node_id": "j05_o00",
                "action": "process",
                "object": "job5",
                "start": 51.0,
                "finish": 54.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j02_o04",
                "action": "process",
                "object": "job2",
                "start": 54.0,
                "finish": 55.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j02_o05",
                "action": "process",
                "object": "job2",
                "start": 55.0,
                "finish": 62.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j04_o01",
                "action": "process",
                "object": "job4",
                "start": 56.0,
                "finish": 59.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine1"
                ]
              },
              {
                "node_id": "j05_o01",
                "action": "process",
                "object": "job5",
                "start": 59.0,
                "finish": 62.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j00_o03",
                "action": "process",
                "object": "job0",
                "start": 62.0,
                "finish": 69.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j03_o03",
                "action": "process",
                "object": "job3",
                "start": 69.0,
                "finish": 72.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j01_o05",
                "action": "process",
                "object": "job1",
                "start": 72.0,
                "finish": 76.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j03_o04",
                "action": "process",
                "object": "job3",
                "start": 72.0,
                "finish": 80.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j04_o02",
                "action": "process",
                "object": "job4",
                "start": 80.0,
                "finish": 85.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j05_o02",
                "action": "process",
                "object": "job5",
                "start": 80.0,
                "finish": 89.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j00_o04",
                "action": "process",
                "object": "job0",
                "start": 89.0,
                "finish": 92.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j00_o05",
                "action": "process",
                "object": "job0",
                "start": 92.0,
                "finish": 98.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j04_o03",
                "action": "process",
                "object": "job4",
                "start": 92.0,
                "finish": 96.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j03_o05",
                "action": "process",
                "object": "job3",
                "start": 96.0,
                "finish": 105.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine5"
                ]
              },
              {
                "node_id": "j05_o03",
                "action": "process",
                "object": "job5",
                "start": 98.0,
                "finish": 108.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j04_o04",
                "action": "process",
                "object": "job4",
                "start": 108.0,
                "finish": 111.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine0"
                ]
              },
              {
                "node_id": "j04_o05",
                "action": "process",
                "object": "job4",
                "start": 111.0,
                "finish": 112.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine3"
                ]
              },
              {
                "node_id": "j05_o04",
                "action": "process",
                "object": "job5",
                "start": 108.0,
                "finish": 112.0,
                "executors": [
                  "right"
                ],
                "resources": [
                  "machine4"
                ]
              },
              {
                "node_id": "j05_o05",
                "action": "process",
                "object": "job5",
                "start": 112.0,
                "finish": 113.0,
                "executors": [
                  "left"
                ],
                "resources": [
                  "machine2"
                ]
              }
            ]
          },
          "metrics": {
            "id": "ft06",
            "group": "public_jobshop_projection",
            "method": "full",
            "nodes": 36,
            "B_nodes": 0,
            "resource_labels": 6,
            "accepted": true,
            "source_semantics_valid": true,
            "makespan": 113.0,
            "speedup": 1.7433628318584071
          }
        }
      ],
      "sources": [
        {
          "path": "reproduction/results/external_discrete_run01/details.jsonl",
          "sha256": "53f850e04e019baaaf34c9090dbdd2afe45302689f136f37c45eaeeacdf4e237",
          "record_id": "ft06",
          "method": "field_match_compressed"
        },
        {
          "path": "reproduction/results/external_discrete_run01/details.jsonl",
          "sha256": "53f850e04e019baaaf34c9090dbdd2afe45302689f136f37c45eaeeacdf4e237",
          "record_id": "ft06",
          "method": "full"
        },
        {
          "path": "reproduction/results/external_discrete_run01/frozen_cases.json",
          "sha256": "095fef49c96a559d91217736c46646effbe90f7939ead37082e80df61280ddc3",
          "record_id": "ft06"
        }
      ],
      "horizon": 152.0,
      "reduction_percent": 25.657894736842106,
      "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1040 492\" role=\"img\" aria-labelledby=\"replay-svg-title replay-svg-desc\"><title id=\"replay-svg-title\">Resource-ordering comparison</title><desc id=\"replay-svg-desc\">Replay of archived accepted schedules. Time is symbolic. Purple joint tasks occupy both L and R. Rectangles show exact stored start and finish times.</desc><style>text{font-family:Arial,sans-serif;fill:#26384d}.label{font-size:13px}.tiny{font-size:11px}.clock{stroke:#d76c40;stroke-width:2}.task-progress{pointer-events:none}.node-id{font-weight:700;font-size:14px}.node-action{font-size:11px}.graph-edge{fill:none;stroke:#99aac0;stroke-width:1.4}</style><defs><marker id=\"replay-arrow\" markerWidth=\"7\" markerHeight=\"7\" refX=\"6\" refY=\"3.5\" orient=\"auto\"><path d=\"M0,0 L7,3.5 L0,7\" fill=\"#99aac0\"/></marker></defs><rect width=\"1040\" height=\"492\" rx=\"8\" fill=\"white\"/><text x=\"68\" y=\"51\" font-size=\"15\" font-weight=\"700\">Field matching + shared compression</text><text x=\"992\" y=\"51\" text-anchor=\"end\" class=\"label\">Makespan 152</text><text x=\"35\" y=\"102\" font-size=\"16\" font-weight=\"700\">L</text><rect x=\"68\" y=\"74\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><text x=\"35\" y=\"150\" font-size=\"16\" font-weight=\"700\">R</text><rect x=\"68\" y=\"122\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><line x1=\"68.00000\" x2=\"68.00000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"68.00000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">0</text><line x1=\"252.80000\" x2=\"252.80000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"252.80000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">30.4</text><line x1=\"437.60000\" x2=\"437.60000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"437.60000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">60.8</text><line x1=\"622.40000\" x2=\"622.40000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"622.40000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">91.2</text><line x1=\"807.20000\" x2=\"807.20000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"807.20000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">121.6</text><line x1=\"992.00000\" x2=\"992.00000\" y1=\"74\" y2=\"164\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"992.00000\" y=\"186\" text-anchor=\"middle\" class=\"tiny\">152</text><g data-task=\"j00_o00\" data-plan=\"0\"><title>j00_o00 · process · job0 | [0, 1) | units: left | resources: machine2</title><rect x=\"68.00000\" y=\"74\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o00\" data-plan=\"0\" x=\"68.00000\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o01\" data-plan=\"0\"><title>j00_o01 · process · job0 | [1, 4) | units: left | resources: machine0</title><rect x=\"74.07895\" y=\"74\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o01\" data-plan=\"0\" x=\"74.07895\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o02\" data-plan=\"0\"><title>j00_o02 · process · job0 | [4, 10) | units: left | resources: machine1</title><rect x=\"92.31579\" y=\"74\" width=\"36.47368\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o02\" data-plan=\"0\" x=\"92.31579\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o03\" data-plan=\"0\"><title>j00_o03 · process · job0 | [10, 17) | units: left | resources: machine3</title><rect x=\"128.78947\" y=\"74\" width=\"42.55263\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o03\" data-plan=\"0\" x=\"128.78947\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"150.06579\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J0.3</text></g><g data-task=\"j00_o04\" data-plan=\"0\"><title>j00_o04 · process · job0 | [17, 20) | units: left | resources: machine5</title><rect x=\"171.34211\" y=\"74\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o04\" data-plan=\"0\" x=\"171.34211\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o05\" data-plan=\"0\"><title>j00_o05 · process · job0 | [20, 26) | units: left | resources: machine4</title><rect x=\"189.57895\" y=\"74\" width=\"36.47368\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o05\" data-plan=\"0\" x=\"189.57895\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o00\" data-plan=\"0\"><title>j01_o00 · process · job1 | [10, 18) | units: right | resources: machine1</title><rect x=\"128.78947\" y=\"122\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o00\" data-plan=\"0\" x=\"128.78947\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"153.10526\" y=\"148.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.0</text></g><g data-task=\"j01_o01\" data-plan=\"0\"><title>j01_o01 · process · job1 | [18, 23) | units: right | resources: machine2</title><rect x=\"177.42105\" y=\"122\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o01\" data-plan=\"0\" x=\"177.42105\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o02\" data-plan=\"0\"><title>j01_o02 · process · job1 | [26, 36) | units: left | resources: machine4</title><rect x=\"226.05263\" y=\"74\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o02\" data-plan=\"0\" x=\"226.05263\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"256.44737\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.2</text></g><g data-task=\"j01_o03\" data-plan=\"0\"><title>j01_o03 · process · job1 | [36, 46) | units: left | resources: machine5</title><rect x=\"286.84211\" y=\"74\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o03\" data-plan=\"0\" x=\"286.84211\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"317.23684\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.3</text></g><g data-task=\"j01_o04\" data-plan=\"0\"><title>j01_o04 · process · job1 | [46, 56) | units: left | resources: machine0</title><rect x=\"347.63158\" y=\"74\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o04\" data-plan=\"0\" x=\"347.63158\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"378.02632\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.4</text></g><g data-task=\"j01_o05\" data-plan=\"0\"><title>j01_o05 · process · job1 | [56, 60) | units: left | resources: machine3</title><rect x=\"408.42105\" y=\"74\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o05\" data-plan=\"0\" x=\"408.42105\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o00\" data-plan=\"0\"><title>j02_o00 · process · job2 | [23, 28) | units: right | resources: machine2</title><rect x=\"207.81579\" y=\"122\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o00\" data-plan=\"0\" x=\"207.81579\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o01\" data-plan=\"0\"><title>j02_o01 · process · job2 | [60, 64) | units: left | resources: machine3</title><rect x=\"432.73684\" y=\"74\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o01\" data-plan=\"0\" x=\"432.73684\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o02\" data-plan=\"0\"><title>j02_o02 · process · job2 | [64, 72) | units: left | resources: machine5</title><rect x=\"457.05263\" y=\"74\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o02\" data-plan=\"0\" x=\"457.05263\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"481.36842\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.2</text></g><g data-task=\"j02_o03\" data-plan=\"0\"><title>j02_o03 · process · job2 | [72, 81) | units: left | resources: machine0</title><rect x=\"505.68421\" y=\"74\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o03\" data-plan=\"0\" x=\"505.68421\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"533.03947\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.3</text></g><g data-task=\"j02_o04\" data-plan=\"0\"><title>j02_o04 · process · job2 | [81, 82) | units: left | resources: machine1</title><rect x=\"560.39474\" y=\"74\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o04\" data-plan=\"0\" x=\"560.39474\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o05\" data-plan=\"0\"><title>j02_o05 · process · job2 | [82, 89) | units: left | resources: machine4</title><rect x=\"566.47368\" y=\"74\" width=\"42.55263\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o05\" data-plan=\"0\" x=\"566.47368\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"587.75000\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.5</text></g><g data-task=\"j03_o00\" data-plan=\"0\"><title>j03_o00 · process · job3 | [82, 87) | units: right | resources: machine1</title><rect x=\"566.47368\" y=\"122\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o00\" data-plan=\"0\" x=\"566.47368\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o01\" data-plan=\"0\"><title>j03_o01 · process · job3 | [87, 92) | units: right | resources: machine0</title><rect x=\"596.86842\" y=\"122\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o01\" data-plan=\"0\" x=\"596.86842\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o02\" data-plan=\"0\"><title>j03_o02 · process · job3 | [92, 97) | units: left | resources: machine2</title><rect x=\"627.26316\" y=\"74\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o02\" data-plan=\"0\" x=\"627.26316\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o03\" data-plan=\"0\"><title>j03_o03 · process · job3 | [97, 100) | units: left | resources: machine3</title><rect x=\"657.65789\" y=\"74\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o03\" data-plan=\"0\" x=\"657.65789\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o04\" data-plan=\"0\"><title>j03_o04 · process · job3 | [100, 108) | units: left | resources: machine4</title><rect x=\"675.89474\" y=\"74\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o04\" data-plan=\"0\" x=\"675.89474\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"700.21053\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J3.4</text></g><g data-task=\"j03_o05\" data-plan=\"0\"><title>j03_o05 · process · job3 | [108, 117) | units: left | resources: machine5</title><rect x=\"724.52632\" y=\"74\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o05\" data-plan=\"0\" x=\"724.52632\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"751.88158\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J3.5</text></g><g data-task=\"j04_o00\" data-plan=\"0\"><title>j04_o00 · process · job4 | [97, 106) | units: right | resources: machine2</title><rect x=\"657.65789\" y=\"122\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o00\" data-plan=\"0\" x=\"657.65789\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"685.01316\" y=\"148.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J4.0</text></g><g data-task=\"j04_o01\" data-plan=\"0\"><title>j04_o01 · process · job4 | [106, 109) | units: right | resources: machine1</title><rect x=\"712.36842\" y=\"122\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o01\" data-plan=\"0\" x=\"712.36842\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o02\" data-plan=\"0\"><title>j04_o02 · process · job4 | [109, 114) | units: right | resources: machine4</title><rect x=\"730.60526\" y=\"122\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o02\" data-plan=\"0\" x=\"730.60526\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o03\" data-plan=\"0\"><title>j04_o03 · process · job4 | [117, 121) | units: left | resources: machine5</title><rect x=\"779.23684\" y=\"74\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o03\" data-plan=\"0\" x=\"779.23684\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o04\" data-plan=\"0\"><title>j04_o04 · process · job4 | [121, 124) | units: left | resources: machine0</title><rect x=\"803.55263\" y=\"74\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o04\" data-plan=\"0\" x=\"803.55263\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o05\" data-plan=\"0\"><title>j04_o05 · process · job4 | [124, 125) | units: left | resources: machine3</title><rect x=\"821.78947\" y=\"74\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o05\" data-plan=\"0\" x=\"821.78947\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o00\" data-plan=\"0\"><title>j05_o00 · process · job5 | [114, 117) | units: right | resources: machine1</title><rect x=\"761.00000\" y=\"122\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o00\" data-plan=\"0\" x=\"761.00000\" y=\"122\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o01\" data-plan=\"0\"><title>j05_o01 · process · job5 | [125, 128) | units: left | resources: machine3</title><rect x=\"827.86842\" y=\"74\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o01\" data-plan=\"0\" x=\"827.86842\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o02\" data-plan=\"0\"><title>j05_o02 · process · job5 | [128, 137) | units: left | resources: machine5</title><rect x=\"846.10526\" y=\"74\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o02\" data-plan=\"0\" x=\"846.10526\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"873.46053\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J5.2</text></g><g data-task=\"j05_o03\" data-plan=\"0\"><title>j05_o03 · process · job5 | [137, 147) | units: left | resources: machine0</title><rect x=\"900.81579\" y=\"74\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o03\" data-plan=\"0\" x=\"900.81579\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"931.21053\" y=\"100.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J5.3</text></g><g data-task=\"j05_o04\" data-plan=\"0\"><title>j05_o04 · process · job5 | [147, 151) | units: left | resources: machine4</title><rect x=\"961.60526\" y=\"74\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o04\" data-plan=\"0\" x=\"961.60526\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o05\" data-plan=\"0\"><title>j05_o05 · process · job5 | [151, 152) | units: left | resources: machine2</title><rect x=\"985.92105\" y=\"74\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o05\" data-plan=\"0\" x=\"985.92105\" y=\"74\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><line class=\"clock\" data-clock=\"0\" x1=\"68\" x2=\"68\" y1=\"69\" y2=\"168\"></line><text x=\"68\" y=\"251\" font-size=\"15\" font-weight=\"700\">Full method</text><text x=\"992\" y=\"251\" text-anchor=\"end\" class=\"label\">Makespan 113</text><text x=\"35\" y=\"302\" font-size=\"16\" font-weight=\"700\">L</text><rect x=\"68\" y=\"274\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><text x=\"35\" y=\"350\" font-size=\"16\" font-weight=\"700\">R</text><rect x=\"68\" y=\"322\" width=\"924\" height=\"42\" fill=\"#f4f7fa\" stroke=\"#dce3eb\"/><line x1=\"68.00000\" x2=\"68.00000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"68.00000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">0</text><line x1=\"252.80000\" x2=\"252.80000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"252.80000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">30.4</text><line x1=\"437.60000\" x2=\"437.60000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"437.60000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">60.8</text><line x1=\"622.40000\" x2=\"622.40000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"622.40000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">91.2</text><line x1=\"807.20000\" x2=\"807.20000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"807.20000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">121.6</text><line x1=\"992.00000\" x2=\"992.00000\" y1=\"274\" y2=\"364\" stroke=\"#dce3eb\" stroke-dasharray=\"2 4\"/><text x=\"992.00000\" y=\"386\" text-anchor=\"middle\" class=\"tiny\">152</text><g data-task=\"j00_o00\" data-plan=\"1\"><title>j00_o00 · process · job0 | [0, 1) | units: left | resources: machine2</title><rect x=\"68.00000\" y=\"274\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o00\" data-plan=\"1\" x=\"68.00000\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o01\" data-plan=\"1\"><title>j00_o01 · process · job0 | [1, 4) | units: left | resources: machine0</title><rect x=\"74.07895\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o01\" data-plan=\"1\" x=\"74.07895\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o00\" data-plan=\"1\"><title>j01_o00 · process · job1 | [0, 8) | units: right | resources: machine1</title><rect x=\"68.00000\" y=\"322\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o00\" data-plan=\"1\" x=\"68.00000\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"92.31579\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.0</text></g><g data-task=\"j02_o00\" data-plan=\"1\"><title>j02_o00 · process · job2 | [4, 9) | units: left | resources: machine2</title><rect x=\"92.31579\" y=\"274\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o00\" data-plan=\"1\" x=\"92.31579\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o01\" data-plan=\"1\"><title>j01_o01 · process · job1 | [9, 14) | units: left | resources: machine2</title><rect x=\"122.71053\" y=\"274\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o01\" data-plan=\"1\" x=\"122.71053\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o02\" data-plan=\"1\"><title>j01_o02 · process · job1 | [14, 24) | units: left | resources: machine4</title><rect x=\"153.10526\" y=\"274\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o02\" data-plan=\"1\" x=\"153.10526\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"183.50000\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.2</text></g><g data-task=\"j02_o01\" data-plan=\"1\"><title>j02_o01 · process · job2 | [9, 13) | units: right | resources: machine3</title><rect x=\"122.71053\" y=\"322\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o01\" data-plan=\"1\" x=\"122.71053\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o02\" data-plan=\"1\"><title>j02_o02 · process · job2 | [13, 21) | units: right | resources: machine5</title><rect x=\"147.02632\" y=\"322\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o02\" data-plan=\"1\" x=\"147.02632\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"171.34211\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.2</text></g><g data-task=\"j01_o03\" data-plan=\"1\"><title>j01_o03 · process · job1 | [24, 34) | units: left | resources: machine5</title><rect x=\"213.89474\" y=\"274\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o03\" data-plan=\"1\" x=\"213.89474\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"244.28947\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.3</text></g><g data-task=\"j03_o00\" data-plan=\"1\"><title>j03_o00 · process · job3 | [21, 26) | units: right | resources: machine1</title><rect x=\"195.65789\" y=\"322\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o00\" data-plan=\"1\" x=\"195.65789\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o02\" data-plan=\"1\"><title>j00_o02 · process · job0 | [26, 32) | units: right | resources: machine1</title><rect x=\"226.05263\" y=\"322\" width=\"36.47368\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o02\" data-plan=\"1\" x=\"226.05263\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o01\" data-plan=\"1\"><title>j03_o01 · process · job3 | [32, 37) | units: right | resources: machine0</title><rect x=\"262.52632\" y=\"322\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o01\" data-plan=\"1\" x=\"262.52632\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o03\" data-plan=\"1\"><title>j02_o03 · process · job2 | [37, 46) | units: left | resources: machine0</title><rect x=\"292.92105\" y=\"274\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o03\" data-plan=\"1\" x=\"292.92105\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"320.27632\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.3</text></g><g data-task=\"j01_o04\" data-plan=\"1\"><title>j01_o04 · process · job1 | [46, 56) | units: left | resources: machine0</title><rect x=\"347.63158\" y=\"274\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o04\" data-plan=\"1\" x=\"347.63158\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"378.02632\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J1.4</text></g><g data-task=\"j03_o02\" data-plan=\"1\"><title>j03_o02 · process · job3 | [37, 42) | units: right | resources: machine2</title><rect x=\"292.92105\" y=\"322\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o02\" data-plan=\"1\" x=\"292.92105\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o00\" data-plan=\"1\"><title>j04_o00 · process · job4 | [42, 51) | units: right | resources: machine2</title><rect x=\"323.31579\" y=\"322\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o00\" data-plan=\"1\" x=\"323.31579\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"350.67105\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J4.0</text></g><g data-task=\"j05_o00\" data-plan=\"1\"><title>j05_o00 · process · job5 | [51, 54) | units: right | resources: machine1</title><rect x=\"378.02632\" y=\"322\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o00\" data-plan=\"1\" x=\"378.02632\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o04\" data-plan=\"1\"><title>j02_o04 · process · job2 | [54, 55) | units: right | resources: machine1</title><rect x=\"396.26316\" y=\"322\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o04\" data-plan=\"1\" x=\"396.26316\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j02_o05\" data-plan=\"1\"><title>j02_o05 · process · job2 | [55, 62) | units: right | resources: machine4</title><rect x=\"402.34211\" y=\"322\" width=\"42.55263\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j02_o05\" data-plan=\"1\" x=\"402.34211\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"423.61842\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J2.5</text></g><g data-task=\"j04_o01\" data-plan=\"1\"><title>j04_o01 · process · job4 | [56, 59) | units: left | resources: machine1</title><rect x=\"408.42105\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o01\" data-plan=\"1\" x=\"408.42105\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o01\" data-plan=\"1\"><title>j05_o01 · process · job5 | [59, 62) | units: left | resources: machine3</title><rect x=\"426.65789\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o01\" data-plan=\"1\" x=\"426.65789\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o03\" data-plan=\"1\"><title>j00_o03 · process · job0 | [62, 69) | units: left | resources: machine3</title><rect x=\"444.89474\" y=\"274\" width=\"42.55263\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o03\" data-plan=\"1\" x=\"444.89474\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"466.17105\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J0.3</text></g><g data-task=\"j03_o03\" data-plan=\"1\"><title>j03_o03 · process · job3 | [69, 72) | units: left | resources: machine3</title><rect x=\"487.44737\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o03\" data-plan=\"1\" x=\"487.44737\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j01_o05\" data-plan=\"1\"><title>j01_o05 · process · job1 | [72, 76) | units: left | resources: machine3</title><rect x=\"505.68421\" y=\"274\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j01_o05\" data-plan=\"1\" x=\"505.68421\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o04\" data-plan=\"1\"><title>j03_o04 · process · job3 | [72, 80) | units: right | resources: machine4</title><rect x=\"505.68421\" y=\"322\" width=\"48.63158\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o04\" data-plan=\"1\" x=\"505.68421\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"530.00000\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J3.4</text></g><g data-task=\"j04_o02\" data-plan=\"1\"><title>j04_o02 · process · job4 | [80, 85) | units: left | resources: machine4</title><rect x=\"554.31579\" y=\"274\" width=\"30.39474\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o02\" data-plan=\"1\" x=\"554.31579\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o02\" data-plan=\"1\"><title>j05_o02 · process · job5 | [80, 89) | units: right | resources: machine5</title><rect x=\"554.31579\" y=\"322\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o02\" data-plan=\"1\" x=\"554.31579\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"581.67105\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J5.2</text></g><g data-task=\"j00_o04\" data-plan=\"1\"><title>j00_o04 · process · job0 | [89, 92) | units: left | resources: machine5</title><rect x=\"609.02632\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o04\" data-plan=\"1\" x=\"609.02632\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j00_o05\" data-plan=\"1\"><title>j00_o05 · process · job0 | [92, 98) | units: left | resources: machine4</title><rect x=\"627.26316\" y=\"274\" width=\"36.47368\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j00_o05\" data-plan=\"1\" x=\"627.26316\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o03\" data-plan=\"1\"><title>j04_o03 · process · job4 | [92, 96) | units: right | resources: machine5</title><rect x=\"627.26316\" y=\"322\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o03\" data-plan=\"1\" x=\"627.26316\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j03_o05\" data-plan=\"1\"><title>j03_o05 · process · job3 | [96, 105) | units: right | resources: machine5</title><rect x=\"651.57895\" y=\"322\" width=\"54.71053\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j03_o05\" data-plan=\"1\" x=\"651.57895\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect><text x=\"678.93421\" y=\"348.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J3.5</text></g><g data-task=\"j05_o03\" data-plan=\"1\"><title>j05_o03 · process · job5 | [98, 108) | units: left | resources: machine0</title><rect x=\"663.73684\" y=\"274\" width=\"60.78947\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o03\" data-plan=\"1\" x=\"663.73684\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect><text x=\"694.13158\" y=\"300.0\" text-anchor=\"middle\" font-size=\"11\" font-weight=\"600\">J5.3</text></g><g data-task=\"j04_o04\" data-plan=\"1\"><title>j04_o04 · process · job4 | [108, 111) | units: left | resources: machine0</title><rect x=\"724.52632\" y=\"274\" width=\"18.23684\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o04\" data-plan=\"1\" x=\"724.52632\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j04_o05\" data-plan=\"1\"><title>j04_o05 · process · job4 | [111, 112) | units: left | resources: machine3</title><rect x=\"742.76316\" y=\"274\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j04_o05\" data-plan=\"1\" x=\"742.76316\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o04\" data-plan=\"1\"><title>j05_o04 · process · job5 | [108, 112) | units: right | resources: machine4</title><rect x=\"724.52632\" y=\"322\" width=\"24.31579\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".13\" stroke=\"#388b82\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o04\" data-plan=\"1\" x=\"724.52632\" y=\"322\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#388b82\" fill-opacity=\".72\"></rect></g><g data-task=\"j05_o05\" data-plan=\"1\"><title>j05_o05 · process · job5 | [112, 113) | units: left | resources: machine2</title><rect x=\"748.84211\" y=\"274\" width=\"6.07895\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".13\" stroke=\"#376eaa\" stroke-width=\".8\"/><rect class=\"task-progress\" data-progress=\"j05_o05\" data-plan=\"1\" x=\"748.84211\" y=\"274\" width=\"0\" height=\"42\" rx=\"3\" fill=\"#376eaa\" fill-opacity=\".72\"></rect></g><line class=\"clock\" data-clock=\"1\" x1=\"68\" x2=\"68\" y1=\"269\" y2=\"368\"></line><text x=\"68\" y=\"437\" class=\"label\">Same input · same compression · common time axis</text><text x=\"992\" y=\"437\" text-anchor=\"end\" class=\"label\">25.66% shorter for the full method on this instance</text><text x=\"68\" y=\"479\" class=\"tiny\">Time: symbolic input units · visual playback speed is arbitrary · archived schedules, not hardware footage</text></svg>"
    }
  ]
};
