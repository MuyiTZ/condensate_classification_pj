# TDP43 condition-level diagnostics

Old trapping-like fractions come from per-dataset condensate_evaluation summaries. New control-guided fractions and distances are only present for datasets already included in the current final classifier; missing values should not be overinterpreted.

## Replicate-level
| genotype | treatment | replicate | n_old_tracks | old_trapping_like_fraction | old_mixed_fraction | n_final_tracks | ambiguous_fraction | chromatin_bound_like_fraction | free_like_fraction | mean_distance_to_H2B | mean_distance_to_MCM2_Bound | near_miss_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12D | ARS | 12D-0416-ARS | 1038 | 0.21579961464354527 | 0.7842003853564548 |  |  |  |  |  |  |  |
| 12D | ARS | 12D-0423-ARS | 260 | 0.2692307692307692 | 0.7307692307692307 |  |  |  |  |  |  |  |
| 12D | ARS | 12D-0515-ARS | 377 | 0.2572944297082228 | 0.7427055702917772 |  |  |  |  |  |  |  |
| 12D | CT | 12D-0416-CT | 225 | 0.22666666666666666 | 0.7733333333333333 |  |  |  |  |  |  |  |
| 12D | CT | 12D-0423-CT | 136 | 0.20588235294117646 | 0.7941176470588235 |  |  |  |  |  |  |  |
| 12D | CT | 12D-0502-CT | 61 | 0.32786885245901637 | 0.6721311475409836 |  |  |  |  |  |  |  |
| WT | ACTD | WT-1211-ACTD | 199 | 0.33668341708542715 | 0.6633165829145728 |  |  |  |  |  |  |  |
| WT | ARS | WT-0416-ARS | 1492 | 0.26005361930294907 | 0.739946380697051 |  |  |  |  |  |  |  |
| WT | ARS | WT-0423-ARS | 830 | 0.27710843373493976 | 0.7216867469879518 |  |  |  |  |  |  |  |
| WT | ARS | WT-0515-ARS | 490 | 0.2755102040816326 | 0.7244897959183674 |  |  |  |  |  |  |  |
| WT | CT | WT-0416-CT | 667 | 0.27136431784107945 | 0.7286356821589205 | 2965.0 | 0.1258010118043845 | 0.5956155143338955 | 0.25531197301854974 | 3.0123996925667855 | 3.984483846137079 |  |
| WT | CT | WT-0423-CT | 246 | 0.18699186991869918 | 0.8130081300813008 |  |  |  |  |  |  |  |
| WT | CT | WT-0515-CT | 194 | 0.28350515463917525 | 0.7164948453608248 |  |  |  |  |  |  |  |

## Genotype-treatment averages
| genotype | treatment | completed_old_repeats | mean_old_trapping_like_fraction | sd_old_trapping_like_fraction | mean_ambiguous_fraction | mean_chromatin_bound_like_fraction | mean_free_like_fraction | mean_near_miss_fraction | mean_distance_to_H2B | mean_distance_to_MCM2_Bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12D | ARS | 3 | 0.24744160452751243 | 0.02804515453981642 |  |  |  |  |  |  |
| 12D | CT | 3 | 0.2534726240222865 | 0.06526175011802451 |  |  |  |  |  |  |
| WT | ACTD | 1 | 0.33668341708542715 |  |  |  |  |  |  |  |
| WT | ARS | 3 | 0.27089075237317384 | 0.009419191812066277 |  |  |  |  |  |  |
| WT | CT | 3 | 0.24728711413298463 | 0.05256888181885497 | 0.1258010118043845 | 0.5956155143338955 | 0.25531197301854974 |  | 3.0123996925667855 | 3.984483846137079 |