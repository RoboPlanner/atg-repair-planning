# Development records

Pilot batches used seeds -1 and -2; they are excluded from the frozen evaluation. The first shared-station pilot dropped held objects. Friction and contact-solver settings were revised before final evaluation.

The first 30-run evaluation completed the tasks but failed an independent logging-alignment check: `mj_step` had integrated `qpos`, while derived object poses were still from the preceding 2 ms step. The logger was corrected with `mj_forward`, all 30 conditions were rerun, and only `frozen_v2` is reported as the final experiment. Original summaries and the failing check are retained here; complete development files remain in the local research workspace.
