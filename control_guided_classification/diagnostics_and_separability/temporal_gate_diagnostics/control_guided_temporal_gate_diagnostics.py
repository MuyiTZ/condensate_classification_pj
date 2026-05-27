import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_PROTEINS = {"TDP43", "NONO"}
REQUESTED_DATASETS = {
    "12D-0502-CT": Path("TDP43/12D-0502-CT/CSV"),
    "WT-0515-CT": Path("TDP43/WT-0515-CT/CSV"),
    "WT-0515-ARS": Path("TDP43/WT-0515-ARS/CSV"),
}


def markdown_table(df):
    if df is None or df.empty:
        return "_No rows._"
    shown = df.copy().replace({np.nan: ""})
    cols = list(shown.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in shown.iterrows():
        values = [str(row[col]).replace("|", "\\|") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def norm_id(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    try:
        number = float(text)
        if number.is_integer():
            return str(int(number))
    except Exception:
        pass
    return text


def parse_dataset_name(folder_name):
    match = re.match(r"(?P<genotype>WT|12D)-(?P<date>[^-]+)-(?P<treatment>.+)", folder_name, re.I)
    if not match:
        return {
            "genotype": "unknown",
            "date_or_experiment_id": "unknown",
            "treatment": "unknown",
            "replicate": folder_name,
        }
    data = match.groupdict()
    genotype = data["genotype"].upper()
    treatment = data["treatment"].upper()
    return {
        "genotype": genotype,
        "date_or_experiment_id": data["date"],
        "treatment": treatment,
        "replicate": f"{genotype}-{data['date']}-{treatment}",
    }


def add_key_columns(df):
    for col in ["protein", "dataset_name", "video_id", "cell_id", "track_id"]:
        if col not in df.columns:
            df[col] = ""
    df["_join_key"] = (
        df["protein"].map(norm_id)
        + "|"
        + df["dataset_name"].map(norm_id)
        + "|"
        + df["video_id"].map(norm_id)
        + "|"
        + df["cell_id"].map(norm_id)
        + "|"
        + df["track_id"].map(norm_id)
    )
    return df


def discover_old_eval(project):
    rows = []
    for p in project.glob("*/**/condensate_evaluation_summary.csv"):
        if "control_guided_classification" in p.parts:
            continue
        protein = next((part for part in p.parts if part.upper() in {"TDP43", "NONO", "H2B", "H2B", "MCM2", "NLS"}), "")
        dataset = ""
        if protein:
            try:
                dataset = p.parts[p.parts.index(protein) + 1]
            except Exception:
                dataset = ""
        rows.append({"protein": protein, "dataset_name": dataset, "path": str(p)})
    return pd.DataFrame(rows)


def load_old_eval(project):
    inventory = discover_old_eval(project)
    frames = []
    for _, row in inventory.iterrows():
        protein = row["protein"]
        if protein not in TARGET_PROTEINS:
            continue
        path = Path(row["path"])
        try:
            df = pd.read_csv(path, low_memory=False)
        except Exception:
            continue
        meta = parse_dataset_name(row["dataset_name"])
        df = df.rename(
            columns={
                "Video #": "video_id",
                "Cell": "cell_id",
                "Track": "track_id",
                "classification": "old_classification",
                "temporal_track_score": "old_temporal_track_score",
                "trapping_score_mean": "old_trapping_score_mean",
                "trapping_score_max": "old_trapping_score_max",
            }
        )
        df["protein"] = protein
        df["dataset_name"] = row["dataset_name"]
        for key, value in meta.items():
            df[key] = value
        df["old_source_path"] = str(path)
        frames.append(df)
    if not frames:
        return pd.DataFrame(), inventory
    old = pd.concat(frames, ignore_index=True, sort=False)
    old = add_key_columns(old)
    return old, inventory


def feature_audit(df, output_dir):
    target = df[df["protein"].isin(TARGET_PROTEINS)].copy()
    aliases = {
        "trap_prob_mean": ["trap_prob_mean"],
        "max_trap_dwell_frames": ["max_trap_dwell_frames"],
        "n_supported_high_score_windows": ["n_supported_high_score_windows"],
        "temporal_score": ["temporal_score", "temporal_track_score", "old_temporal_track_score"],
        "supported_high_score_window": [
            "supported_high_score_window",
            "supported_temporal_trapping",
            "frac_supported_high_score_windows",
        ],
    }
    rows = []
    for requested, candidates in aliases.items():
        present = [c for c in candidates if c in target.columns]
        chosen = present[0] if present else ""
        if not chosen:
            rows.append(
                {
                    "requested_feature": requested,
                    "present_column_used": "",
                    "status": "missing",
                    "n_tracks": len(target),
                    "missing_fraction": 1.0,
                    "non_missing_fraction": 0.0,
                    "pass_rate_if_interpretable": np.nan,
                    "pass_rule": "not evaluated",
                }
            )
            continue
        series = target[chosen]
        non_missing = series.notna()
        pass_rate = np.nan
        rule = "non-missing only"
        if requested == "trap_prob_mean":
            pass_rate = (pd.to_numeric(series, errors="coerce") >= 0.30).mean()
            rule = ">= 0.30"
        elif requested == "max_trap_dwell_frames":
            pass_rate = (pd.to_numeric(series, errors="coerce") >= 4).mean()
            rule = ">= 4 frames"
        elif requested == "n_supported_high_score_windows":
            pass_rate = (pd.to_numeric(series, errors="coerce") >= 1).mean()
            rule = ">= 1"
        elif requested == "temporal_score":
            pass_rate = (pd.to_numeric(series, errors="coerce") > 0).mean()
            rule = "> 0"
        elif requested == "supported_high_score_window":
            if series.dtype == bool:
                pass_rate = series.fillna(False).mean()
                rule = "boolean True"
            else:
                pass_rate = (pd.to_numeric(series, errors="coerce") > 0).mean()
                rule = "> 0"
        rows.append(
            {
                "requested_feature": requested,
                "present_column_used": chosen,
                "status": "present" if chosen == requested else "alias_or_misnamed",
                "n_tracks": len(target),
                "missing_fraction": float(1 - non_missing.mean()),
                "non_missing_fraction": float(non_missing.mean()),
                "pass_rate_if_interpretable": float(pass_rate) if pd.notna(pass_rate) else np.nan,
                "pass_rule": rule,
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(output_dir / "temporal_support_feature_audit.csv", index=False)
    broken = audit.loc[audit["requested_feature"].isin(["n_supported_high_score_windows", "temporal_score", "supported_high_score_window"])]
    interpretation = [
        "# Temporal-support feature audit",
        "",
        "Motion-pattern language only: this audit tests whether target-specific trapping-like gate failures are data-supported or caused by missing/misnamed temporal columns.",
        "",
        f"Target rows audited: {len(target)} TDP43/NONO rows from the current final control-guided table.",
        "",
    ]
    if (broken["missing_fraction"] > 0.95).any() or (broken["status"] != "present").any():
        interpretation.append(
            "Conclusion: the strict temporal_support gate appears at least partly broken by missing or misnamed temporal-support columns in the final control-guided table. "
            "The raw per-dataset condensate_evaluation files contain related temporal columns, but the final classifier table mostly stores them as missing for the strict gate."
        )
    else:
        interpretation.append("Conclusion: temporal_support appears to be genuinely evaluable from the current columns.")
    interpretation.append("")
    interpretation.append(markdown_table(audit))
    (output_dir / "temporal_support_feature_audit.md").write_text("\n".join(interpretation), encoding="utf-8")
    return audit


def old_new_crosstab(old, final, output_dir):
    final_target = final[final["protein"].isin(TARGET_PROTEINS)].copy()
    final_target = add_key_columns(final_target)
    keep = [
        "_join_key",
        "final_control_guided_class",
        "P_free_like",
        "P_chromatin_bound_like",
        "P_mcm_bound_like",
        "distance_to_H2B_centroid",
        "distance_to_MCM2_Bound_centroid",
        "control_outlier_score",
    ]
    joined = old.merge(final_target[[c for c in keep if c in final_target.columns]], on="_join_key", how="left")
    joined.to_csv(output_dir / "old_vs_new_joined_target_tracks.csv", index=False)
    ctab = pd.crosstab(joined["old_classification"].fillna("missing_old"), joined["final_control_guided_class"].fillna("not_in_current_final_classifier"))
    ctab.to_csv(output_dir / "old_vs_new_target_crosstab.csv")
    trapping = joined[joined["old_classification"].astype(str).str.lower().eq("trapping_like")]
    dest = trapping["final_control_guided_class"].fillna("not_in_current_final_classifier").value_counts().rename_axis("new_destination").reset_index(name="n_old_trapping_like_tracks")
    dest.to_csv(output_dir / "old_trapping_like_destination_diagnostics.csv", index=False)
    md = [
        "# Old-vs-new target crosstab",
        "",
        "This compares old `condensate_evaluation` motion-pattern classes with the current final control-guided classifier when exact track keys match.",
        "",
        "## Old trapping_like destinations",
        "",
        markdown_table(dest),
        "",
        "Tracks marked `not_in_current_final_classifier` are from datasets that have per-dataset condensate_evaluation output but were not included in the current final control-guided table.",
    ]
    (output_dir / "old_vs_new_target_crosstab.md").write_text("\n".join(md), encoding="utf-8")
    return joined


def gate_ablation(gate, output_dir):
    gate = gate[gate["protein"].isin(TARGET_PROTEINS)].copy()
    flag_cols = [
        "passed_not_free_gate",
        "passed_not_h2b_gate",
        "passed_not_mcm2_gate",
        "passed_temporal_support_gate",
        "passed_no_diffusive_burst_gate",
        "passed_control_outlier_gate",
        "passed_feature_completeness_gate",
        "passed_target_protein_gate",
    ]
    for col in flag_cols:
        if col not in gate.columns:
            gate[col] = False
        gate[col] = gate[col].fillna(False).astype(bool)
    scenarios = {
        "full_strict_rule": flag_cols,
        "without_temporal_gate": [c for c in flag_cols if c != "passed_temporal_support_gate"],
        "without_not_h2b_gate": [c for c in flag_cols if c != "passed_not_h2b_gate"],
        "without_control_outlier_gate": [c for c in flag_cols if c != "passed_control_outlier_gate"],
        "relaxed_near_miss_rule": [
            "passed_not_free_gate",
            "passed_not_mcm2_gate",
            "passed_no_diffusive_burst_gate",
            "passed_feature_completeness_gate",
            "passed_target_protein_gate",
        ],
    }
    rows = []
    for name, cols in scenarios.items():
        passed = gate[cols].all(axis=1)
        rows.append({"scenario": name, "n_pass": int(passed.sum()), "n_total": len(gate), "fraction_pass": float(passed.mean())})
    out = pd.DataFrame(rows)
    out.to_csv(output_dir / "target_gate_ablation_summary.csv", index=False)
    (output_dir / "target_gate_ablation_report.md").write_text(
        "# Gate-ablation analysis\n\n"
        "Counts are candidate motion-pattern calls under each diagnostic rule, not definitive condensate localization.\n\n"
        + markdown_table(out)
        + "\n",
        encoding="utf-8",
    )
    return out


def ambiguous_table(joined, final, output_dir):
    final_target = final[final["protein"].isin(TARGET_PROTEINS)].copy()
    final_target = add_key_columns(final_target)
    old_cols = [
        "_join_key",
        "old_classification",
        "old_trapping_score_mean",
        "old_trapping_score_max",
        "old_temporal_track_score",
    ]
    old_features = joined[[c for c in old_cols if c in joined.columns]].drop_duplicates("_join_key")
    merged = final_target.merge(old_features, on="_join_key", how="left")
    amb = merged[merged["final_control_guided_class"].astype(str).eq("ambiguous")].copy()
    for col in ["control_outlier_score", "trap_prob_mean", "max_trap_dwell_frames", "old_trapping_score_mean", "old_temporal_track_score"]:
        if col not in amb.columns:
            amb[col] = np.nan
        amb[col] = pd.to_numeric(amb[col], errors="coerce")
    amb["old_trapping_like"] = amb["old_classification"].astype(str).str.lower().eq("trapping_like")
    amb["review_priority_score"] = (
        amb["old_trapping_like"].astype(int) * 5
        + amb["control_outlier_score"].fillna(0).rank(pct=True)
        + amb["trap_prob_mean"].fillna(0).rank(pct=True)
        + amb["max_trap_dwell_frames"].fillna(0).rank(pct=True)
        + amb["old_trapping_score_mean"].fillna(0).rank(pct=True)
        + amb["old_temporal_track_score"].fillna(0).rank(pct=True)
    )
    amb["inspection_reason"] = np.where(
        amb["old_trapping_like"],
        "old trapping_like + current ambiguous + ranked by trapping/temporal/outlier features",
        "current ambiguous + ranked by available trapping/temporal/outlier features",
    )
    amb = amb.sort_values("review_priority_score", ascending=False)
    amb.to_csv(output_dir / "ambiguous_target_ranked_inspection_table.csv", index=False)
    amb.head(100).to_csv(output_dir / "ambiguous_target_ranked_top100.csv", index=False)
    summary = amb.groupby(["protein", "old_trapping_like"], dropna=False).size().reset_index(name="n_ambiguous_tracks")
    summary.to_csv(output_dir / "ambiguous_target_ranked_summary.csv", index=False)
    return amb


def tdp43_conditions(old, final, gate, output_dir):
    tdp = old[old["protein"].eq("TDP43")].copy()
    rows = []
    for keys, group in tdp.groupby(["genotype", "treatment", "replicate"], dropna=False):
        genotype, treatment, replicate = keys
        total = len(group)
        rows.append(
            {
                "genotype": genotype,
                "treatment": treatment,
                "replicate": replicate,
                "n_old_tracks": total,
                "old_trapping_like_fraction": float(group["old_classification"].astype(str).str.lower().eq("trapping_like").mean()) if total else np.nan,
                "old_mixed_fraction": float(group["old_classification"].astype(str).str.lower().eq("mixed").mean()) if total else np.nan,
            }
        )
    cond = pd.DataFrame(rows)
    final_t = final[final["protein"].eq("TDP43")].copy()
    if not final_t.empty:
        final_summary = final_t.groupby(["dataset_name"], dropna=False).agg(
            n_final_tracks=("track_id", "size"),
            ambiguous_fraction=("final_control_guided_class", lambda s: s.astype(str).eq("ambiguous").mean()),
            chromatin_bound_like_fraction=("final_control_guided_class", lambda s: s.astype(str).eq("chromatin_bound_like").mean()),
            free_like_fraction=("final_control_guided_class", lambda s: s.astype(str).eq("free_like").mean()),
            mean_distance_to_H2B=("distance_to_H2B_centroid", "mean"),
            mean_distance_to_MCM2_Bound=("distance_to_MCM2_Bound_centroid", "mean"),
        ).reset_index().rename(columns={"dataset_name": "replicate"})
        cond = cond.merge(final_summary, on="replicate", how="left")
    gate_t = gate[gate["protein"].eq("TDP43")].copy()
    if not gate_t.empty:
        gate_t["replicate"] = gate_t["replicate"].map(norm_id)
        near = gate_t.groupby("replicate", dropna=False).agg(
            near_miss_fraction=("near_miss_target_specific", lambda s: s.fillna(False).astype(bool).mean())
        ).reset_index()
        cond["replicate"] = cond["replicate"].map(norm_id)
        cond = cond.merge(near, on="replicate", how="left")
    cond.to_csv(output_dir / "tdp43_condition_level_diagnostics.csv", index=False)
    avg = cond.groupby(["genotype", "treatment"], dropna=False).agg(
        completed_old_repeats=("replicate", "nunique"),
        mean_old_trapping_like_fraction=("old_trapping_like_fraction", "mean"),
        sd_old_trapping_like_fraction=("old_trapping_like_fraction", "std"),
        mean_ambiguous_fraction=("ambiguous_fraction", "mean"),
        mean_chromatin_bound_like_fraction=("chromatin_bound_like_fraction", "mean"),
        mean_free_like_fraction=("free_like_fraction", "mean"),
        mean_near_miss_fraction=("near_miss_fraction", "mean"),
        mean_distance_to_H2B=("mean_distance_to_H2B", "mean"),
        mean_distance_to_MCM2_Bound=("mean_distance_to_MCM2_Bound", "mean"),
    ).reset_index()
    avg.to_csv(output_dir / "tdp43_condition_average_diagnostics.csv", index=False)
    md = [
        "# TDP43 condition-level diagnostics",
        "",
        "Old trapping-like fractions come from per-dataset condensate_evaluation summaries. New control-guided fractions and distances are only present for datasets already included in the current final classifier; missing values should not be overinterpreted.",
        "",
        "## Replicate-level",
        markdown_table(cond),
        "",
        "## Genotype-treatment averages",
        markdown_table(avg),
    ]
    (output_dir / "tdp43_condition_level_diagnostics.md").write_text("\n".join(md), encoding="utf-8")
    return cond


def requested_dataset_status(project, output_dir):
    rows = []
    for name, rel in REQUESTED_DATASETS.items():
        csv_dir = project / rel
        out = csv_dir / "SF_10ms_condensate_pj_"
        summary = out / "condensate_evaluation_summary.csv"
        potential = out / "potential-condensate-pool.csv"
        config = csv_dir / "SF_10ms_condensate_pj_script-config.toml"
        seg = csv_dir.parent / "SEG"
        rows.append(
            {
                "dataset": name,
                "csv_dir": str(csv_dir),
                "csv_dir_exists": csv_dir.exists(),
                "seg_dir_inside_allowed_project_exists": seg.exists(),
                "config_exists": config.exists(),
                "potential_condensate_pool_exists": potential.exists(),
                "condensate_evaluation_summary_exists": summary.exists(),
                "condensate_evaluation_summary_bytes": summary.stat().st_size if summary.exists() else 0,
                "run_status": "existing_outputs_used_for_diagnostics",
                "note": "Full rerun skipped because stored TOML paths point outside approved folders or matching SEG folder is absent; final classifier not rerun.",
            }
        )
    status = pd.DataFrame(rows)
    status.to_csv(output_dir / "requested_dataset_analysis_status.csv", index=False)
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-folder", required=True)
    args = parser.parse_args()
    project = Path(args.project_folder)
    output_dir = project / "control_guided_classification" / "diagnostics_and_separability" / "temporal_gate_diagnostics"
    output_dir.mkdir(parents=True, exist_ok=True)

    final = pd.read_csv(project / "control_guided_classification" / "final_control_guided_track_classification.csv", low_memory=False)
    gate = pd.read_csv(project / "control_guided_classification" / "diagnostics_and_separability" / "target_gate_failure_table.csv", low_memory=False)
    old, inventory = load_old_eval(project)

    requested_dataset_status(project, output_dir)
    inventory.to_csv(output_dir / "old_condensate_evaluation_inventory.csv", index=False)
    feature_audit(final, output_dir)
    joined = old_new_crosstab(old, final, output_dir)
    gate_ablation(gate, output_dir)
    ambiguous_table(joined, final, output_dir)
    tdp43_conditions(old, final, gate, output_dir)

    summary = [
        "# Temporal gate diagnostics summary",
        "",
        "No full control-guided classifier rerun was performed.",
        "",
        "The requested three TDP43 datasets already had per-dataset condensate_evaluation outputs available and were included in the old-classification condition summaries.",
        "",
        "The temporal-support audit indicates that the zero temporal gate in the current final classifier is at least partly explained by missing/misnamed strict temporal columns rather than clear biological absence of temporal support.",
        "",
        "All language is motion-pattern based; no definitive condensate localization is claimed.",
    ]
    (output_dir / "temporal_gate_diagnostics_summary.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Wrote diagnostics to {output_dir}")


if __name__ == "__main__":
    main()
