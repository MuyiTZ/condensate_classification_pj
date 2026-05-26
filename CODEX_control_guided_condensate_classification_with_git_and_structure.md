# Codex Task Specification: Control-Guided Condensate Track Classification

## 0. Purpose

This markdown file gives Codex the complete instructions to implement **Step 3, Step 4, and Step 5** of the condensate classification project using the existing outputs from SMol-FIESTA and the manually prepared MCM2 bound-track file.

The biological goal is **not** to claim that every trapped track is inside a condensate. The goal is to identify target-protein tracks, especially **TDP43** and **NONO**, whose motion is:

1. not explained by freely diffusive nuclear motion, using **NLS-HaloTag** as the free-like control,
2. not explained by ordinary chromatin-bound motion, using **H2B** as the chromatin-bound control,
3. not explained by replication/chromatin-bound motion, using **MCM2_Bound.csv** as the MCM-bound control,
4. supported by temporal trapping evidence,
5. not driven only by one short slow segment or one noisy sliding window.

The final output should classify tracks into interpretable control-guided classes:

- `free_like`
- `chromatin_bound_like`
- `mcm_bound_like`
- `slow_diffusive`
- `mixed`
- `target_specific_trapping_like`
- `ambiguous`

This project should be implemented in a way that is reproducible, logged, recoverable, and safe for the existing SMol-FIESTA codebase.

---

## 1. User-filled paths and local execution instructions

### 1.1 Project data folder

The user will manually fill in the absolute path below.

```text
CONDENSATE_CLASSIFICATION_PJ = "PASTE_ABSOLUTE_PATH_TO_condensate_classification_pj_HERE"
```

This folder contains the analyzed data for:

- TDP43
- NONO
- NLS
- H2B
- MCM2
- manually prepared `MCM2_Bound.csv`

Codex must assume that all project data are inside this folder.

### 1.2 SMol-FIESTA local module folder

The user will manually fill in the absolute path below.

```text
SMOL_FIESTA_MODULE_FOLDER = "PASTE_ABSOLUTE_PATH_TO_SMOL_FIESTA_MODULE_FOLDER_HERE"
```

This is the only codebase Codex is allowed to inspect or modify.

### 1.3 Local Anaconda Prompt instructions

The user will manually fill in how SMol-FIESTA is run locally.

```text
HOW_I_RUN_SMOL_FIESTA_LOCALLY:

PASTE YOUR LOCAL ANACONDA PROMPT COMMANDS HERE.

Example format only:
conda activate smol_env
cd C:/path/to/Smol-FIESTA
python BatchRun_Rebind.py -c C:/path/to/config.toml

Replace with your real commands.
```

Codex must not invent the user's local commands. Codex may create new scripts/modules and then report exactly how they should be called, but it must leave this section for the user to define the existing local SMol-FIESTA execution.

---

## 2. Strict folder-access rules

Codex must obey the following access rules.

### 2.1 Allowed folders

Codex may access only:

1. `CONDENSATE_CLASSIFICATION_PJ`
2. `SMOL_FIESTA_MODULE_FOLDER`

### 2.2 Forbidden folders

Codex must not read, write, delete, scan, or modify files outside these two locations.

Codex must not access:

- Desktop
- Downloads
- Documents
- OneDrive root
- SharePoint root
- parent directories of the project folder
- unrelated microscopy datasets
- unrelated Python environments
- unrelated Git repositories

### 2.3 Safe output rule

All new project outputs must be written inside:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/
```

All code backups must be written inside:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/
```

No output should overwrite original SMol-FIESTA data files.

---

## 3. Git version control for `condensate_classification_pj`

The project folder `CONDENSATE_CLASSIFICATION_PJ` should be initialized as a Git repository so that Codex leaves a clear, recoverable record of the project state, code changes, analysis runs, logs, summaries, and final output tables.

The Git repository should live only inside:

```text
CONDENSATE_CLASSIFICATION_PJ
```

The purpose of Git in this project is:

1. to preserve a history of all analysis changes,
2. to make the project recoverable,
3. to document exactly what Codex changed,
4. to allow the user to push the project to a personal GitHub repository,
5. to avoid losing previous versions of output files or analysis scripts.

### 3.1 Git safety rules

Codex must follow these rules:

1. Codex may initialize Git only inside `CONDENSATE_CLASSIFICATION_PJ`.
2. Codex must not initialize Git in parent folders.
3. Codex must not add unrelated files outside `CONDENSATE_CLASSIFICATION_PJ`.
4. Codex must not force-push to GitHub.
5. Codex must not delete Git history.
6. Codex must not commit files containing secrets, passwords, tokens, API keys, private credentials, or personal access tokens.
7. Codex must check file sizes before committing.
8. Codex must warn the user if very large microscopy files, raw movies, TIFF stacks, AVI files, ND2 files, CZI files, LIF files, or other heavy raw-data files are present.
9. Codex must create or update a `.gitignore` file before the first commit.
10. Codex must not push to GitHub unless the user explicitly provides the GitHub remote URL and asks Codex to push.
11. Codex must write every Git command it runs into the main log file.
12. Codex must include Git status information in `RUN_SUMMARY.md`.

### 3.2 Required GitHub remote URL

