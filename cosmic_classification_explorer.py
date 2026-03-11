#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import gzip
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, TextIO, Tuple


MISSENSE_TERMS = {
    "missense_variant",
}

PROTEIN_CHANGING_TERMS = {
    "missense_variant",
    "frameshift_variant",
    "stop_gained",
    "stop_lost",
    "start_lost",
    "inframe_insertion",
    "inframe_deletion",
    "protein_altering_variant",
}

HELP_SKIP_COLUMNS = {
    "COSMIC_PHENOTYPE_ID",
    "NCI_CODE",
    "EFO",
}


def open_text(path: Path, mode: str = "rt") -> TextIO:
    """
    Open plain text or gzipped text transparently.
    """
    if path.suffix == ".gz":
        return gzip.open(path, mode, encoding="utf-8", newline="")
    return open(path, mode, encoding="utf-8", newline="")


def norm(x: Optional[str]) -> str:
    """
    Normalize a cell value by stripping whitespace.
    """
    return (x or "").strip()


def parse_mutation_description(desc: Optional[str]) -> Set[str]:
    """
    Split MUTATION_DESCRIPTION into normalized consequence terms.

    COSMIC may contain one or more comma-separated terms, for example:
        missense_variant
        missense_variant,splice_region_variant
        frameshift_variant,stop_gained
    """
    raw = norm(desc).lower()
    if not raw:
        return set()

    return {term.strip() for term in raw.split(",") if term.strip()}


