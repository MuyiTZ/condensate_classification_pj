# Control-Guided Condensate Classification Run Summary

Status: DRY-RUN PASS
Run date: 
2026-05-25T23:36:53.8780099-04:00

## What Was Done

- Read the project control specification.
- Created the required control_guided_classification folder structure.
- Initialized Git inside D:\Tianzi\condensate_classification_pj only.
- Added .gitignore and Git recovery notes.
- Added the new SMol-FIESTA module control_guided_condensate_classification.py.
- Performed dry-run inventory before full analysis.
- Committed project data, logs, and dry-run inventory after checking file sizes.

## Dry-Run Results

- TDP43: FOUND
- NONO: FOUND
- NLS: FOUND
- H2B: FOUND (folder is named H2b, canonicalized to H2B)
- MCM2: FOUND
- MCM2_Bound: FOUND
- single-behaviour-track-MCM2-bound.csv: FOUND

## Inputs Used

- Project folder: D:\Tianzi\condensate_classification_pj
- SMol-FIESTA module folder: C:\Users\rangq\Desktop\SMT_codes\Analysis_PIPELINE\workshopV2\Smol-FIESTA\SMol_FIESTA
- MCM2 bound file: D:\Tianzi\condensate_classification_pj\MCM2\HCT116-1125-CT\CSV\SF_10ms_condensate_may22_\single-behaviour-track-MCM2-bound.csv

## Outputs Generated So Far

- control_guided_classification/input_file_inventory.csv
- control_guided_classification/dry_run_csv_column_inventory.csv
- control_guided_classification/DRY_RUN_SUMMARY.md
- control_guided_classification/RUN_SUMMARY.md
- control_guided_classification/logs/control_guided_classification_*.log

## Full Analysis Status

Full model training and final classification were not run yet because dry-run was requested first and the available Python runtime is outside the two user-approved folders. Permission to use that runtime was rejected, so no workaround was attempted.

## File-Size Check

One file is larger than 50 MB and below 100 MB:
- H2b/HAP1-0117-CT/CSV/SF_10ms_condensate_may25_/Intermediates/tracks.csv: 71,745,112 bytes

No files larger than 100 MB were found in the dry-run file-size check.

## Git Status

```text
```

## Recent Git Log

```text
f386e4b Record dry-run inventory for condensate classification
9e81021 Initialize condensate classification project repository
```

## GitHub Remote

```text
No remote configured yet.
```

## Rerun Commands

```bash
python control_guided_condensate_classification.py --project-folder "D:\Tianzi\condensate_classification_pj" --dry-run
python control_guided_condensate_classification.py --project-folder "D:\Tianzi\condensate_classification_pj"
```

## Update 2026-05-26

- The bundled Codex Python was used only for syntax checking and dry-run inventory, as approved.
- The script dry-run completed successfully.
- Attempted to run final analysis with `conda run -n smol_env ...`, but `conda` is not available on this PowerShell PATH.
- Full analysis is blocked until the exact Anaconda/conda command or `conda.exe` path for `smol_env` is provided.