The user has specified the exact personal GitHub repository for this project. Codex must use this repository as the `origin` remote for `CONDENSATE_CLASSIFICATION_PJ`:

```text
GITHUB_REMOTE_URL = "https://github.com/MuyiTZ/condensate_classification_pj"
```

Codex must push the Git-tracked project contents to this repository after successful commits, unless authentication fails or Git reports that the remote already points somewhere else.

Rules:

1. Codex must not invent or substitute another GitHub URL.
2. Codex must not push to any repository other than `https://github.com/MuyiTZ/condensate_classification_pj`.
3. Codex must not force-push.
4. If `origin` already exists, Codex must run `git remote -v` and verify that it matches this URL before pushing.
5. If `origin` points to a different repository, Codex must stop and report this in the log and `RUN_SUMMARY.md`.
6. If GitHub authentication is not configured on the user's computer, Codex must leave the local commits intact and write the exact push command for the user to run manually.

### 3.3 Recommended `.gitignore`

Codex should create or update:

```text
CONDENSATE_CLASSIFICATION_PJ/.gitignore
```

Suggested content:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.ipynb_checkpoints/

# Operating system files
.DS_Store
Thumbs.db
desktop.ini

# Temporary files
*.tmp
*.bak
*.swp
~$*

# Local/private environment files and credentials
.env
*.env
secrets.*
credentials.*
token.*
*.pem
*.key

# Python/virtual environment folders that should not be versioned
venv/
.venv/
env/
conda-meta/
```

Important: the user specifically wants the project record to include **logs, results, and data**. Therefore Codex must **not** ignore these by default:

```text
*.log
*.csv
*.xlsx
*.md
*.py
*.toml
*.png
*.pdf
*.txt
*.json
*.tif
*.tiff
*.avi
*.mp4
*.npy
*.npz
```

Before committing or pushing, Codex must scan tracked file sizes. GitHub blocks files larger than about 100 MB and warns for files larger than about 50 MB. If any file is larger than 50 MB, Codex must list it in the log and `RUN_SUMMARY.md`. If any file is larger than 100 MB, Codex must stop before pushing and explain that the file is too large for normal GitHub upload. Codex must not silently exclude large project data unless the user explicitly approves a `.gitignore` change or Git LFS setup.

### 3.4 Initial Git setup commands

Codex should run these commands only inside `CONDENSATE_CLASSIFICATION_PJ`:

```bash
git init
git status
```

Then Codex should create or update `.gitignore`.

Then Codex should run:

```bash
git add .gitignore
git commit -m "Initialize condensate classification project repository"
```

If Git user identity is not configured, Codex should stop and tell the user to run either the global configuration:

```bash
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL"
```

or the repository-only configuration:

```bash
git config user.name "YOUR_NAME"
git config user.email "YOUR_EMAIL"
```

Codex must not invent the user's Git identity.

### 3.5 Git commits during Codex work

Codex should make small, descriptive commits at key stages.

Recommended commit sequence:

```bash
git add .
git commit -m "Add control-guided condensate classification specification"
```

After creating the analysis script:

```bash
git add .
git commit -m "Add control-guided condensate classification script"
```

After dry-run succeeds:

```bash
git add .
git commit -m "Record dry-run inventory for condensate classification"
```

After full analysis succeeds:

```bash
git add .
git commit -m "Run control-guided condensate classification analysis"
```

After acceptance tests pass:

```bash
git add .
git commit -m "Add final classification outputs and run summary"
```

If there are no changes to commit at any stage, Codex should log that no commit was necessary.

### 3.6 GitHub remote setup and push

Codex must configure the project repository to use the specified GitHub repository:

```bash
git remote add origin https://github.com/MuyiTZ/condensate_classification_pj
git branch -M main
git push -u origin main
```

If `origin` already exists, Codex must run:

```bash
git remote -v
```

Then:

- if `origin` already points to `https://github.com/MuyiTZ/condensate_classification_pj`, Codex may continue;
- if `origin` points anywhere else, Codex must stop and report the mismatch;
- if authentication fails, Codex must not retry repeatedly and must write the manual command for the user.

Codex must not run:

```bash
git push --force
```

or any equivalent force-push command.

### 3.7 Git status reporting

At the end of every Codex run, Codex must include the following command outputs in `RUN_SUMMARY.md`:

```bash
git status
git log --oneline -n 10
```

The summary should report:

- whether `CONDENSATE_CLASSIFICATION_PJ` is a Git repository,
- latest commit hash,
- latest commit message,
- whether there are uncommitted changes,
- whether a GitHub remote is configured,
- whether the latest commit was pushed.

### 3.8 Git recovery notes

Codex should create:

```text
CONDENSATE_CLASSIFICATION_PJ/GIT_RECOVERY_NOTES.md
```

This file should explain the following commands:

```bash
# See recent commits
git log --oneline

# See changed files
git status

# See changes in a file
git diff path/to/file

# Restore one file to the last committed version
git restore path/to/file

# Restore the whole project to the last committed version
git restore .

# Go back to a previous commit temporarily
git checkout COMMIT_HASH

# Return to main
git checkout main
```

Codex must not run destructive Git commands such as:

```bash
git reset --hard
git clean -fd
```

unless the user explicitly asks and understands the consequence.

