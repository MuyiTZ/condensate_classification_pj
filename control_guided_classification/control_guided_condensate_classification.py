#!/usr/bin/env python3
"""
Control-guided condensate track classification.

This module implements the dry-run inventory and full analysis scaffold for the
control-guided condensate classification project. It reads only the project
folder supplied on the command line and writes outputs only under
control_guided_classification inside that project folder.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import numpy as np
    import pandas as pd
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(f"Required package missing: {exc}")

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        classification_report,
        confusion_matrix,
    )
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.decomposition import PCA
except ImportError:  # pragma: no cover - optional in limited environments
    IsolationForest = None
    RandomForestClassifier = None
    LogisticRegression = None
    accuracy_score = None
    balanced_accuracy_score = None
    classification_report = None
    confusion_matrix = None
    StratifiedKFold = None
    cross_val_predict = None
    PCA = None

try:
    import joblib
except ImportError:  # pragma: no cover
    joblib = None

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    plt = None


PROJECT_OUTPUT_NAME = "control_guided_classification"
RANDOM_SEED = 42
EXPECTED_MCM2_BOUND = Path(
    "MCM2/HCT116-1125-CT/CSV/SF_10ms_condensate_may22_/single-behaviour-track-MCM2-bound.csv"
)
REQUIRED_GROUPS = ["TDP43", "NONO", "NLS", "H2B", "MCM2", "MCM2_Bound"]
FINAL_CLASSES = [
    "free_like",
    "chromatin_bound_like",
    "mcm_bound_like",
    "slow_diffusive",
    "mixed",
    "target_specific_trapping_like",
    "ambiguous",
]
IDENTITY_COLUMNS = [
    "dataset_name",
    "protein",
    "condition",
    "replicate",
    "source_file",
    "source_folder",
    "track_id",
    "cell_id",
    "video_id",
    "n_frames",
    "track_length",
    "is_control",
    "control_role",
]


FEATURE_SYNONYMS = {
    "D": ["d", "diffusion_coefficient", "diffusion coefficient"],
    "mean_D": ["mean_d", "d_mean", "mean diffusion coefficient"],
    "median_D": ["median_d", "d_median"],
    "step_size_mean": ["step_size_mean", "mean_step_size", "step mean"],
    "step_size_median": ["step_size_median", "median_step_size"],
    "Rg": ["rg", "radius_of_gyration", "radius gyration"],
    "area_of_confinement": ["area_of_confinement", "confinement_area"],
    "compactness": ["compactness"],
    "anisotropy": ["anisotropy"],
    "eccentricity": ["eccentricity"],
    "max_trap_dwell_frames": ["max_trap_dwell_frames", "max_dwell", "max dwell"],
    "mean_trap_dwell_frames": ["mean_trap_dwell_frames", "mean_dwell"],
    "trap_prob_mean": ["trap_prob_mean", "mean_trap_probability"],
    "trap_prob_max": ["trap_prob_max", "max_trap_probability"],
    "n_supported_high_score_windows": ["n_supported_high_score_windows"],
    "frac_supported_high_score_windows": ["frac_supported_high_score_windows"],
    "max_consecutive_bound": ["max_consecutive_bound"],
    "max_consecutive_constrained": ["max_consecutive_constrained"],
    "max_consecutive_diffusive": ["max_consecutive_diffusive"],
    "frac_bound": ["frac_bound"],
    "frac_constrained": ["frac_constrained"],
    "frac_diffusive": ["frac_diffusive"],
    "n_state_switches": ["n_state_switches"],
    "transition_rate": ["transition_rate"],
    "recurrence": ["recurrence"],
    "local_density": ["local_density"],
    "return_probability": ["return_probability"],
    "revisit_fraction": ["revisit_fraction"],
    "trapping_score": ["trapping_score", "composite_trapping_score", "geometry_score"],
    "temporal_score": ["temporal_score"],
}


@dataclass
class RunContext:
    project_folder: Path
    output_folder: Path
    log_path: Path
    random_seed: int
    dry_run: bool

    def log(self, message: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message}\n")


def canonical_group(name: str) -> Optional[str]:
    key = name.lower().replace("-", "").replace("_", "")
    mapping = {
        "tdp43": "TDP43",
        "tardbp": "TDP43",
        "nono": "NONO",
        "p54nrb": "NONO",
        "nls": "NLS",
        "nlshalo": "NLS",
        "nlshalotag": "NLS",
        "h2b": "H2B",
        "histoneh2b": "H2B",
        "mcm2": "MCM2",
        "mcm2bound": "MCM2_Bound",
        "mcm2boundtracks": "MCM2_Bound",
    }
    return mapping.get(key)


def safe_relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def ensure_inside(path: Path, root: Path) -> None:
    path.resolve().relative_to(root.resolve())


def make_context(args: argparse.Namespace) -> RunContext:
    project = Path(args.project_folder).resolve()
    if not project.exists() or not project.is_dir():
        raise SystemExit(f"Project folder does not exist: {project}")

    output = Path(args.output_folder).resolve() if args.output_folder else project / PROJECT_OUTPUT_NAME
    ensure_inside(output, project)
    for sub in ["logs", "standardized_inputs", "plots", "easy_interpretation", "trained_models"]:
        (output / sub).mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = output / "logs" / f"control_guided_classification_{stamp}.log"
    ctx = RunContext(project, output, log_path, args.random_seed, args.dry_run)
    ctx.log("Started control-guided condensate classification")
    ctx.log(f"Python version: {sys.version}")
    ctx.log(f"Operating system: {platform.platform()}")
    ctx.log(f"Current working directory: {Path.cwd()}")
    ctx.log(f"Project folder: {project}")
    ctx.log(f"Output folder: {output}")
    ctx.log(f"Dry run: {args.dry_run}")
    ctx.log(f"Random seed: {args.random_seed}")
    return ctx


def parse_dataset_folder(name: str) -> Tuple[str, str, str]:
    parts = name.split("-")
    if len(parts) >= 3:
        return parts[0], parts[1], "-".join(parts[2:])
    if len(parts) == 2:
        return parts[0], parts[1], ""
    return name, "", ""


def infer_metadata(path: Path, project: Path) -> Dict[str, str]:
    rel_parts = path.resolve().relative_to(project.resolve()).parts
    protein_raw = rel_parts[0] if rel_parts else ""
    protein = canonical_group(protein_raw) or protein_raw
    dataset_name = rel_parts[1] if len(rel_parts) > 1 else protein_raw
    strain, date_or_batch, condition = parse_dataset_folder(dataset_name)
    analysis_folder = ""
    if "CSV" in rel_parts:
        idx = rel_parts.index("CSV")
        if len(rel_parts) > idx + 1:
            analysis_folder = rel_parts[idx + 1]
    return {
        "protein": protein,
        "dataset_name": dataset_name,
        "strain": strain,
        "date_or_batch": date_or_batch,
        "condition": condition,
        "analysis_folder": analysis_folder,
    }


def discover_files(ctx: RunContext) -> pd.DataFrame:
    rows = []
    for path in sorted(ctx.project_folder.rglob("*")):
        if ".git" in path.parts:
            continue
        if path.is_file():
            meta = infer_metadata(path, ctx.project_folder)
            rel = safe_relative(path, ctx.project_folder)
            group = meta["protein"]
            if path.name.lower() == "single-behaviour-track-mcm2-bound.csv":
                group = "MCM2_Bound"
            rows.append(
                {
                    "relative_path": rel,
                    "absolute_path": str(path),
                    "file_name": path.name,
                    "suffix": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                    "protein_inferred": group,
                    **meta,
                }
            )
    inventory = pd.DataFrame(rows)
    inventory.to_csv(ctx.output_folder / "input_file_inventory.csv", index=False)
    ctx.log(f"Discovered {len(inventory)} files")
    return inventory


def find_required_groups(inventory: pd.DataFrame) -> Dict[str, bool]:
    present = {group: False for group in REQUIRED_GROUPS}
    if inventory.empty:
        return present
    for group in inventory["protein_inferred"].dropna().astype(str).unique():
        canonical = canonical_group(group) or group
        if canonical in present:
            present[canonical] = True
    return present


def find_mcm2_bound(ctx: RunContext, inventory: pd.DataFrame) -> Tuple[Optional[Path], List[str]]:
    exact = ctx.project_folder / EXPECTED_MCM2_BOUND
    candidates = []
    if not inventory.empty:
        mask = inventory["file_name"].str.lower().str.contains("mcm2", na=False) & inventory[
            "file_name"
        ].str.lower().str.contains("bound", na=False)
        candidates = inventory.loc[mask, "relative_path"].tolist()
    if exact.exists():
        return exact, candidates
    return None, candidates


def csv_columns(path: Path) -> List[str]:
    try:
        return pd.read_csv(path, nrows=0).columns.tolist()
    except Exception:
        return []


def dry_run(ctx: RunContext, inventory: pd.DataFrame) -> int:
    group_presence = find_required_groups(inventory)
    mcm_path, candidates = find_mcm2_bound(ctx, inventory)

    csv_rows = []
    for rel in inventory.loc[inventory["suffix"].eq(".csv"), "relative_path"].tolist():
        path = ctx.project_folder / rel
        csv_rows.append(
            {
                "relative_path": rel,
                "columns": "|".join(csv_columns(path)),
                "n_columns": len(csv_columns(path)),
            }
        )
    pd.DataFrame(csv_rows).to_csv(ctx.output_folder / "dry_run_csv_column_inventory.csv", index=False)

    summary_lines = [
        "# Dry Run Summary",
        "",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"Project folder: `{ctx.project_folder}`",
        f"Output folder: `{ctx.output_folder}`",
        "",
        "## Required Dataset Presence",
        "",
    ]
    for group in REQUIRED_GROUPS:
        summary_lines.append(f"- {group}: {'FOUND' if group_presence[group] else 'MISSING'}")
    summary_lines.extend(
        [
            "",
            "## MCM2 Bound File",
            "",
            f"- Expected file: `{EXPECTED_MCM2_BOUND.as_posix()}`",
            f"- Status: {'FOUND' if mcm_path else 'MISSING'}",
        ]
    )
    if mcm_path:
        summary_lines.append(f"- Resolved path: `{mcm_path}`")
    if candidates:
        summary_lines.append("- Candidate MCM2-bound-like files:")
        summary_lines.extend([f"  - `{candidate}`" for candidate in candidates])
    summary_lines.extend(
        [
            "",
            "## Files",
            "",
            f"- Total files discovered: {len(inventory)}",
            f"- CSV files discovered: {int((inventory['suffix'] == '.csv').sum()) if not inventory.empty else 0}",
            "",
            "## Expected Full-Analysis Outputs",
            "",
            "- feature_matrix_tracks.csv",
            "- feature_dictionary.csv",
            "- control_model_predictions.csv",
            "- final_control_guided_track_classification.csv",
            "- summary_by_dataset.csv",
            "- plots/ and easy_interpretation/",
        ]
    )

    ok = all(group_presence.values()) and mcm_path is not None
    summary_lines.extend(["", f"Dry-run result: {'PASS' if ok else 'FAIL'}", ""])
    (ctx.output_folder / "DRY_RUN_SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")
    ctx.log(f"Dry-run group presence: {json.dumps(group_presence, sort_keys=True)}")
    ctx.log(f"Dry-run MCM2 bound status: {'found' if mcm_path else 'missing'}")
    ctx.log(f"Dry-run result: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


def normalize_key(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(columns: Iterable[str], synonyms: Sequence[str]) -> Optional[str]:
    normalized = {normalize_key(col): col for col in columns}
    for syn in synonyms:
        key = normalize_key(syn)
        if key in normalized:
            return normalized[key]
    return None


def track_key_columns(df: pd.DataFrame) -> List[str]:
    cols = []
    for synonyms in [["Video #", "video", "video_id"], ["Cell", "cell", "cell_id"], ["Track", "track", "track_id"]]:
        col = find_column(df.columns, synonyms)
        if col:
            cols.append(col)
    return cols


def numeric_summary(group: pd.DataFrame) -> Dict[str, float]:
    out = {}
    for canonical, synonyms in FEATURE_SYNONYMS.items():
        col = find_column(group.columns, [canonical] + synonyms)
        if col and pd.api.types.is_numeric_dtype(group[col]):
            values = pd.to_numeric(group[col], errors="coerce")
            out[canonical] = float(values.mean()) if values.notna().any() else math.nan
    return out


def behavior_features(group: pd.DataFrame) -> Dict[str, float]:
    col = find_column(group.columns, ["Bound", "bound", "behavior", "behaviour"])
    if not col:
        return {}
    vals = pd.to_numeric(group[col], errors="coerce").dropna().astype(int).tolist()
    valid = [v for v in vals if v in [0, 1, 2]]
    if not valid:
        return {}

    def max_run(target: int) -> int:
        best = cur = 0
        for v in valid:
            if v == target:
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        return best

    return {
        "frac_diffusive": valid.count(0) / len(valid),
        "frac_constrained": valid.count(1) / len(valid),
        "frac_bound": valid.count(2) / len(valid),
        "max_consecutive_diffusive": max_run(0),
        "max_consecutive_constrained": max_run(1),
        "max_consecutive_bound": max_run(2),
        "n_state_switches": sum(1 for a, b in zip(valid, valid[1:]) if a != b),
    }


def rows_from_csv(path: Path, ctx: RunContext, role_override: Optional[str] = None) -> List[Dict[str, object]]:
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        ctx.log(f"WARNING: could not parse CSV {path}: {exc}")
        return []
    if df.empty:
        return []

    meta = infer_metadata(path, ctx.project_folder)
    protein = "MCM2_Bound" if role_override == "mcm_bound_control" else meta["protein"]
    control_role = role_override or {
        "NLS": "free_like_control",
        "H2B": "chromatin_bound_control",
        "TDP43": "target",
        "NONO": "target",
    }.get(protein, "unused_or_reference")
    is_control = control_role in ["free_like_control", "chromatin_bound_control", "mcm_bound_control"]
    keys = track_key_columns(df)
    if not keys:
        keys = [df.index.name] if df.index.name else []

    rows = []
    groups = df.groupby(keys, dropna=False) if keys else [(("all",), df)]
    for key, group in groups:
        key_tuple = key if isinstance(key, tuple) else (key,)
        row = {
            "dataset_name": meta["dataset_name"],
            "protein": protein,
            "condition": meta["condition"],
            "replicate": meta["date_or_batch"],
            "source_file": path.name,
            "source_folder": str(path.parent),
            "track_id": key_tuple[-1] if key_tuple else len(rows),
            "cell_id": key_tuple[1] if len(key_tuple) > 1 else "",
            "video_id": key_tuple[0] if len(key_tuple) > 0 else "",
            "n_frames": len(group),
            "track_length": len(group),
            "is_control": is_control,
            "control_role": control_role,
        }
        row.update(numeric_summary(group))
        row.update(behavior_features(group))
        rows.append(row)
    return rows


def build_feature_matrix(ctx: RunContext, inventory: pd.DataFrame) -> pd.DataFrame:
    selected = []
    wanted_names = {
        "condensate_evaluation_summary.csv",
        "condensate_stats.csv",
        "single_behaviour_track_breakdown.csv",
        "multi_behaviour_track_breakdown.csv",
        "single-behaviour-track.csv",
        "multi-behaviour-track.csv",
    }
    for _, row in inventory.iterrows():
        name = str(row["file_name"]).lower()
        if name in wanted_names or name == "single-behaviour-track-mcm2-bound.csv":
            selected.append(ctx.project_folder / row["relative_path"])

    mcm_path, _ = find_mcm2_bound(ctx, inventory)
    if mcm_path:
        std = ctx.output_folder / "standardized_inputs" / "MCM2_Bound.csv"
        shutil.copy2(mcm_path, std)
        ctx.log(f"Standardized MCM2_Bound copy created: {std}")

    rows = []
    seen = set()
    for path in selected:
        role = "mcm_bound_control" if path.name.lower() == "single-behaviour-track-mcm2-bound.csv" else None
        for row in rows_from_csv(path, ctx, role_override=role):
            key = (row["protein"], row["source_file"], row["video_id"], row["cell_id"], row["track_id"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)

    fm = pd.DataFrame(rows)
    if fm.empty:
        raise RuntimeError("No usable track rows were found for feature matrix.")
    for col in IDENTITY_COLUMNS:
        if col not in fm.columns:
            fm[col] = ""
    fm.to_csv(ctx.output_folder / "feature_matrix_tracks.csv", index=False)

    feature_rows = []
    for col in fm.columns:
        if col in IDENTITY_COLUMNS:
            continue
        feature_rows.append({"feature": col, "dtype": str(fm[col].dtype), "description": "Extracted or aggregated track feature"})
    pd.DataFrame(feature_rows).to_csv(ctx.output_folder / "feature_dictionary.csv", index=False)
    missing = fm.isna().mean().reset_index()
    missing.columns = ["column", "missing_fraction"]
    missing.to_csv(ctx.output_folder / "feature_missingness_report.csv", index=False)
    fm.groupby(["protein", "dataset_name", "control_role"], dropna=False).size().reset_index(name="n_tracks").to_csv(
        ctx.output_folder / "track_count_by_dataset.csv", index=False
    )
    return fm


def preprocess_features(fm: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], Dict[str, object]]:
    numeric_cols = [c for c in fm.columns if c not in IDENTITY_COLUMNS and pd.api.types.is_numeric_dtype(fm[c])]
    controls = fm["control_role"].isin(["free_like_control", "chromatin_bound_control", "mcm_bound_control"])
    keep = []
    for col in numeric_cols:
        if fm.loc[controls, col].notna().mean() >= 0.30 and fm.loc[controls, col].nunique(dropna=True) > 1:
            keep.append(col)
    if not keep:
        raise RuntimeError("No usable numeric features after missingness and variance filtering.")
    train = fm.loc[controls, keep].apply(pd.to_numeric, errors="coerce")
    med = train.median()
    mean = train.fillna(med).mean()
    std = train.fillna(med).std().replace(0, 1).fillna(1)
    z = fm[keep].apply(pd.to_numeric, errors="coerce").fillna(med)
    z = (z - mean) / std
    return z, keep, {"median": med, "mean": mean, "std": std}


def run_models(ctx: RunContext, fm: pd.DataFrame) -> pd.DataFrame:
    z, features, prep = preprocess_features(fm)
    controls = fm["control_role"].isin(["free_like_control", "chromatin_bound_control", "mcm_bound_control"])
    y = fm.loc[controls, "control_role"].astype(str)
    x_train = z.loc[controls]
    if y.nunique() < 3:
        raise RuntimeError("Need NLS, H2B, and MCM2_Bound controls for model training.")

    class_map = {
        "free_like_control": "free_like",
        "chromatin_bound_control": "chromatin_bound_like",
        "mcm_bound_control": "mcm_bound_like",
    }
    prob_df = pd.DataFrame(index=fm.index)
    pred = pd.Series("ambiguous", index=fm.index)

    rf = None
    if RandomForestClassifier is not None:
        rf = RandomForestClassifier(n_estimators=300, random_state=ctx.random_seed, class_weight="balanced")
        rf.fit(x_train, y)
        probs = rf.predict_proba(z)
        for cls, idx in zip(rf.classes_, range(len(rf.classes_))):
            prob_df[class_map[cls]] = probs[:, idx]
        pred = pd.Series(rf.predict(z), index=fm.index).map(class_map)
        pd.DataFrame({"feature": features, "importance": rf.feature_importances_}).sort_values(
            "importance", ascending=False
        ).to_csv(ctx.output_folder / "feature_importance_random_forest.csv", index=False)
    else:
        for role, label in class_map.items():
            prob_df[label] = 1.0 / 3.0

    if LogisticRegression is not None:
        lr = LogisticRegression(max_iter=2000, class_weight="balanced", multi_class="auto")
        lr.fit(x_train, y)
        coef_rows = []
        for cls, coefs in zip(lr.classes_, lr.coef_):
            for feature, coef in zip(features, coefs):
                coef_rows.append({"class": cls, "feature": feature, "coefficient": coef})
        pd.DataFrame(coef_rows).to_csv(ctx.output_folder / "logistic_regression_coefficients.csv", index=False)

    centroids = {}
    for role in class_map:
        centroids[role] = z.loc[fm["control_role"].eq(role)].mean()
    centroid_df = pd.DataFrame(centroids).T
    centroid_df.to_csv(ctx.output_folder / "control_centroids.csv")

    distance_cols = {}
    for role, centroid in centroids.items():
        distance_cols[f"distance_to_{class_map[role].replace('_like', '').replace('chromatin_bound', 'H2B').replace('free', 'NLS').replace('mcm_bound', 'MCM2_Bound')}_centroid"] = np.sqrt(
            ((z - centroid) ** 2).sum(axis=1)
        )
    dist = pd.DataFrame(distance_cols)
    dist["nearest_control_class"] = dist.idxmin(axis=1).str.replace("distance_to_", "", regex=False).str.replace(
        "_centroid", "", regex=False
    )
    dist["nearest_control_distance"] = dist[distance_cols.keys()].min(axis=1)
    dist["control_outlier_score"] = dist["nearest_control_distance"]
    dist.to_csv(ctx.output_folder / "distance_to_controls.csv", index=False)

    if IsolationForest is not None:
        iso = IsolationForest(random_state=ctx.random_seed, contamination="auto")
        iso.fit(x_train)
        outlier_score = -iso.score_samples(z)
    else:
        outlier_score = dist["control_outlier_score"].to_numpy()
    anomaly = pd.DataFrame({"control_outlier_score": outlier_score})
    threshold = float(np.nanpercentile(outlier_score[controls], 95))
    anomaly["is_control_outlier"] = anomaly["control_outlier_score"] > threshold
    anomaly.to_csv(ctx.output_folder / "anomaly_model_scores.csv", index=False)

    metrics_rows = []
    cm = pd.DataFrame()
    if RandomForestClassifier is not None and min(y.value_counts()) >= 2:
        splits = min(5, int(min(y.value_counts())))
        cv = StratifiedKFold(n_splits=splits, shuffle=True, random_state=ctx.random_seed)
        cv_pred = cross_val_predict(rf, x_train, y, cv=cv)
        metrics_rows.append({"metric": "accuracy", "value": accuracy_score(y, cv_pred)})
        metrics_rows.append({"metric": "balanced_accuracy", "value": balanced_accuracy_score(y, cv_pred)})
        report = classification_report(y, cv_pred, output_dict=True, zero_division=0)
        for cls, vals in report.items():
            if isinstance(vals, dict):
                for metric, value in vals.items():
                    metrics_rows.append({"metric": f"{cls}_{metric}", "value": value})
        cm = pd.DataFrame(confusion_matrix(y, cv_pred, labels=sorted(y.unique())), index=sorted(y.unique()), columns=sorted(y.unique()))
    else:
        metrics_rows.append({"metric": "cross_validation_skipped", "value": 1})
    pd.DataFrame(metrics_rows).to_csv(ctx.output_folder / "control_classifier_metrics.csv", index=False)
    cm.to_csv(ctx.output_folder / "control_classifier_confusion_matrix.csv")

    out = fm[IDENTITY_COLUMNS].copy()
    out["P_free_like"] = prob_df.get("free_like", 1 / 3)
    out["P_chromatin_bound_like"] = prob_df.get("chromatin_bound_like", 1 / 3)
    out["P_mcm_bound_like"] = prob_df.get("mcm_bound_like", 1 / 3)
    out["supervised_control_prediction"] = pred
    out = pd.concat([out, dist, anomaly[["is_control_outlier"]]], axis=1)
    out.to_csv(ctx.output_folder / "control_model_predictions.csv", index=False)

    if joblib is not None:
        joblib.dump({"features": features, "preprocessing": prep, "random_forest": rf}, ctx.output_folder / "trained_models" / "control_models.joblib")
    return out


def final_classification(ctx: RunContext, fm: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    merged = pd.concat([pred.copy(), fm.drop(columns=[c for c in pred.columns if c in fm.columns], errors="ignore")], axis=1)
    for col in ["trapping_score", "temporal_score", "trap_prob_mean", "max_trap_dwell_frames", "n_supported_high_score_windows", "frac_diffusive", "max_consecutive_diffusive"]:
        if col not in merged.columns:
            merged[col] = np.nan

    nls = merged["control_role"].eq("free_like_control")
    trap_threshold = float(np.nanpercentile(merged.loc[nls, "trapping_score"].dropna(), 95)) if merged.loc[nls, "trapping_score"].notna().any() else np.nan
    nls_frac = merged.loc[nls, "frac_diffusive"].dropna()
    diff_threshold = min(0.50, float(np.nanpercentile(nls_frac, 75))) if not nls_frac.empty else 0.50
    outlier_threshold = float(np.nanpercentile(merged.loc[merged["is_control"].astype(bool), "control_outlier_score"].dropna(), 95))

    classes = []
    reasons = []
    temporal_flags = []
    for _, row in merged.iterrows():
        temporal = (
            (not pd.isna(row["trapping_score"]) and (pd.isna(trap_threshold) or row["trapping_score"] > trap_threshold))
            and (
                (not pd.isna(row["trap_prob_mean"]) and row["trap_prob_mean"] >= 0.30)
                or (not pd.isna(row["max_trap_dwell_frames"]) and row["max_trap_dwell_frames"] >= 4)
                or (not pd.isna(row["n_supported_high_score_windows"]) and row["n_supported_high_score_windows"] >= 1)
            )
        )
        temporal_flags.append(bool(temporal))
        burst = (
            not pd.isna(row["max_consecutive_diffusive"])
            and not pd.isna(row["frac_diffusive"])
            and row["max_consecutive_diffusive"] >= 3
            and row["frac_diffusive"] >= diff_threshold
        )
        is_target = row["protein"] in ["TDP43", "NONO"]
        outlier = bool(row["control_outlier_score"] > outlier_threshold)
        probs = {
            "free_like": row["P_free_like"],
            "chromatin_bound_like": row["P_chromatin_bound_like"],
            "mcm_bound_like": row["P_mcm_bound_like"],
        }
        best = max(probs, key=lambda k: probs[k] if not pd.isna(probs[k]) else -1)
        if row["control_role"] == "free_like_control" or (best == "free_like" and probs[best] >= 0.60 and not temporal):
            klass = "free_like"
            reason = "High free-like control probability or NLS control role; classified as free_like."
        elif row["control_role"] == "chromatin_bound_control" or (best == "chromatin_bound_like" and probs[best] >= 0.60 and not outlier):
            klass = "chromatin_bound_like"
            reason = "Nearest/supervised behavior is H2B-like without target-specific outlier evidence."
        elif row["control_role"] == "mcm_bound_control" or (best == "mcm_bound_like" and probs[best] >= 0.60 and not outlier):
            klass = "mcm_bound_like"
            reason = "Nearest/supervised behavior is MCM2_Bound-like without target-specific outlier evidence."
        elif temporal and burst:
            klass = "mixed"
            reason = "Temporal trapping evidence present but diffusive-burst flag is true; classified as mixed."
        elif is_target and temporal and outlier:
            klass = "target_specific_trapping_like"
            reason = "Target track is temporally supported and a control-landscape outlier not explained by the main control-like rules."
        elif not temporal and not pd.isna(row.get("trapping_score", np.nan)):
            klass = "slow_diffusive"
            reason = "Slow or confined features lack required temporal trapping support; classified as slow_diffusive."
        else:
            klass = "ambiguous"
            reason = "Insufficient or conflicting evidence for a specific control-guided class."
        classes.append(klass)
        reasons.append(reason)

    merged["supported_temporal_trapping"] = temporal_flags
    merged["diffusive_burst_flag"] = (
        (merged["max_consecutive_diffusive"] >= 3) & (merged["frac_diffusive"] >= diff_threshold)
    ).fillna(False)
    merged["final_control_guided_class"] = classes
    merged["classification_reason"] = reasons
    merged["is_control_outlier"] = merged["control_outlier_score"] > outlier_threshold
    merged.to_csv(ctx.output_folder / "final_control_guided_track_classification.csv", index=False)
    ctx.log(f"NLS trapping threshold: {trap_threshold}")
    ctx.log(f"Diffusive fraction threshold: {diff_threshold}")
    ctx.log(f"Control outlier threshold: {outlier_threshold}")
    return merged


def write_summaries(ctx: RunContext, final: pd.DataFrame) -> None:
    for group_col, out_name in [
        ("dataset_name", "summary_by_dataset.csv"),
        ("protein", "summary_by_protein.csv"),
        ("condition", "summary_by_condition.csv"),
        ("replicate", "summary_by_replicate.csv"),
    ]:
        rows = []
        for key, grp in final.groupby(group_col, dropna=False):
            row = {group_col: key, "total_tracks": len(grp)}
            counts = grp["final_control_guided_class"].value_counts()
            for klass in FINAL_CLASSES:
                row[f"n_{klass}"] = int(counts.get(klass, 0))
                row[f"frac_{klass}"] = float(counts.get(klass, 0) / len(grp)) if len(grp) else 0.0
            for col in ["trapping_score", "temporal_score", "max_trap_dwell_frames", "control_outlier_score"]:
                row[f"median_{col}"] = float(pd.to_numeric(grp[col], errors="coerce").median()) if col in grp else math.nan
            rows.append(row)
        pd.DataFrame(rows).to_csv(ctx.output_folder / out_name, index=False)

    final.groupby(["protein", "condition", "replicate", "final_control_guided_class"], dropna=False).size().reset_index(
        name="n_tracks"
    ).to_csv(ctx.output_folder / "replicate_level_class_fractions.csv", index=False)

    if "n_frames" in final:
        final.groupby(["dataset_name", "final_control_guided_class"], dropna=False)["n_frames"].sum().reset_index().to_csv(
            ctx.output_folder / "summary_frames_by_dataset.csv", index=False
        )

    easy = ctx.output_folder / "easy_interpretation"
    summary = pd.read_csv(ctx.output_folder / "summary_by_protein.csv")
    summary.to_csv(easy / "simplified_results_table.csv", index=False)
    try:
        summary.to_excel(easy / "simplified_results_table.xlsx", index=False)
    except Exception as exc:
        ctx.log(f"WARNING: could not write XLSX simplified table: {exc}")
    (easy / "EXECUTIVE_SUMMARY.md").write_text(
        "# Executive Summary\n\n"
        "This control-guided analysis compares target-protein track dynamics against NLS, H2B, and MCM2_Bound controls. "
        "The results identify candidate target-specific trapping-like dynamics, not definitive condensate localization.\n\n"
        "NLS was used as the free-like nuclear mobility control, H2B as the chromatin-bound confinement control, "
        "and MCM2_Bound as the replication/chromatin-associated bound-motion control.\n",
        encoding="utf-8",
    )
    (easy / "target_vs_control_interpretation.md").write_text(
        "# Target vs Control Interpretation\n\nUse cautious language: tracks classified as target-specific trapping-like are candidates whose dynamics are not explained by the three controls.\n",
        encoding="utf-8",
    )
    (easy / "key_findings_bullets.md").write_text("# Key Findings\n\n- See `summary_by_protein.csv` for class fractions by protein.\n", encoding="utf-8")
    (easy / "figure_readme.md").write_text("# Figure README\n\nFigures are generated when plotting dependencies and sufficient data are available.\n", encoding="utf-8")


def write_plots(ctx: RunContext, final: pd.DataFrame) -> None:
    if plt is None:
        ctx.log("WARNING: matplotlib unavailable; plots skipped")
        return
    plots = ctx.output_folder / "plots"
    easy = ctx.output_folder / "easy_interpretation"
    for group_col, name in [("dataset_name", "final_class_by_dataset"), ("protein", "final_class_percent_by_protein")]:
        table = pd.crosstab(final[group_col], final["final_control_guided_class"], normalize="index") * 100
        ax = table.plot(kind="bar", stacked=True, figsize=(10, 5))
        ax.set_ylabel("Percent tracks")
        ax.figure.tight_layout()
        for folder in [plots, easy if group_col == "protein" else plots]:
            ax.figure.savefig(folder / f"{name}.png", dpi=200)
            ax.figure.savefig(folder / f"{name}.pdf")
        plt.close(ax.figure)

    target_frac = (
        final.assign(
            is_target_specific=final["final_control_guided_class"].eq("target_specific_trapping_like").astype(float)
        )
        .groupby("protein", dropna=False)["is_target_specific"]
        .mean()
        .mul(100)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    target_frac.plot(kind="bar", ax=ax, color="#4C78A8")
    ax.set_ylabel("Percent target-specific trapping-like")
    ax.set_xlabel("Protein")
    ax.set_ylim(0, max(5, float(target_frac.max()) * 1.2 if len(target_frac) else 5))
    fig.tight_layout()
    fig.savefig(easy / "target_specific_trapping_percent_by_protein.png", dpi=200)
    fig.savefig(easy / "target_specific_trapping_percent_by_protein.pdf")
    plt.close(fig)

    prob_cols = ["P_free_like", "P_chromatin_bound_like", "P_mcm_bound_like"]
    if all(col in final.columns for col in prob_cols):
        heat = final.groupby("protein", dropna=False)[prob_cols].mean()
        fig, ax = plt.subplots(figsize=(8, max(3, 0.45 * len(heat))))
        im = ax.imshow(heat.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
        ax.set_xticks(range(len(prob_cols)))
        ax.set_xticklabels(prob_cols, rotation=30, ha="right")
        ax.set_yticks(range(len(heat.index)))
        ax.set_yticklabels(heat.index)
        fig.colorbar(im, ax=ax, label="Mean probability")
        fig.tight_layout()
        fig.savefig(easy / "control_similarity_heatmap.png", dpi=200)
        fig.savefig(easy / "control_similarity_heatmap.pdf")
        plt.close(fig)

    if "trapping_score" in final.columns and final["trapping_score"].notna().any():
        fig, ax = plt.subplots(figsize=(9, 4))
        groups = [
            pd.to_numeric(group["trapping_score"], errors="coerce").dropna().values
            for _, group in final.groupby("protein", dropna=False)
        ]
        labels = [str(name) for name, _ in final.groupby("protein", dropna=False)]
        ax.boxplot(groups, labels=labels, showfliers=False)
        ax.set_ylabel("Trapping score")
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        fig.savefig(easy / "trapping_score_controls_vs_targets.png", dpi=200)
        fig.savefig(easy / "trapping_score_controls_vs_targets.pdf")
        fig.savefig(plots / "trapping_score_by_protein.png", dpi=200)
        fig.savefig(plots / "trapping_score_by_protein.pdf")
        plt.close(fig)
    else:
        ctx.log("WARNING: trapping_score_controls_vs_targets plot skipped because trapping_score is unavailable.")

    flow_counts = {
        "all_tracks": len(final),
        "temporal_support": int(final.get("supported_temporal_trapping", pd.Series(False, index=final.index)).sum()),
        "diffusive_burst_flag": int(final.get("diffusive_burst_flag", pd.Series(False, index=final.index)).sum()),
        "control_outlier": int(final.get("is_control_outlier", pd.Series(False, index=final.index)).sum()),
        "target_specific": int(final["final_control_guided_class"].eq("target_specific_trapping_like").sum()),
    }
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(flow_counts.keys(), flow_counts.values(), color=["#4C78A8", "#72B7B2", "#F58518", "#54A24B", "#B279A2"])
    ax.set_ylabel("Track count")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(easy / "decision_flow_summary.png", dpi=200)
    fig.savefig(easy / "decision_flow_summary.pdf")
    plt.close(fig)


def write_run_summary(ctx: RunContext, status: str, notes: Sequence[str]) -> None:
    lines = [
        "# Control-Guided Condensate Classification Run Summary",
        "",
        f"Status: {status}",
        f"Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"Project folder: `{ctx.project_folder}`",
        f"Output folder: `{ctx.output_folder}`",
        f"Dry run: {ctx.dry_run}",
        "",
        "## Notes",
        "",
    ]
    lines.extend([f"- {note}" for note in notes])
    lines.extend(
        [
            "",
            "## Rerun Commands",
            "",
            "```bash",
            f"python control_guided_condensate_classification.py --project-folder \"{ctx.project_folder}\" --dry-run",
            f"python control_guided_condensate_classification.py --project-folder \"{ctx.project_folder}\"",
            "```",
        ]
    )
    (ctx.output_folder / "RUN_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def run_full(ctx: RunContext, inventory: pd.DataFrame) -> int:
    mcm_path, _ = find_mcm2_bound(ctx, inventory)
    if not mcm_path:
        write_run_summary(ctx, "FAILED", ["Required MCM2_Bound file was not found."])
        return 2
    fm = build_feature_matrix(ctx, inventory)
    pred = run_models(ctx, fm)
    final = final_classification(ctx, fm, pred)
    bad_classes = sorted(set(final["final_control_guided_class"]) - set(FINAL_CLASSES))
    if bad_classes:
        write_run_summary(ctx, "FAILED", [f"Invalid final classes found: {bad_classes}"])
        return 3
    if final["classification_reason"].isna().any() or final["classification_reason"].eq("").any():
        write_run_summary(ctx, "FAILED", ["At least one row has an empty classification_reason."])
        return 3
    write_summaries(ctx, final)
    write_plots(ctx, final)
    write_run_summary(
        ctx,
        "PASS",
        [
            "Feature matrix, model predictions, final classifications, summaries, and interpretation files were generated.",
            "TDP43 and NONO were not used for model fitting; only NLS, H2B, and MCM2_Bound controls were used.",
            "MCM2_Bound was standardized from the manually prepared single-behaviour MCM2 bound file.",
        ],
    )
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Control-guided condensate track classification")
    parser.add_argument("--project-folder", required=True)
    parser.add_argument("--output-folder", default="")
    parser.add_argument("--window-size", type=int, default=11)
    parser.add_argument("--random-seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--nls-name", default="NLS")
    parser.add_argument("--h2b-name", default="H2B")
    parser.add_argument("--mcm-bound-file", default="")
    parser.add_argument("--target-names", default="TDP43,NONO")
    parser.add_argument("--min-feature-nonmissing", type=float, default=0.30)
    parser.add_argument("--probability-threshold", type=float, default=0.60)
    parser.add_argument("--nls-quantile", type=float, default=0.95)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    ctx = make_context(args)
    try:
        inventory = discover_files(ctx)
        code = dry_run(ctx, inventory) if args.dry_run else run_full(ctx, inventory)
        ctx.log(f"Finished with exit code {code}")
        return code
    except Exception as exc:
        ctx.log(f"ERROR: {exc}")
        write_run_summary(ctx, "FAILED", [str(exc)])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
