window.ATG_SIMULATION = {
  "engine": "MuJoCo 3.3.3",
  "evaluation": "frozen_v2",
  "trials": 30,
  "independent_recheck": 30,
  "cases": [
    {
      "case": "parallel",
      "title": "Parallel sorting",
      "full": {
        "successes": 5,
        "n": 5,
        "makespan_s": 12.0,
        "max_goal_error_mm": 7.48318111203043,
        "mean_task_max_error_mm": 7.325935204137208,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "serial": {
        "successes": 5,
        "n": 5,
        "makespan_s": 24.0,
        "max_goal_error_mm": 13.090636265564967,
        "mean_task_max_error_mm": 12.900143633640019,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "makespan_reduction_percent": 50.0
    },
    {
      "case": "shared",
      "title": "Shared inspection station",
      "full": {
        "successes": 5,
        "n": 5,
        "makespan_s": 28.0,
        "max_goal_error_mm": 16.80387113045287,
        "mean_task_max_error_mm": 15.776130368364138,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "serial": {
        "successes": 5,
        "n": 5,
        "makespan_s": 40.0,
        "max_goal_error_mm": 17.1759530804708,
        "mean_task_max_error_mm": 16.319121531793755,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "makespan_reduction_percent": 30.0
    },
    {
      "case": "cooperative",
      "title": "Cooperative tray transfer",
      "full": {
        "successes": 5,
        "n": 5,
        "makespan_s": 17.0,
        "max_goal_error_mm": 1.0491089570669234,
        "mean_task_max_error_mm": 1.0411783061146762,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "serial": {
        "successes": 5,
        "n": 5,
        "makespan_s": 22.0,
        "max_goal_error_mm": 1.0574322134059697,
        "mean_task_max_error_mm": 1.0444323673292526,
        "station_conflicts": 0,
        "interarm_penetration_contacts": 0
      },
      "makespan_reduction_percent": 22.727272727272727
    }
  ],
  "videos": [
    {
      "file": "assets/videos/parallel_full.mp4",
      "case": "parallel",
      "seed": 0,
      "mode": "full",
      "sha256": "783d42c0db44e9b7f83137429660333bfcf6af2cae3be76d9c0075f0cc305657",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    },
    {
      "file": "assets/videos/parallel_serial.mp4",
      "case": "parallel",
      "seed": 0,
      "mode": "serial",
      "sha256": "a3860237be83167a597198f90ceb9302a309eb8bdd64a7f6926653345406f91a",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    },
    {
      "file": "assets/videos/shared_full.mp4",
      "case": "shared",
      "seed": 0,
      "mode": "full",
      "sha256": "82d53be63b2602d9723d5c3d004745ba829e564298e63d1733c7f8690165708a",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    },
    {
      "file": "assets/videos/shared_serial.mp4",
      "case": "shared",
      "seed": 0,
      "mode": "serial",
      "sha256": "09fe316bb3318fe385c92647c3a1e0ae4c3aec665bb7fd9097abc2c8f693d702",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    },
    {
      "file": "assets/videos/cooperative_full.mp4",
      "case": "cooperative",
      "seed": 0,
      "mode": "full",
      "sha256": "66893e3a4077b7f7681ac98486601876a9b8b1855bae89a09f6decea63708314",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    },
    {
      "file": "assets/videos/cooperative_serial.mp4",
      "case": "cooperative",
      "seed": 0,
      "mode": "serial",
      "sha256": "66d329d638be8296aeddec086b09f860f83664f86a504aa5be38cc1efd74624f",
      "fps": 25,
      "resolution": [
        1280,
        720
      ],
      "selection": "seed 0 fixed in protocol before evaluation"
    }
  ],
  "scope": "Constructed tasks and fixed primitives; simulation time in seconds, not hardware measurements; not a comparison between relation-repair heuristics."
};