### 3.9 Relationship between Git and SMol-FIESTA code backups

Git inside `CONDENSATE_CLASSIFICATION_PJ` does not replace the SMol-FIESTA module backup system.

Codex must still create file-level backups for any modified file inside `SMOL_FIESTA_MODULE_FOLDER`, as described in the version backup and recovery section below.

The project Git repository records the classification project. The SMol-FIESTA backup folder protects the original codebase.

---

## 4. Mandatory logging and audit trail

Codex must create a log file before doing any work.

### 4.1 Log folder

Create:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/logs/
```

### 4.2 Main log file

Create a timestamped log file:

```text
control_guided_classification_YYYYMMDD_HHMMSS.log
```

The log must record:

- start time
- end time
- Python version
- operating system
- current working directory
- paths used
- all files discovered
- all files read
- all files created
- all files modified
- all modules modified
- all backups created
- all warnings
- all errors
- all assumptions
- all skipped steps and why
- model parameters
- random seeds
- package versions when available
- final output summary

### 4.3 Human-readable run summary

At the end of every run, Codex must create:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/RUN_SUMMARY.md
```

This summary must include:

- what was done
- what input files were used
- what outputs were generated
- what model was trained
- what features were used
- how MCM2_Bound was used
- how H2B was used
- how NLS was used
- what thresholds were selected
- how many tracks were classified into each class
- any files that could not be parsed
- any assumptions that may affect interpretation
- exact commands to rerun the analysis

---

## 5. Version backup and recovery rules

Codex must make recoverable backups before modifying any SMol-FIESTA module.

### 5.1 Before modifying code

Before editing any file inside `SMOL_FIESTA_MODULE_FOLDER`, Codex must:

1. create a backup copy of the original file,
2. place it inside:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/YYYYMMDD_HHMMSS/
```

3. preserve relative path structure.

Example:

If modifying:

```text
SMOL_FIESTA_MODULE_FOLDER/condensate_evaluation.py
```

Backup should be:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/YYYYMMDD_HHMMSS/condensate_evaluation.py
```

### 5.2 Backup manifest

Create:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/YYYYMMDD_HHMMSS/BACKUP_MANIFEST.csv
```

Columns:

- `timestamp`
- `original_path`
- `backup_path`
- `sha256_original`
- `file_size_bytes`
- `reason_for_backup`

### 5.3 Recovery script

Create a recovery script:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/YYYYMMDD_HHMMSS/restore_backups.py
```

This script should copy backed-up files back to their original paths.

It must not run automatically. It should only exist for user-controlled recovery.

### 5.4 Prefer adding new modules

Codex should prefer creating new files instead of modifying existing SMol-FIESTA modules.

Recommended new module name:

```text
control_guided_condensate_classification.py
```

If modification of existing modules is not necessary, do not modify them.

---

## 6. Expected input files

Codex should search recursively inside `CONDENSATE_CLASSIFICATION_PJ` only.

The project is expected to contain outputs from Step 1 and Step 2.

### 6.1 Expected folder structure

Codex should assume the project follows this structure unless the real file inventory shows otherwise:

```text
D:/Tianzi/condensate_classification_pj/
    TDP43/
        WT-0416-CT/
            CSV/
                SF_10ms_condensate_pj_/
                    Step 1 SMol-FIESTA outputs for potential condensate tracks
            seg/
                segmentation masks
    NONO/
        strain-monthday-condition/
            CSV/
                folder_of_current_SMol_FIESTA_analysis_on_potential_condensate_tracks/
            seg/
    NLS/
        strain-monthday-condition/
            CSV/
                folder_of_current_SMol_FIESTA_analysis_on_potential_condensate_tracks/
            seg/
    H2B/
        strain-monthday-condition/
            CSV/
                folder_of_current_SMol_FIESTA_analysis_on_potential_condensate_tracks/
            seg/
    MCM2/
        HCT116-1125-CT/
            CSV/
                SF_10ms_condensate_may22_/
                    single-behaviour-track-MCM2-bound.csv
                    Step 1 SMol-FIESTA outputs for MCM2
            seg/
```

The general pattern is:

```text
CONDENSATE_CLASSIFICATION_PJ/
    "protein name"/
        "strain"-"month date"-"condition"/
            CSV/
                "folder of current SMol-FIESTA analysis on potential condensate track"/
                    output files
            seg/
                segmentation files
```

Codex should parse metadata from this structure as follows:

- `protein` from the first folder under `CONDENSATE_CLASSIFICATION_PJ`, for example `TDP43`, `NONO`, `NLS`, `H2B`, `MCM2`;
- `strain`, `date_or_batch`, and `condition` from the second-level folder, for example `WT-0416-CT` or `HCT116-1125-CT`;
- `analysis_folder` from the folder inside `CSV`, for example `SF_10ms_condensate_pj_`;
- `source_file` from the actual CSV file name.

For the example `WT-0416-CT`, Codex should infer:

```text
strain = WT
date_or_batch = 0416
condition = CT
```

For the example `HCT116-1125-CT`, Codex should infer:

```text
strain = HCT116
date_or_batch = 1125
condition = CT
```

If the folder name contains more than three dash-separated parts, Codex should preserve the full original folder name in `dataset_name` and use conservative parsing rather than guessing aggressively. All parsing assumptions must be logged.

