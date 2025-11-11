import argparse
import os

import yaml

from . import evaluate, features, ingest, make_figures, train
from .collectors import geo_collector, meta_analysis, pubmed_collector
from .utils.config import load_config


def collect_pubmed_data(config_path: str):
    """Collect data from PubMed"""
    cfg = load_config(config_path)

    # Load data sources config
    data_sources_path = config_path.replace("default.yaml", "data_sources.yaml")
    if not os.path.exists(data_sources_path):
        print(f"[collect_pubmed] Error: {data_sources_path} not found")
        return

    with open(data_sources_path, "r") as f:
        data_sources = yaml.safe_load(f)

    # Initialize collector
    pubmed_config = data_sources["pubmed"]
    collector = pubmed_collector.PubMedCollector(
        email=pubmed_config["email"], api_key=pubmed_config.get("api_key")
    )

    # Collect data
    df = collector.collect_data(pubmed_config)

    # Save results
    output_dir = cfg["data"]["raw_dir"]
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "pubmed_studies.csv"), index=False)
    print(
        f"[collect_pubmed] Saved {len(df)} studies to {output_dir}/pubmed_studies.csv"
    )


def collect_geo_data(config_path: str):
    """Collect data from GEO"""
    cfg = load_config(config_path)

    data_sources_path = config_path.replace("default.yaml", "data_sources.yaml")
    if not os.path.exists(data_sources_path):
        print(f"[collect_geo] Error: {data_sources_path} not found")
        return

    with open(data_sources_path, "r") as f:
        data_sources = yaml.safe_load(f)

    collector = geo_collector.GEOCollector(
        cache_dir=os.path.join(cfg["data"]["raw_dir"], "geo_cache")
    )

    datasets = collector.collect_datasets(data_sources["geo"])

    # Save dataset summaries
    output_dir = cfg["data"]["raw_dir"]
    os.makedirs(output_dir, exist_ok=True)

    import json

    with open(os.path.join(output_dir, "geo_datasets.json"), "w") as f:
        # Convert datasets to JSON-serializable format
        json_datasets = {}
        for acc, data in datasets.items():
            json_datasets[acc] = {
                "accession": data["accession"],
                "title": data["title"],
                "summary": (
                    data["summary"][:500] + "..."
                    if len(data["summary"]) > 500
                    else data["summary"]
                ),
                "organism": data["organism"],
                "platform": data["platform"],
                "n_samples": len(data["samples"]),
                "has_methylation_data": data["methylation_data"] is not None,
            }
        json.dump(json_datasets, f, indent=2)

    print(f"[collect_geo] Processed {len(datasets)} datasets")


def run_meta_analysis(config_path: str):
    """Run meta-analysis on collected data"""
    cfg = load_config(config_path)
    analyzer = meta_analysis.MetaAnalyzer()

    raw_dir = cfg["data"]["raw_dir"]

    # Load PubMed data
    pubmed_path = os.path.join(raw_dir, "pubmed_studies.csv")
    geo_path = os.path.join(raw_dir, "geo_datasets.json")

    literature_analysis = {}
    geo_analysis = {}

    if os.path.exists(pubmed_path):
        import pandas as pd

        pubmed_df = pd.read_csv(pubmed_path)
        literature_analysis = analyzer.analyze_literature(pubmed_df)

    if os.path.exists(geo_path):
        import json

        with open(geo_path, "r") as f:
            geo_datasets = json.load(f)
        geo_analysis = analyzer.analyze_geo_data(geo_datasets)

    # Synthesize findings
    synthesis = analyzer.synthesize_findings(literature_analysis, geo_analysis)

    # Save results
    results_dir = cfg["output"]["results_dir"]
    os.makedirs(results_dir, exist_ok=True)

    import json

    with open(os.path.join(results_dir, "meta_analysis.json"), "w") as f:
        json.dump(
            {
                "literature_analysis": literature_analysis,
                "geo_analysis": geo_analysis,
                "synthesis": synthesis,
            },
            f,
            indent=2,
        )

    print(f"[meta_analyze] Results saved to {results_dir}/meta_analysis.json")


def generate_report(config_path: str):
    """Generate comprehensive report"""
    cfg = load_config(config_path)
    results_dir = cfg["output"]["results_dir"]

    # This would generate a comprehensive markdown/HTML report
    # combining all analyses
    print(f"[generate_report] Report generation not yet implemented")
    print(f"[generate_report] Check {results_dir}/ for individual result files")


def main():
    p = argparse.ArgumentParser(
        description="Epigenetic Clock Pipeline with Real Data Collection"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Data collection commands
    collect_pubmed_cmd = sub.add_parser(
        "collect_pubmed", help="Collect PubMed literature data"
    )
    collect_pubmed_cmd.add_argument("--config", required=True)

    collect_geo_cmd = sub.add_parser(
        "collect_geo", help="Collect GEO methylation datasets"
    )
    collect_geo_cmd.add_argument("--config", required=True)

    meta_cmd = sub.add_parser(
        "meta_analyze", help="Run meta-analysis on collected data"
    )
    meta_cmd.add_argument("--config", required=True)

    # Analysis commands
    for name in ["ingest", "features", "train", "evaluate", "make_figures"]:
        sp = sub.add_parser(name)
        sp.add_argument("--config", required=True)

    # Reporting
    report_cmd = sub.add_parser("generate_report", help="Generate comprehensive report")
    report_cmd.add_argument("--config", required=True)

    args = p.parse_args()

    # Route commands
    if args.cmd == "collect_pubmed":
        collect_pubmed_data(args.config)
    elif args.cmd == "collect_geo":
        collect_geo_data(args.config)
    elif args.cmd == "meta_analyze":
        run_meta_analysis(args.config)
    elif args.cmd == "ingest":
        ingest.run(args.config)
    elif args.cmd == "features":
        features.run(args.config)
    elif args.cmd == "train":
        train.run(args.config)
    elif args.cmd == "evaluate":
        evaluate.run(args.config)
    elif args.cmd == "make_figures":
        make_figures.run(args.config)
    elif args.cmd == "generate_report":
        generate_report(args.config)


if __name__ == "__main__":
    main()
