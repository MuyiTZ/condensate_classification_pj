# Old-vs-new target crosstab

This compares old `condensate_evaluation` motion-pattern classes with the current final control-guided classifier when exact track keys match.

## Old trapping_like destinations

| new_destination | n_old_trapping_like_tracks |
| --- | --- |
| not_in_current_final_classifier | 1411 |
| chromatin_bound_like | 754 |
| ambiguous | 126 |
| mcm_bound_like | 41 |
| free_like | 5 |

Tracks marked `not_in_current_final_classifier` are from datasets that have per-dataset condensate_evaluation output but were not included in the current final control-guided table.