def load_rows(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Load the TSV file into memory.
    Returns rows and fieldnames.
    """
    with open_text(path, "rt") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    return rows, fieldnames


def parse_condition(expr: str) -> Tuple[str, str, str]:
    """
    Parse a filter condition.

    Supported formats:
        COL=value
        COL!=value
        COL~regex
        COL!~regex
    """
    for op in ("!~", "!=", "~", "="):
        if op in expr:
            col, value = expr.split(op, 1)
            return col.strip(), op, value.strip()

    raise ValueError(
        f"Invalid condition: {expr}. Use COL=value, COL!=value, COL~regex or COL!~regex"
    )


def build_predicate(conditions: List[str], valid_columns: List[str]):
    """
    Build a row-filtering predicate from user conditions.
    """
    parsed = [parse_condition(c) for c in conditions]
    valid_set = set(valid_columns)

    for col, _op, _value in parsed:
        if col not in valid_set:
            raise ValueError(
                f"Column '{col}' does not exist. Available columns: {', '.join(valid_columns)}"
            )

    def pred(row: Dict[str, str]) -> bool:
        for col, op, value in parsed:
            cell = norm(row.get(col))

            if op == "=":
                if cell != value:
                    return False
            elif op == "!=":
                if cell == value:
                    return False
            elif op == "~":
                if re.search(value, cell, flags=re.IGNORECASE) is None:
                    return False
            elif op == "!~":
                if re.search(value, cell, flags=re.IGNORECASE) is not None:
                    return False

        return True

    return pred


def validate_columns(cols: List[str], valid_columns: List[str]) -> None:
    """
    Ensure that all requested columns exist in the file.
    """
    valid_set = set(valid_columns)
    bad = [c for c in cols if c not in valid_set]

    if bad:
        raise ValueError(
            f"Invalid columns: {', '.join(bad)}\n"
            f"Available columns: {', '.join(valid_columns)}"
        )


def parse_show_argument(show_arg: str) -> List[str]:
    """
    Parse --show argument.

    Supported forms:
        --show COL
        --show COL1,COL2
    """
    cols = [part.strip() for part in show_arg.split(",") if part.strip()]

    if not cols:
        raise ValueError("Empty --show argument.")

    if len(cols) > 2:
        raise ValueError("--show supports one column or two comma-separated columns only.")

    return cols


def filter_ns_pair(values: Tuple[str, ...], include_ns: bool) -> bool:
    """
    Return True if the value tuple should be kept.
    """
    if include_ns:
        return True

    for value in values:
        if value in {"", "NS"}:
            return False

    return True


def show_counts(rows: List[Dict[str, str]], columns: List[str], include_ns: bool) -> None:
    """
    Show value counts for one column or combination counts for two columns.
    """
    if len(columns) == 1:
        col = columns[0]
        counter = Counter()

        for row in rows:
            value = norm(row.get(col))
            if not filter_ns_pair((value,), include_ns):
                continue
            counter[value] += 1

        print(f"# show: {col}")
        print(f"{col}\tcount")

        for value, count in counter.most_common():
            print(f"{value}\t{count}")

        return

    col1, col2 = columns
    counter = Counter()

    for row in rows:
        v1 = norm(row.get(col1))
        v2 = norm(row.get(col2))

        if not filter_ns_pair((v1, v2), include_ns):
            continue

        counter[(v1, v2)] += 1

    print(f"# show: {col1},{col2}")
    print(f"{col1}\t{col2}\tcount")

    for (v1, v2), count in counter.most_common():
        print(f"{v1}\t{v2}\t{count}")


def summarize_columns_for_help(
    rows: List[Dict[str, str]],
    fieldnames: List[str],
    include_ns_in_help: bool = False,
    max_unique_to_show_all: int = 20,
    top_n_large: int = 8,
) -> str:
    """
    Build a compact help summary for each useful column.
    """
    lines = []
    lines.append("Available columns and example filter values:")

    for col in fieldnames:
        if col in HELP_SKIP_COLUMNS:
            continue

        counter = Counter()

        for row in rows:
            value = norm(row.get(col))
            if not include_ns_in_help and value in {"", "NS"}:
                continue
            counter[value] += 1

        n_unique = len(counter)

        if n_unique == 0:
            lines.append(f"  - {col}: no non-empty values")
            continue

        if n_unique <= max_unique_to_show_all:
            values = ", ".join(
                f"{repr(v)} ({counter[v]})"
                for v in sorted(counter.keys())
            )
            lines.append(f"  - {col}: {values}")
        else:
            top_values = ", ".join(
                f"{repr(v)} ({c})"
                for v, c in counter.most_common(top_n_large)
            )
            lines.append(
                f"  - {col}: {n_unique} unique values; top values: {top_values}"
            )

    return "\n".join(lines)


def load_phenotype_ids_from_classification(
    classification_tsv: Path,
    conditions: List[str],
) -> Set[str]:
    """
    Filter classification rows and return matching COSMIC_PHENOTYPE_ID values.
    """
    rows, fieldnames = load_rows(classification_tsv)

    if "COSMIC_PHENOTYPE_ID" not in fieldnames:
        raise ValueError("Column 'COSMIC_PHENOTYPE_ID' not found in classification file.")

    if conditions:
        pred = build_predicate(conditions, fieldnames)
        rows = [r for r in rows if pred(r)]

    phenotype_ids = {
        norm(r.get("COSMIC_PHENOTYPE_ID"))
        for r in rows
        if norm(r.get("COSMIC_PHENOTYPE_ID"))
    }

    return phenotype_ids


def load_sample_ids_for_phenotypes(sample_tsv: Path, phenotype_ids: Set[str]) -> Set[str]:
    """
    Return COSMIC_SAMPLE_ID values linked to the selected phenotype IDs.
    """
    sample_ids: Set[str] = set()

    with open_text(sample_tsv, "rt") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames or []

        required = {"COSMIC_SAMPLE_ID", "COSMIC_PHENOTYPE_ID"}
        missing = required - set(fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in sample TSV: {sorted(missing)}")

        for row in reader:
            pid = norm(row.get("COSMIC_PHENOTYPE_ID"))
            sid = norm(row.get("COSMIC_SAMPLE_ID"))

            if pid in phenotype_ids and sid:
                sample_ids.add(sid)

    return sample_ids


def protein_change_ok(hgvsp: str) -> bool:
    """
    Keep only informative protein changes.
    """
    if not hgvsp:
        return False
    if hgvsp == "p.?":
        return False
    if "=" in hgvsp:
        return False
    return True


def count_mutations_for_samples(
    mutations_tsv: Path,
    sample_ids: Set[str],
    mutation_mode: str = "missense",
) -> Dict[str, Set[str]]:
    """
    Count unique samples per mutation key.

    mutation_mode:
        - missense: keep variants whose MUTATION_DESCRIPTION contains missense_variant
        - protein_changing: keep variants whose MUTATION_DESCRIPTION contains at least
          one protein-changing consequence term
        - all: keep all mutations

    Returns:
        mut_key -> set(sample_ids)
    """
    mut_to_samples: Dict[str, Set[str]] = defaultdict(set)

    n_total = 0
    n_selected_samples = 0
    n_kept = 0

    with open_text(mutations_tsv, "rt") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = reader.fieldnames or []

        required = {
            "COSMIC_SAMPLE_ID",
            "GENE_SYMBOL",
            "MUTATION_DESCRIPTION",
            "GENOMIC_MUTATION_ID",
        }
        missing = required - set(fieldnames)
        if missing:
            raise ValueError(f"Missing required columns in mutations TSV: {sorted(missing)}")

        for row in reader:
            n_total += 1

            sample_id = norm(row.get("COSMIC_SAMPLE_ID"))
            if sample_id not in sample_ids:
                continue

            n_selected_samples += 1

            gene = norm(row.get("GENE_SYMBOL"))
            desc_raw = norm(row.get("MUTATION_DESCRIPTION"))
            desc_terms = parse_mutation_description(desc_raw)
            hgvsp = norm(row.get("HGVSP") or row.get("MUTATION_AA"))
            genomic_id = norm(row.get("GENOMIC_MUTATION_ID"))

            if mutation_mode == "missense":
                if not desc_terms.intersection(MISSENSE_TERMS):
                    continue
                if not gene or not protein_change_ok(hgvsp):
                    continue
                mut_key = f"{gene}|{hgvsp}"

            elif mutation_mode == "protein_changing":
                if not desc_terms.intersection(PROTEIN_CHANGING_TERMS):
                    continue
                if gene and protein_change_ok(hgvsp):
                    mut_key = f"{gene}|{hgvsp}"
                elif genomic_id:
                    mut_key = genomic_id
                else:
                    continue

            elif mutation_mode == "all":
                if genomic_id:
                    mut_key = genomic_id
                elif gene and hgvsp:
                    mut_key = f"{gene}|{hgvsp}"
                elif gene and desc_raw:
                    mut_key = f"{gene}|{desc_raw}"
                else:
                    continue

            else:
                raise ValueError(f"Unsupported mutation_mode: {mutation_mode}")

            mut_to_samples[mut_key].add(sample_id)
            n_kept += 1

            if n_total % 1_000_000 == 0:
                print(
                    f"[INFO] Processed {n_total:,} mutation rows; "
                    f"selected samples rows: {n_selected_samples:,}; kept: {n_kept:,}",
                    file=sys.stderr,
                )

    print(f"[INFO] Mutation rows processed: {n_total:,}", file=sys.stderr)
    print(f"[INFO] Rows belonging to selected samples: {n_selected_samples:,}", file=sys.stderr)
    print(f"[INFO] Rows kept after mutation filter ({mutation_mode}): {n_kept:,}", file=sys.stderr)

    return mut_to_samples


def write_mutation_counts(path: Path, mut_to_samples: Dict[str, Set[str]]) -> None:
    """
    Write final recurrent mutation counts.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["gene", "mutation", "n_samples"])

        for mut_key, samples in sorted(mut_to_samples.items(), key=lambda x: len(x[1]), reverse=True):
            if "|" in mut_key:
                gene, mutation = mut_key.split("|", 1)
            else:
                gene, mutation = "", mut_key
            writer.writerow([gene, mutation, len(samples)])