### 6.2 Expected Step 1 files

For each protein/dataset, Codex should look for files such as:

- `condensate_evaluation_summary.csv`
- `condensate_evaluation_windows.csv`
- `condensate_stats.csv`
- `single_behaviour_track_breakdown.csv`
- `multi_behaviour_track_breakdown.csv`
- any existing SMol-FIESTA track-level classification outputs

The exact folder structure may vary. Codex must recursively detect files and infer protein identity from folder names and/or file names.

### 6.3 Required Step 2 file

Codex must find the MCM2 bound-track file. The expected file is:

```text
D:/Tianzi/condensate_classification_pj/MCM2/HCT116-1125-CT/CSV/SF_10ms_condensate_may22_/single-behaviour-track-MCM2-bound.csv
```

This file is the required Step 2 MCM2-bound control input. It contains only the single-behaviour MCM2 tracks that the user wants to use as the primary benchmark for stable replication-associated chromatin-bound confinement.

For internal standardization, Codex may copy this file into the output folder as:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/standardized_inputs/MCM2_Bound.csv
```

Codex must not overwrite the original `single-behaviour-track-MCM2-bound.csv`.

If multiple candidate MCM2-bound files are found, Codex should prioritize the exact expected file above. If the exact expected file is missing but other likely MCM2-bound files exist, Codex must stop and report the candidates in the log and `RUN_SUMMARY.md`.

If no MCM2-bound file is found, Codex must stop and write a clear error into the log and `RUN_SUMMARY.md`.

### 6.4 Required biological groups

Codex should identify these datasets:

- `NLS`
- `H2B`
- `MCM2`
- `MCM2_Bound`
- `TDP43`
- `NONO`

Acceptable folder/file naming variants:

- `TDP43`, `TDP-43`, `TARDBP`
- `NONO`, `p54nrb`
- `NLS`, `NLS-Halo`, `NLS_HaloTag`
- `H2B`, `H2b`, `Histone_H2B`
- `MCM2`, `Mcm2`
- `MCM2_Bound`, `MCM2-bound`, `MCM2_bound_tracks`

Codex must log exactly how each dataset identity was inferred.

---

## 7. Step 3: Build the control-guided feature matrix

### 7.1 Goal

Create one unified track-level table where each row is a track and each column is a feature used for control-guided classification.

Output:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/feature_matrix_tracks.csv
```

