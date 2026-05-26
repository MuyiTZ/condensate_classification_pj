# Control-Guided Condensate Classification Run Summary

Status: FULL ANALYSIS PASS
Run date: 
2026-05-26T00:09:14.3419887-04:00

## What Was Done

- Read the project control specification.
- Created the required control_guided_classification folder structure.
- Initialized Git inside D:\Tianzi\condensate_classification_pj only.
- Added .gitignore and Git recovery notes.
- Added the new SMol-FIESTA module control_guided_condensate_classification.py.
- Ran dry-run inventory first.
- Ran the full analysis using smol_env through the user-provided conda.bat path.
- Generated feature matrix, control model predictions, final classifications, summaries, model artifact, logs, and easy-interpretation files.

## Inputs Used

- Project folder: D:\Tianzi\condensate_classification_pj
- SMol-FIESTA module folder: C:\Users\rangq\Desktop\SMT_codes\Analysis_PIPELINE\workshopV2\Smol-FIESTA\SMol_FIESTA
- MCM2 bound control: D:\Tianzi\condensate_classification_pj\MCM2\HCT116-1125-CT\CSV\SF_10ms_condensate_may22_\single-behaviour-track-MCM2-bound.csv

## Dry-Run Results

- TDP43: FOUND
- NONO: FOUND
- NLS: FOUND
- H2B: FOUND (folder is named H2b, canonicalized to H2B)
- MCM2: FOUND
- MCM2_Bound / single-behaviour-track-MCM2-bound.csv: FOUND

## Model And Controls

- NLS was used as the free-like control.
- H2B was used as the chromatin-bound control.
- MCM2_Bound was used as the MCM-bound control.
- TDP43 and NONO were not used for model fitting.
- Random seed: 42

## Final Track Counts

- Total final rows: 18,671
- chromatin_bound_like: 14,445
- free_like: 2,660
- ambiguous: 1,122
- mcm_bound_like: 444
- mixed: 0
- slow_diffusive: 0
- target_specific_trapping_like: 0

## Acceptance Checks

- feature_matrix_tracks.csv exists: PASS
- final_control_guided_track_classification.csv exists: PASS
- RUN_SUMMARY.md exists: PASS
- log file exists: PASS
- MCM2_Bound used as mcm_bound_control: PASS
- TDP43/NONO used for model fitting: NO
- invalid final classes: 0
- empty classification_reason rows: 0
- generated files are inside control_guided_classification: PASS
- existing SMol-FIESTA files modified: NO; only a new module was added.

## Warnings And Assumptions

- scikit-learn reported a FutureWarning for LogisticRegression multi_class. This does not stop the run.
- numpy reported repeated Mean of empty slice warnings, likely from unavailable/missing feature columns in some groups.
- trapping_score_controls_vs_targets plot was skipped because trapping_score was unavailable as a usable feature.
- One file is larger than 50 MB and below 100 MB: H2b/HAP1-0117-CT/CSV/SF_10ms_condensate_may25_/Intermediates/tracks.csv, 71,745,112 bytes.
- No files larger than 100 MB were found.

## Key Outputs

- feature_matrix_tracks.csv
- final_control_guided_track_classification.csv
- control_model_predictions.csv
- distance_to_controls.csv
- anomaly_model_scores.csv
- summary_by_dataset.csv
- summary_by_protein.csv
- easy_interpretation/simplified_results_table.csv
- trained_models/control_models.joblib
- control_guided_condensate_classification.py copied for provenance

## Git Status Before Final Commit

```text
 M control_guided_classification/RUN_SUMMARY.md
 M control_guided_classification/input_file_inventory.csv
?? control_guided_classification/anomaly_model_scores.csv
?? control_guided_classification/control_centroids.csv
?? control_guided_classification/control_classifier_confusion_matrix.csv
?? control_guided_classification/control_classifier_metrics.csv
?? control_guided_classification/control_guided_condensate_classification.py
?? control_guided_classification/control_model_predictions.csv
?? control_guided_classification/distance_to_controls.csv
?? control_guided_classification/easy_interpretation/
?? control_guided_classification/feature_dictionary.csv
?? control_guided_classification/feature_importance_random_forest.csv
?? control_guided_classification/feature_matrix_tracks.csv
?? control_guided_classification/feature_missingness_report.csv
?? control_guided_classification/final_control_guided_track_classification.csv
?? control_guided_classification/logistic_regression_coefficients.csv
?? control_guided_classification/logs/control_guided_classification_20260526_000535.log
?? control_guided_classification/logs/control_guided_classification_20260526_000745.log
?? control_guided_classification/plots/
?? control_guided_classification/replicate_level_class_fractions.csv
?? control_guided_classification/standardized_inputs/
?? control_guided_classification/summary_by_condition.csv
?? control_guided_classification/summary_by_dataset.csv
?? control_guided_classification/summary_by_protein.csv
?? control_guided_classification/summary_by_replicate.csv
?? control_guided_classification/summary_frames_by_dataset.csv
?? control_guided_classification/track_count_by_dataset.csv
?? control_guided_classification/trained_models/
```

## Recent Git Log Before Final Commit

```text
2275c02 Record approved dry-run and smol_env launch blocker
0fe910a Update dry-run audit log
d08a13f Add dry-run summary for condensate classification
f386e4b Record dry-run inventory for condensate classification
9e81021 Initialize condensate classification project repository
```

## GitHub Remote Before Push

```text
No remote configured yet.
```

## Rerun Commands

```bash
C:\Users\rangq\anaconda3\condabin\conda.bat run -n smol_env python C:\Users\rangq\Desktop\SMT_codes\Analysis_PIPELINE\workshopV2\Smol-FIESTA\SMol_FIESTA\control_guided_condensate_classification.py --project-folder "D:\Tianzi\condensate_classification_pj" --dry-run
C:\Users\rangq\anaconda3\condabin\conda.bat run -n smol_env python C:\Users\rangq\Desktop\SMT_codes\Analysis_PIPELINE\workshopV2\Smol-FIESTA\SMol_FIESTA\control_guided_condensate_classification.py --project-folder "D:\Tianzi\condensate_classification_pj"
```

## Git Status After Final Analysis Commit

```text
```

## Recent Git Log After Final Analysis Commit

```text
0039073 Run control-guided condensate classification analysis
2275c02 Record approved dry-run and smol_env launch blocker
0fe910a Update dry-run audit log
d08a13f Add dry-run summary for condensate classification
f386e4b Record dry-run inventory for condensate classification
9e81021 Initialize condensate classification project repository
```

## GitHub Remote After Final Analysis Commit

```text
No remote configured yet.
```