def build_parser(dynamic_help: str) -> argparse.ArgumentParser:
    """
    Build the argument parser with dynamic help text.
    """
    description = (
        "Explore Cosmic_Classification TSV files and optionally run the full "
        "phenotype/sample/mutation workflow.\n\n"
        "Exploration idea:\n"
        "  1. List the available columns\n"
        "  2. Show values for one column\n"
        "  3. Apply filters with --where\n"
        "  4. Show another column or a two-column combination\n"
        "  5. Run the final workflow with --run\n\n"
        "Filter syntax:\n"
        "  COL=value     exact match\n"
        "  COL!=value    exact mismatch\n"
        "  COL~regex     regex match\n"
        "  COL!~regex    regex exclusion\n\n"
        "Examples:\n"
        "  --classification-tsv Cosmic_Classification.tsv --list-columns\n"
        "  --classification-tsv Cosmic_Classification.tsv --show PRIMARY_SITE\n"
        "  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_SITE=skin' --show PRIMARY_HISTOLOGY\n"
        "  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_HISTOLOGY~melanoma' --show PRIMARY_SITE,HISTOLOGY_SUBTYPE_1\n"
        "  --classification-tsv Cosmic_Classification.tsv --sample-tsv Cosmic_Sample.tsv "
        "--mutations-tsv Cosmic_GenomeScreensMutant.tsv --where 'PRIMARY_HISTOLOGY~melanoma' "
        "--run --outdir results\n"
    )

    parser = argparse.ArgumentParser(
        description=description,
        epilog=dynamic_help,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--classification-tsv",
        required=True,
        type=Path,
        help="Path to Cosmic_Classification TSV or TSV.GZ file.",
    )

    parser.add_argument(
        "--where",
        action="append",
        default=[],
        help="Filter condition. Can be repeated.",
    )

    parser.add_argument(
        "--list-columns",
        action="store_true",
        help="Print column names and exit.",
    )

    parser.add_argument(
        "--show",
        type=str,
        help="Show value counts for one column or combination counts for two columns. Use COL or COL1,COL2.",
    )

    parser.add_argument(
        "--include-ns",
        action="store_true",
        help="Include empty values and 'NS' in exploration output.",
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the full phenotype/sample/mutation workflow.",
    )

    parser.add_argument(
        "--sample-tsv",
        type=Path,
        help="Path to Cosmic_Sample TSV or TSV.GZ file.",
    )

    parser.add_argument(
        "--mutations-tsv",
        type=Path,
        help="Path to Cosmic_GenomeScreensMutant TSV or TSV.GZ file.",
    )

    parser.add_argument(
        "--outdir",
        type=Path,
        help="Output directory for mutation counts.",
    )

    parser.add_argument(
        "--mutation-mode",
        choices=["missense", "protein_changing", "all"],
        default="missense",
        help=(
            "Mutation filtering mode for --run. Default: missense. "
            "'protein_changing' keeps variants with protein-changing consequence terms, "
            "'all' keeps all mutations."
        ),
    )

    return parser