Also create:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/feature_dictionary.csv
```

### 7.2 Track identity columns

The feature matrix must contain stable identity columns:

- `dataset_name`
- `protein`
- `condition`, if available
- `replicate`, if available
- `source_file`
- `source_folder`
- `track_id`
- `cell_id`, if available
- `video_id`, if available
- `n_frames`, if available
- `track_length`, if available
- `is_control`
- `control_role`

`control_role` should be:

- `free_like_control` for NLS
- `chromatin_bound_control` for H2B
- `mcm_bound_control` for MCM2_Bound
- `target` for TDP43 and NONO
- `unused_or_reference` for total MCM2 unless explicitly used

### 7.3 Features to collect from existing SMol-FIESTA outputs

Codex must not assume exact column names. It should implement flexible column mapping using case-insensitive matching and synonym lists.

#### Mobility features

Try to extract:

- `D`
- `D2`
- `mean_D`
- `median_D`
- `min_D`
- `max_D`
- `diffusion_coefficient`
- `step_size_mean`
- `step_size_median`
- `step_size_p95`
- `mean_displacement`
- `net_displacement`
- `path_length`

#### Geometry features

Try to extract:

- `Rg`
- `radius_of_gyration`
- `area_of_confinement`
- `confinement_area`
- `compactness`
- `anisotropy`
- `asymmetry`
- `eccentricity`

#### Temporal and dwell features

Try to extract:

- `max_trap_dwell_frames`
- `mean_trap_dwell_frames`
- `trap_prob_mean`
- `trap_prob_max`
- `supported_high_score_window`
- `n_supported_high_score_windows`
- `frac_supported_high_score_windows`
- `max_consecutive_bound`
- `max_consecutive_constrained`
- `max_consecutive_diffusive`
- `frac_bound`
- `frac_constrained`
- `frac_diffusive`
- `n_state_switches`
- `transition_rate`
- `bound_segment_mean`
- `bound_segment_min`
- `bound_segment_max`

#### Recurrence and local trapping features

Try to extract:

- `recurrence`
- `recurrence_r1`
- `recurrence_r2`
- `local_density`
- `return_probability`
- `revisit_fraction`
- `trapping_score`
- `temporal_score`
- `composite_trapping_score`
- `geometry_score`

#### Existing classification labels

Try to extract:

- `classification`
- `track_class`
- `final_classification`
- `single_or_multi`
- `behaviour_class`
- `behavior_class`

Existing classifications should be preserved as metadata, not blindly used as final ground truth.

### 7.4 Sliding-window aggregation

If `condensate_evaluation_windows.csv` exists, Codex should aggregate window-level features to track-level features.

For each numeric window feature, calculate:

- mean
- median
- standard deviation
- minimum
- maximum
- 5th percentile
- 95th percentile
- number of valid windows

For binary features such as `supported_high_score_window`, calculate:

- count
- fraction
- max
- any

Output window-aggregated features with clear suffixes:

- `_win_mean`
- `_win_median`
- `_win_std`
- `_win_min`
- `_win_max`
- `_win_p05`
- `_win_p95`
- `_win_count`
- `_win_frac`

### 7.5 Handling tracks shorter than sliding-window size

If a track is shorter than the window size used in Step 1, it may not appear in the window table.

Codex must not silently discard such tracks.

Rules:

1. Keep short tracks in the feature matrix if they appear in summary or behavior-breakdown files.
2. Add `has_window_features = False`.
3. Add `shorter_than_window = True` if track length is known and shorter than the configured window size.
4. Final classification for tracks with insufficient data should usually be `ambiguous`, unless there is enough independent feature evidence.

### 7.6 Missing values

Codex must not drop rows simply because some features are missing.

Rules:

1. Preserve rows.
2. For model training, impute numeric features using training-control medians.
3. Add missingness indicator columns for key features when useful.
4. Log feature missingness rates.
5. Exclude features that are missing in more than 70% of rows, unless they are biologically critical and only missing in one dataset.

### 7.7 Required output from Step 3

Create:

```text
feature_matrix_tracks.csv
feature_dictionary.csv
feature_missingness_report.csv
input_file_inventory.csv
track_count_by_dataset.csv
```

---

## 8. Step 4: Learn the control landscape

### 8.1 Goal

Use controls to model known nuclear mobility behaviors.

Training controls:

- NLS = `free_like_control`
- H2B = `chromatin_bound_control`
- MCM2_Bound = `mcm_bound_control`

Target datasets:

- TDP43
- NONO

Total MCM2 should not be used as a training class unless the user explicitly asks. The manually prepared `MCM2_Bound.csv` is the MCM control.

### 8.2 Required models

Codex should implement at least three model layers.

#### Model A: supervised control classifier

Train a classifier to distinguish:

- `free_like_control`
- `chromatin_bound_control`
- `mcm_bound_control`

Recommended starting models:

1. Random Forest classifier
2. Multinomial logistic regression with standardized features

Use both if possible:

- Random Forest for nonlinear patterns and feature importance
- Logistic regression for interpretability

If package availability is limited, use scikit-learn models available in the local environment.

#### Model B: control-manifold outlier detector

Train an outlier/anomaly model using only the combined controls:

- NLS
- H2B
- MCM2_Bound

Recommended options:

1. Isolation Forest
2. One-class SVM
3. Robust covariance / Mahalanobis distance if feature dimensions allow

The purpose is to identify target tracks that do not fit any known control behavior.

#### Model C: interpretable distance-to-controls

Calculate distance from each track to each control class.

Minimum requirement:

- z-scored Euclidean distance to each control centroid
- optionally Mahalanobis distance if covariance matrix is stable

Output columns:

- `distance_to_NLS_centroid`
- `distance_to_H2B_centroid`
- `distance_to_MCM2_Bound_centroid`
- `nearest_control_class`
- `nearest_control_distance`
- `control_outlier_score`

### 8.3 Feature preprocessing

Codex must implement a reproducible preprocessing pipeline:

1. Keep identity columns separate.
2. Select numeric feature columns only.
3. Remove columns with too many missing values.
4. Remove zero-variance columns.
5. Impute missing numeric values using training-control median.
6. Standardize features using training-control mean and standard deviation.
7. Apply the same preprocessing to targets.

The fitted preprocessing objects must be saved.

### 8.4 Avoid data leakage

Codex must avoid training on target data.

Rules:

- TDP43 and NONO must not be used to fit scalers, imputers, PCA, supervised classifiers, or anomaly model thresholds.
- Target data may be transformed using preprocessing learned from controls.
- Thresholds must be learned from controls only.

### 8.5 Cross-validation and sanity checks

If sufficient control data exist, Codex should perform stratified cross-validation on the control classifier.

Report:

- accuracy
- balanced accuracy
- confusion matrix
- per-class precision
- per-class recall
- per-class F1 score

If there are too few tracks for cross-validation, Codex should skip CV and write a warning.

### 8.6 Dimensionality reduction for visualization, not classification

Codex should create PCA and UMAP if packages are available.

Rules:

- PCA may be required.
- UMAP is optional and should be skipped if `umap-learn` is not installed.
- t-SNE is optional and exploratory only.
- Dimensionality reduction should not be used as the only classifier.

Outputs:

```text
PCA_coordinates_tracks.csv
UMAP_coordinates_tracks.csv
```

Plots:

```text
plots/pca_by_dataset.png
plots/pca_by_control_role.png
plots/pca_by_final_class.png
plots/umap_by_dataset.png
plots/umap_by_control_role.png
plots/umap_by_final_class.png
```

### 8.7 Required output from Step 4

Create:

```text
control_model_predictions.csv
control_classifier_metrics.csv
control_classifier_confusion_matrix.csv
feature_importance_random_forest.csv
logistic_regression_coefficients.csv
control_centroids.csv
distance_to_controls.csv
anomaly_model_scores.csv
trained_models/
```

The `trained_models/` folder should contain saved preprocessing and model objects using `joblib` if available.

---

## 9. Step 5: Define target-specific trapping-like classification

### 9.1 Goal

Create a final classification that combines:

1. supervised similarity to controls,
2. distance/outlier score relative to controls,
3. existing SMol-FIESTA trapping features,
4. temporal support,
5. diffusive-burst penalty.

Output:

```text
final_control_guided_track_classification.csv
```

### 9.2 Required output columns

The final table must include all identity columns plus:

- `P_free_like`
- `P_chromatin_bound_like`
- `P_mcm_bound_like`
- `supervised_control_prediction`
- `nearest_control_class`
- `nearest_control_distance`
- `control_outlier_score`
- `is_control_outlier`
- `trapping_score`
- `temporal_score`
- `trap_prob_mean`
- `max_trap_dwell_frames`
- `n_supported_high_score_windows`
- `frac_diffusive`
- `max_consecutive_diffusive`
- `supported_temporal_trapping`
- `diffusive_burst_flag`
- `final_control_guided_class`
- `classification_reason`

### 9.3 Thresholding philosophy

Codex should use control-derived thresholds wherever possible.

Recommended thresholds:

#### Free-like threshold

Use NLS to estimate the false-positive floor.

Examples:

- `trapping_score > 95th percentile of NLS`
- or `temporal_score > 95th percentile of NLS`
- or target track has low `P_free_like`

#### Chromatin-bound threshold

Use H2B to identify tracks that look like generic chromatin confinement.

Examples:

- high `P_chromatin_bound_like`
- close to H2B centroid
- not an outlier from H2B-like space

#### MCM-bound threshold

Use MCM2_Bound to identify tracks that look like replication/chromatin-bound confinement.

Examples:

- high `P_mcm_bound_like`
- close to MCM2_Bound centroid
- not an outlier from MCM2_Bound-like space

#### Target-specific trapping threshold

A track can be called `target_specific_trapping_like` only if it passes all of the following:

1. not free-like:
   - `P_free_like` below a chosen threshold, or trapping score above NLS high percentile
2. not explained by H2B:
   - `P_chromatin_bound_like` not dominant, or track is outlier relative to H2B-like behavior
3. not explained by MCM2_Bound:
   - `P_mcm_bound_like` not dominant, or track is outlier relative to MCM2_Bound behavior
4. temporally supported:
   - see section 8.4
5. not dominated by diffusive bursts:
   - see section 8.5

### 9.4 Temporal support rule

Use the following biological/computational rule:

```text
supported_temporal_trapping =
    high geometry/trapping score
    AND
    (trap_prob_mean >= 0.30 OR max_trap_dwell_frames >= 4 OR n_supported_high_score_windows >= 1)
