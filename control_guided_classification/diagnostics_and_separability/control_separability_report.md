# H2B_Bound versus MCM2_Bound separability report

Final interpretation: **partly**.

Balanced cross-validated balanced accuracy: 0.623.

Repeated downsample median balanced accuracy: 0.830.

Permutation-test p-value: 0.0196.

Top separating features:

- intensity_mean: Cohen's d=-1.29, MCM2-H2B mean difference=-5.74e+03
- Rg: Cohen's d=0.29, MCM2-H2B mean difference=7.18
- step_size_p95: Cohen's d=0.27, MCM2-H2B mean difference=22.7
- step_size_mean: Cohen's d=0.24, MCM2-H2B mean difference=4.4
- path_length: Cohen's d=0.22, MCM2-H2B mean difference=81
- net_displacement: Cohen's d=-0.12, MCM2-H2B mean difference=-0.0623
- intensity_std: Cohen's d=0.12, MCM2-H2B mean difference=736
- step_size_median: Cohen's d=-0.03, MCM2-H2B mean difference=-0.24

Target tracks were projected onto the H2B_Bound/MCM2_Bound feature space for similarity only; they were not used to train the bound-control classifier.

Cautious interpretation: this is a motion-pattern diagnostic, not proof of physical condensate or paraspeckle localization.
