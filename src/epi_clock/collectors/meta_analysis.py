from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class MetaAnalyzer:
    def __init__(self):
        """Meta-analysis of collected methylation studies"""
        self.literature_data = None
        self.geo_data = None
        self.combined_results = None

    def analyze_literature(self, pubmed_df: pd.DataFrame) -> Dict:
        """Analyze PubMed literature data"""
        if pubmed_df.empty:
            return {}

        print(f"[Meta] Analyzing {len(pubmed_df)} literature studies")

        analysis = {
            "total_studies": len(pubmed_df),
            "study_types": pubmed_df["study_type"].value_counts().to_dict(),
            "journals": pubmed_df["journal"].value_counts().head(10).to_dict(),
            "yearly_trend": pubmed_df["year"].value_counts().sort_index().to_dict(),
            "sample_sizes": self._analyze_sample_sizes(pubmed_df),
            "key_terms": self._extract_key_terms(pubmed_df),
            "high_impact_studies": self._identify_high_impact(pubmed_df),
        }

        return analysis

    def _analyze_sample_sizes(self, df: pd.DataFrame) -> Dict:
        """Analyze sample sizes across studies"""
        sample_sizes = df["sample_size"].dropna()

        if sample_sizes.empty:
            return {}

        return {
            "total_samples": int(sample_sizes.sum()),
            "mean_sample_size": float(sample_sizes.mean()),
            "median_sample_size": float(sample_sizes.median()),
            "min_sample_size": int(sample_sizes.min()),
            "max_sample_size": int(sample_sizes.max()),
            "studies_with_sample_size": len(sample_sizes),
        }

    def _extract_key_terms(self, df: pd.DataFrame) -> Dict:
        """Extract key terms from abstracts"""
        all_text = " ".join(df["abstract"].fillna(""))

        # Key addiction-related terms
        addiction_terms = [
            "cocaine",
            "alcohol",
            "nicotine",
            "opioid",
            "cannabis",
            "methamphetamine",
            "substance abuse",
            "drug addiction",
            "alcoholism",
            "smoking",
        ]

        # Key methylation terms
        methyl_terms = [
            "DNA methylation",
            "CpG sites",
            "hypermethylation",
            "hypomethylation",
            "methylation patterns",
            "epigenetic modifications",
            "methylome",
        ]

        term_counts = {}
        for term in addiction_terms + methyl_terms:
            count = all_text.lower().count(term.lower())
            if count > 0:
                term_counts[term] = count

        return dict(sorted(term_counts.items(), key=lambda x: x[1], reverse=True))

    def _identify_high_impact(
        self, df: pd.DataFrame, min_citations: int = 50
    ) -> List[Dict]:
        """Identify high-impact studies (simplified - would need citation data)"""
        # In real implementation, would fetch citation counts from APIs
        high_impact = []

        # Use methylation mentions and sample size as proxies for impact
        df_scored = df.copy()
        df_scored["impact_score"] = (
            df_scored["methylation_mentions"] * 2
            + (df_scored["sample_size"].fillna(0) / 100)
            + df_scored["year"].astype(int) * 0.1
        )

        top_studies = df_scored.nlargest(10, "impact_score")

        for _, study in top_studies.iterrows():
            high_impact.append(
                {
                    "pmid": study["pmid"],
                    "title": study["title"],
                    "year": study["year"],
                    "journal": study["journal"],
                    "sample_size": study["sample_size"],
                    "impact_score": round(study["impact_score"], 2),
                }
            )

        return high_impact

    def analyze_geo_data(self, geo_datasets: Dict[str, Dict]) -> Dict:
        """Analyze GEO methylation datasets"""
        if not geo_datasets:
            return {}

        print(f"[Meta] Analyzing {len(geo_datasets)} GEO datasets")

        analysis = {
            "total_datasets": len(geo_datasets),
            "total_samples": 0,
            "platforms": {},
            "organisms": {},
            "cpg_overlap": None,
            "data_quality": {},
        }

        all_cpg_sites = []
        platform_counts = {}
        organism_counts = {}

        for accession, dataset in geo_datasets.items():
            # Count samples
            n_samples = len(dataset["samples"])
            analysis["total_samples"] += n_samples

            # Platform distribution
            platform = dataset.get("platform", "Unknown")
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

            # Organism distribution
            organism = dataset.get("organism", "Unknown")
            organism_counts[organism] = organism_counts.get(organism, 0) + 1

            # CpG sites
            if dataset["methylation_data"] is not None:
                cpg_sites = set(dataset["methylation_data"].index)
                all_cpg_sites.append((accession, cpg_sites))

                # Data quality metrics
                data = dataset["methylation_data"]
                analysis["data_quality"][accession] = {
                    "n_cpg_sites": len(cpg_sites),
                    "n_samples": data.shape[1],
                    "missing_rate": float(data.isnull().sum().sum() / data.size),
                    "value_range": [float(data.min().min()), float(data.max().max())],
                }

        analysis["platforms"] = platform_counts
        analysis["organisms"] = organism_counts

        # Analyze CpG overlap
        if all_cpg_sites:
            analysis["cpg_overlap"] = self._analyze_cpg_overlap(all_cpg_sites)

        return analysis

    def _analyze_cpg_overlap(self, cpg_data: List[Tuple[str, set]]) -> Dict:
        """Analyze CpG site overlap between datasets"""
        if len(cpg_data) < 2:
            return {}

        all_cpgs = set()
        for _, cpgs in cpg_data:
            all_cpgs.update(cpgs)

        # Find core CpG sites (present in all datasets)
        core_cpgs = cpg_data[0][1]
        for _, cpgs in cpg_data[1:]:
            core_cpgs = core_cpgs.intersection(cpgs)

        # Dataset-specific CpGs
        dataset_specific = {}
        for acc, cpgs in cpg_data:
            others = set()
            for other_acc, other_cpgs in cpg_data:
                if other_acc != acc:
                    others.update(other_cpgs)
            specific = cpgs - others
            dataset_specific[acc] = len(specific)

        return {
            "total_unique_cpgs": len(all_cpgs),
            "core_cpgs": len(core_cpgs),
            "core_cpg_list": list(core_cpgs)[:100],  # First 100 for space
            "dataset_specific_counts": dataset_specific,
            "overlap_matrix": self._create_overlap_matrix(cpg_data),
        }

    def _create_overlap_matrix(self, cpg_data: List[Tuple[str, set]]) -> Dict:
        """Create pairwise overlap matrix"""
        accessions = [acc for acc, _ in cpg_data]
        n = len(accessions)
        overlap_matrix = {}

        for i in range(n):
            overlap_matrix[accessions[i]] = {}
            for j in range(n):
                if i == j:
                    overlap = 1.0
                else:
                    set1 = cpg_data[i][1]
                    set2 = cpg_data[j][1]
                    overlap = len(set1.intersection(set2)) / len(set1.union(set2))
                overlap_matrix[accessions[i]][accessions[j]] = round(overlap, 3)

        return overlap_matrix

    def synthesize_findings(
        self, literature_analysis: Dict, geo_analysis: Dict
    ) -> Dict:
        """Synthesize findings from literature and GEO data"""
        synthesis = {
            "data_sources": {
                "literature_studies": literature_analysis.get("total_studies", 0),
                "geo_datasets": geo_analysis.get("total_datasets", 0),
                "total_samples": (
                    literature_analysis.get("sample_sizes", {}).get("total_samples", 0)
                    + geo_analysis.get("total_samples", 0)
                ),
            },
            "methodological_insights": self._extract_methodological_insights(
                literature_analysis
            ),
            "data_availability": self._assess_data_availability(geo_analysis),
            "research_gaps": self._identify_research_gaps(
                literature_analysis, geo_analysis
            ),
            "recommendations": self._generate_recommendations(
                literature_analysis, geo_analysis
            ),
        }

        return synthesis

    def _extract_methodological_insights(self, lit_analysis: Dict) -> List[str]:
        """Extract methodological insights from literature"""
        insights = []

        if "study_types" in lit_analysis:
            most_common = max(lit_analysis["study_types"].items(), key=lambda x: x[1])
            insights.append(
                f"Most common study design: {most_common[0]} ({most_common[1]} studies)"
            )

        if "sample_sizes" in lit_analysis:
            sample_info = lit_analysis["sample_sizes"]
            if sample_info:
                insights.append(
                    f"Average sample size: {sample_info.get('mean_sample_size', 0):.0f} "
                    f"(range: {sample_info.get('min_sample_size', 0)}-{sample_info.get('max_sample_size', 0)})"
                )

        if "key_terms" in lit_analysis:
            top_terms = list(lit_analysis["key_terms"].keys())[:3]
            if top_terms:
                insights.append(f"Most studied substances: {', '.join(top_terms)}")

        return insights

    def _assess_data_availability(self, geo_analysis: Dict) -> List[str]:
        """Assess data availability from GEO analysis"""
        availability = []

        if "platforms" in geo_analysis:
            platforms = geo_analysis["platforms"]
            availability.append(f"Available platforms: {list(platforms.keys())}")

        if "cpg_overlap" in geo_analysis and geo_analysis["cpg_overlap"]:
            core_cpgs = geo_analysis["cpg_overlap"].get("core_cpgs", 0)
            total_cpgs = geo_analysis["cpg_overlap"].get("total_unique_cpgs", 0)
            availability.append(
                f"Core CpG sites across datasets: {core_cpgs}/{total_cpgs}"
            )

        quality_issues = []
        if "data_quality" in geo_analysis:
            for acc, quality in geo_analysis["data_quality"].items():
                if quality["missing_rate"] > 0.1:
                    quality_issues.append(
                        f"{acc}: {quality['missing_rate']:.1%} missing"
                    )

        if quality_issues:
            availability.append(
                f"Data quality concerns: {len(quality_issues)} datasets with >10% missing"
            )

        return availability

    def _identify_research_gaps(
        self, lit_analysis: Dict, geo_analysis: Dict
    ) -> List[str]:
        """Identify research gaps"""
        gaps = []

        # Sample size gaps
        if "sample_sizes" in lit_analysis:
            sample_info = lit_analysis["sample_sizes"]
            if sample_info.get("mean_sample_size", 0) < 200:
                gaps.append("Small sample sizes in most studies (avg < 200)")

        # Longitudinal studies gap
        if "study_types" in lit_analysis:
            study_types = lit_analysis["study_types"]
            longitudinal_pct = study_types.get("longitudinal", 0) / sum(
                study_types.values()
            )
            if longitudinal_pct < 0.2:
                gaps.append("Limited longitudinal studies for causal inference")

        # Data integration gap
        if geo_analysis.get("total_datasets", 0) < 5:
            gaps.append("Limited publicly available methylation datasets")

        # CpG overlap gap
        if "cpg_overlap" in geo_analysis and geo_analysis["cpg_overlap"]:
            core_ratio = geo_analysis["cpg_overlap"].get("core_cpgs", 0) / geo_analysis[
                "cpg_overlap"
            ].get("total_unique_cpgs", 1)
            if core_ratio < 0.3:
                gaps.append(
                    "Low CpG site overlap between datasets limits meta-analysis"
                )

        return gaps

    def _generate_recommendations(
        self, lit_analysis: Dict, geo_analysis: Dict
    ) -> List[str]:
        """Generate recommendations for future research"""
        recommendations = []

        recommendations.append(
            "Standardize methylation platforms for better data integration"
        )
        recommendations.append(
            "Increase sample sizes through multi-site collaborations"
        )
        recommendations.append("Develop longitudinal cohorts for causal inference")
        recommendations.append("Focus on replication across diverse populations")
        recommendations.append("Integrate clinical outcomes with methylation data")

        # Specific recommendations based on data
        if "key_terms" in lit_analysis:
            understudied = ["methamphetamine", "synthetic drugs", "polysubstance"]
            available_terms = lit_analysis["key_terms"].keys()
            missing = [term for term in understudied if term not in available_terms]
            if missing:
                recommendations.append(
                    f"Address understudied substances: {', '.join(missing)}"
                )

        return recommendations