```

If exact column names differ, map them using the feature dictionary.

If `trap_prob_mean`, `max_trap_dwell_frames`, and `n_supported_high_score_windows` are all unavailable, temporal support cannot be established and the final class should usually be `ambiguous` unless other temporal features provide equivalent evidence.

### 9.5 Soft diffusive-burst penalty

Use the softer rule discussed by the user:

```text
If max_consecutive_diffusive >= 3
AND frac_diffusive is high
THEN do not classify as pure target_specific_trapping_like.
Classify as mixed instead, unless stronger evidence says otherwise.
```

Define `frac_diffusive is high` from controls when possible.

Recommended approach:

- calculate the distribution of `frac_diffusive` in NLS
- use a threshold such as the lower of:
  - 0.50
  - 75th percentile of NLS `frac_diffusive`
- log the chosen threshold

Suggested rule:

```text
diffusive_burst_flag =
    max_consecutive_diffusive >= 3
    AND frac_diffusive >= diffusive_fraction_threshold
```

If `diffusive_burst_flag = True` and the track otherwise passes trapping criteria:

```text
final_control_guided_class = mixed
```

not `target_specific_trapping_like`.

### 9.6 Suggested final classification logic

Apply the following in order.

#### Rule 1: Insufficient data

If too few usable features or no temporal evidence:

```text
final_control_guided_class = ambiguous
```

#### Rule 2: Free-like

If the track is strongly NLS-like:

```text
final_control_guided_class = free_like
```

Criteria can include:

- high `P_free_like`
- nearest control is NLS and distance is small
- trapping score not above NLS high percentile

#### Rule 3: Chromatin-bound-like

If the track is strongly H2B-like:

```text
final_control_guided_class = chromatin_bound_like
```

Criteria can include:

- high `P_chromatin_bound_like`
- nearest control is H2B and distance is small
- no target-specific outlier evidence

#### Rule 4: MCM-bound-like

If the track is strongly MCM2_Bound-like:

```text
final_control_guided_class = mcm_bound_like
```

Criteria can include:

- high `P_mcm_bound_like`
- nearest control is MCM2_Bound and distance is small
- no target-specific outlier evidence

#### Rule 5: Slow-diffusive

If the track is slow but lacks recurrence/dwell/temporal support:

```text
final_control_guided_class = slow_diffusive
```

This class is important. It prevents the classifier from treating every low-D track as condensate-like.

#### Rule 6: Mixed

If the track has both trapping evidence and strong diffusive-burst evidence:

```text
final_control_guided_class = mixed
```

#### Rule 7: Target-specific trapping-like

Only use this if the track:

- is from TDP43 or NONO,
- is not free-like,
- is not H2B-like,
- is not MCM2_Bound-like,
- has temporal trapping support,
- is an outlier or distinct from the combined control landscape,
- does not trigger the diffusive-burst penalty.

Then:

```text
final_control_guided_class = target_specific_trapping_like
```

### 9.7 Classification reason

Every row must include a short text explanation in `classification_reason`.

Examples:

```text
High P_free_like and low trapping score; classified as free_like.
```

```text
Nearest control is H2B with low distance and high P_chromatin_bound_like; classified as chromatin_bound_like.
```

```text
Above NLS trapping threshold, temporally supported, control outlier, not H2B-like or MCM2-like; classified as target_specific_trapping_like.
```

```text
Trapping evidence present but max_consecutive_diffusive >= 3 and high frac_diffusive; classified as mixed.
```

---

## 10. Statistical summaries to generate

Create per-dataset and per-condition summaries.

### 10.1 Track-level summary

Output:

```text
summary_by_dataset.csv
summary_by_protein.csv
summary_by_condition.csv
summary_by_replicate.csv
```

Include:

- total tracks
- number and fraction `free_like`
- number and fraction `chromatin_bound_like`
- number and fraction `mcm_bound_like`
- number and fraction `slow_diffusive`
- number and fraction `mixed`
- number and fraction `target_specific_trapping_like`
- number and fraction `ambiguous`
- median trapping score
- median temporal score
- median max trap dwell
- median control outlier score

### 10.2 Frame-level summary if possible

If frame counts are available, calculate:

- total frames
- frames assigned to each final class
- fraction of frames assigned to each final class

Output:

```text
summary_frames_by_dataset.csv
```

If frame-level calculation is not possible, log that frame-level summary was skipped.

### 10.3 Replicate-level comparison

If replicate information is available, calculate replicate-level fractions for each protein/condition.

Output:

```text
replicate_level_class_fractions.csv
```

No statistical test should be overinterpreted if there are fewer than 3 biological replicates.

---

## 11. Plots to generate

Create a folder:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/plots/
```