def main() -> None:
    """
    Main entry point.

    The parser is built in two stages so that -h/--help can include
    real columns and example values from the provided input file.
    """
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--classification-tsv", type=Path)
    pre_args, _unknown = pre.parse_known_args()

    dynamic_help = (
        "To show dynamic column/value help, run:\n"
        "  script.py --classification-tsv Cosmic_Classification.tsv --help"
    )

    if pre_args.classification_tsv:
        try:
            rows, fieldnames = load_rows(pre_args.classification_tsv)
            dynamic_help = summarize_columns_for_help(rows, fieldnames)
        except Exception as e:
            dynamic_help = f"Could not build dynamic help from input file: {e}"

    parser = build_parser(dynamic_help)
    args = parser.parse_args()

    if not args.classification_tsv.exists():
        raise SystemExit(
            f"[ERROR] Classification file does not exist: {args.classification_tsv}"
        )

    rows, fieldnames = load_rows(args.classification_tsv)

    if args.list_columns:
        for col in fieldnames:
            print(col)
        return

    filtered_rows = rows

    if args.where:
        pred = build_predicate(args.where, fieldnames)
        filtered_rows = [r for r in rows if pred(r)]

    if args.show:
        show_columns = parse_show_argument(args.show)
        validate_columns(show_columns, fieldnames)

        print(f"# total_rows\t{len(rows)}", file=sys.stderr)
        print(f"# filtered_rows\t{len(filtered_rows)}", file=sys.stderr)

        show_counts(filtered_rows, show_columns, args.include_ns)
        return

    if args.run:
        if not args.sample_tsv or not args.mutations_tsv or not args.outdir:
            raise SystemExit(
                "[ERROR] --run requires --sample-tsv, --mutations-tsv and --outdir."
            )

        print(
            f"[INFO] Running the full workflow with mutation mode: {args.mutation_mode}. "
            "Tip: explore first with --list-columns, --show and --where.",
            file=sys.stderr,
        )

        phenotype_ids = load_phenotype_ids_from_classification(
            args.classification_tsv,
            args.where,
        )

        if not phenotype_ids:
            raise SystemExit(
                "[ERROR] No phenotype IDs matched the provided filters."
            )

        sample_ids = load_sample_ids_for_phenotypes(
            args.sample_tsv,
            phenotype_ids,
        )

        if not sample_ids:
            raise SystemExit(
                "[ERROR] No sample IDs matched the selected phenotype IDs."
            )

        mut_to_samples = count_mutations_for_samples(
            args.mutations_tsv,
            sample_ids,
            mutation_mode=args.mutation_mode,
        )

        args.outdir.mkdir(parents=True, exist_ok=True)

        write_mutation_counts(
            args.outdir / "mutation_counts.tsv",
            mut_to_samples,
        )

        print(
            f"[INFO] Phenotype IDs matched: {len(phenotype_ids):,}",
            file=sys.stderr,
        )

        print(
            f"[INFO] Sample IDs matched: {len(sample_ids):,}",
            file=sys.stderr,
        )

        print(
            f"[INFO] Unique recurrent mutations: {len(mut_to_samples):,}",
            file=sys.stderr,
        )

        print(
            f"[INFO] Output directory: {args.outdir}",
            file=sys.stderr,
        )

        return

    print(
        "[INFO] No action requested. You can explore the classification table with "
        "--list-columns, --show and --where, or run the full workflow with --run.",
        file=sys.stderr,
    )
    parser.print_help()


if __name__ == "__main__":
    main()