Generate the following plots when data allow:

1. stacked bar plot of final classes by dataset
2. stacked bar plot of final classes by protein
3. boxplot/violin plot of trapping score by dataset
4. boxplot/violin plot of temporal score by dataset
5. boxplot/violin plot of control outlier score by dataset
6. PCA plot colored by dataset
7. PCA plot colored by final class
8. distance-to-control plots
9. feature importance plot from Random Forest
10. confusion matrix heatmap for control classifier

All plots should be saved as both:

- `.png`
- `.pdf`

### 11.1 Easy-to-interpret result summaries

In addition to raw machine-readable CSV files, Codex must create human-friendly summaries that make the biological interpretation easy. These outputs should be understandable without opening the full feature matrix.

Create:

```text
CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/easy_interpretation/
    EXECUTIVE_SUMMARY.md
    simplified_results_table.csv
    simplified_results_table.xlsx, if openpyxl is available
    target_vs_control_interpretation.md
    key_findings_bullets.md
    figure_readme.md
```

`EXECUTIVE_SUMMARY.md` must include:

1. a one-paragraph summary of the analysis purpose;
2. a plain-language explanation of how NLS, H2B, and MCM2-bound were used;
3. a short section for each target protein, especially TDP43 and NONO;
4. a ranked list of the strongest findings;
5. a cautious interpretation section explaining what can and cannot be concluded without condensate masks;
6. a short list of recommended next validation experiments or plots.

`simplified_results_table.csv` must include one row per protein/condition/replicate if available, with columns such as:

- `protein`
- `condition`
- `replicate`
- `n_tracks`
- `percent_free_like`
- `percent_chromatin_bound_like`
- `percent_mcm_bound_like`
- `percent_slow_diffusive`
- `percent_mixed`
- `percent_target_specific_trapping_like`
- `percent_ambiguous`
- `median_trapping_score`
- `median_temporal_score`
- `plain_language_interpretation`

Codex must also create at least these easy-to-read figures when data allow:

1. `easy_interpretation/final_class_percent_by_protein.png` and `.pdf`
2. `easy_interpretation/target_specific_trapping_percent_by_protein.png` and `.pdf`
3. `easy_interpretation/control_similarity_heatmap.png` and `.pdf`
4. `easy_interpretation/trapping_score_controls_vs_targets.png` and `.pdf`
5. `easy_interpretation/decision_flow_summary.png` and `.pdf`, if feasible

The easy summaries must use cautious wording. They should say `candidate target-specific trapping-like dynamics`, not `definitive condensate localization`.

---

## 12. Recommended implementation structure

Prefer creating one new script:

```text
SMOL_FIESTA_MODULE_FOLDER/control_guided_condensate_classification.py
```

Recommended command-line interface:

```bash
python control_guided_condensate_classification.py --project-folder "PATH_TO_condensate_classification_pj"
```

Optional arguments:

```bash
--output-folder
--window-size
--random-seed
--nls-name
--h2b-name
--mcm-bound-file
--target-names
--min-feature-nonmissing
--probability-threshold
--nls-quantile
--dry-run
```

### 12.1 Dry run mode

Codex should implement a dry-run option:

```bash
python control_guided_condensate_classification.py --project-folder "PATH" --dry-run
```

Dry run should:

- list discovered files
- infer dataset identities
- check required files
- check required columns
- report expected outputs
- not train models
- not write final classification files

### 12.2 Random seed

Use a fixed default random seed:

```text
random_seed = 42
```

Write this into the log and output metadata.

---

## 13. Acceptance tests

Codex must verify the implementation before considering the task complete.

### 13.1 Required checks

The run must verify:

- `feature_matrix_tracks.csv` exists
- `final_control_guided_track_classification.csv` exists
- `RUN_SUMMARY.md` exists
- log file exists
- no original input files were overwritten
- MCM2_Bound was used as the MCM-bound control
- TDP43/NONO were not used for model fitting
- all final-class values are from the allowed class list
- every final-class row has a non-empty `classification_reason`
- all generated files are inside `control_guided_classification/`
- all modified code files have backups

### 13.2 Allowed final classes

Only these final classes are allowed:

```text
free_like
chromatin_bound_like
mcm_bound_like
slow_diffusive
mixed
target_specific_trapping_like
ambiguous
```

### 13.3 Failure behavior

If any required check fails, Codex must:

1. stop,
2. write the failure to the log,
3. write a clear failure section in `RUN_SUMMARY.md`,
4. not pretend the task completed successfully.

---

## 14. Biological interpretation rules for reports

Codex must use cautious language.

Allowed wording:

- `target-specific trapping-like dynamics`
- `control-guided trapping-like classification`
- `not explained by NLS, H2B, or MCM2_Bound controls`
- `candidate condensate-like behavior`
- `track dynamics consistent with trapping or confinement`

Avoid overclaiming:

- do not say `inside condensates` unless condensate location/mask exists
- do not say `definitive condensate tracks`
- do not say `paraspeckle localization` from tracking alone
- do not say H2B is a pure negative control
- do not say MCM2 is a pure negative control
- do not say NLS is perfectly free

Correct interpretation:

- NLS defines free-like nuclear mobility and the empirical false-positive floor.
- H2B defines chromatin-bound confinement.
- MCM2_Bound defines replication/chromatin-bound confinement.
- TDP43/NONO tracks are interesting when they show reproducible trapping-like behavior beyond all three controls.

---

## 15. Final deliverables

At completion, Codex should produce:

```text
CONDENSATE_CLASSIFICATION_PJ/
    .gitignore
    GIT_RECOVERY_NOTES.md

CONDENSATE_CLASSIFICATION_PJ/control_guided_classification/
    RUN_SUMMARY.md
    feature_matrix_tracks.csv
    feature_dictionary.csv
    feature_missingness_report.csv
    input_file_inventory.csv
    track_count_by_dataset.csv
    control_model_predictions.csv
    control_classifier_metrics.csv
    control_classifier_confusion_matrix.csv
    feature_importance_random_forest.csv
    logistic_regression_coefficients.csv
    control_centroids.csv
    distance_to_controls.csv
    anomaly_model_scores.csv
    final_control_guided_track_classification.csv
    summary_by_dataset.csv
    summary_by_protein.csv
    summary_by_condition.csv
    summary_by_replicate.csv
    replicate_level_class_fractions.csv
    summary_frames_by_dataset.csv, if possible
    plots/
    easy_interpretation/
    trained_models/
    logs/
    GIT_RECOVERY_NOTES.md
```

Inside the SMol-FIESTA module folder:

```text
SMOL_FIESTA_MODULE_FOLDER/
    control_guided_condensate_classification.py
```

If existing files were modified:

```text
SMOL_FIESTA_MODULE_FOLDER/_codex_backups/control_guided_classification/YYYYMMDD_HHMMSS/
    BACKUP_MANIFEST.csv
    restore_backups.py
    backed-up files...
```

---

## 16. Suggested first Codex actions

When Codex receives this file, it should proceed in this order:

1. Read this entire markdown file.
2. Identify the user-filled paths.
3. Confirm that both allowed folders exist.
4. Create the log folder and start the log.
5. Initialize Git inside `CONDENSATE_CLASSIFICATION_PJ` if it is not already a Git repository.
6. Create or update `.gitignore`.
7. Create `GIT_RECOVERY_NOTES.md`.
8. Make the initial Git commit if there are changes to commit.
9. Perform a dry inventory of files inside `CONDENSATE_CLASSIFICATION_PJ`.
10. Locate `MCM2_Bound.csv`.
11. Locate Step 1 outputs.
12. Infer dataset identities.
13. Create or update the new script `control_guided_condensate_classification.py`.
14. Commit the new or updated script.
15. Run dry-run mode.
16. If dry-run passes, commit the dry-run inventory.
17. Run the full analysis.
18. Write all outputs.
19. Run acceptance tests.
20. Write `RUN_SUMMARY.md`, including Git status and recent commit information.
21. Commit final outputs and summary if acceptance tests pass.
22. If the user provided a real `GITHUB_REMOTE_URL` and explicitly asked to push, push to GitHub.
23. Report concise final instructions to the user.

---

## 17. User reminder

This analysis does not prove physical condensate localization because no condensate masks or imaging markers are provided. It is a control-guided track-dynamics analysis designed to identify tracks whose behavior is not explained by free nuclear diffusion, chromatin-bound motion, or MCM-bound chromatin-associated motion.
