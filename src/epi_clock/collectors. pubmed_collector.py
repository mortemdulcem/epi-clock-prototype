import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
from Bio import Entrez


class PubMedCollector:
    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        PubMed API collector for methylation studies

        Args:
            email: Required by NCBI
            api_key: Optional API key for higher rate limits
        """
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.delay = 0.34 if api_key else 1.0  # Rate limiting

    def search_studies(
        self,
        query: str,
        retmax: int = 100,
        date_start: str = "2015/01/01",
        date_end: str = "2024/12/31",
    ) -> List[str]:
        """Search PubMed for relevant studies"""
        search_query = f"{query} AND {date_start}:{date_end}[PDAT]"

        print(f"[PubMed] Searching: {search_query}")

        handle = Entrez.esearch(
            db="pubmed", term=search_query, retmax=retmax, sort="relevance"
        )

        record = Entrez.read(handle)
        handle.close()

        pmids = record["IdList"]
        print(f"[PubMed] Found {len(pmids)} articles")

        time.sleep(self.delay)
        return pmids

    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed information for PMIDs"""
        if not pmids:
            return []

        print(f"[PubMed] Fetching details for {len(pmids)} articles...")

        # Batch processing for efficiency
        batch_size = 50
        all_records = []

        for i in range(0, len(pmids), batch_size):
            batch = pmids[i : i + batch_size]

            handle = Entrez.efetch(db="pubmed", id=batch, rettype="xml", retmode="text")

            records = Entrez.read(handle)
            handle.close()

            for record in records["PubmedArticle"]:
                try:
                    article_data = self._extract_article_data(record)
                    all_records.append(article_data)
                except Exception as e:
                    print(f"[PubMed] Error processing article: {e}")

            time.sleep(self.delay)

        return all_records

    def _extract_article_data(self, record) -> Dict:
        """Extract relevant data from PubMed record"""
        article = record["MedlineCitation"]["Article"]

        # Basic info
        pmid = record["MedlineCitation"]["PMID"]
        title = article["ArticleTitle"]

        # Abstract
        abstract = ""
        if "Abstract" in article:
            abstract_sections = article["Abstract"].get("AbstractText", [])
            if isinstance(abstract_sections, list):
                abstract = " ".join([str(section) for section in abstract_sections])
            else:
                abstract = str(abstract_sections)

        # Authors
        authors = []
        if "AuthorList" in article:
            for author in article["AuthorList"]:
                if "LastName" in author and "ForeName" in author:
                    authors.append(f"{author['ForeName']} {author['LastName']}")

        # Journal and year
        journal = article["Journal"]["Title"]
        year = article["Journal"]["JournalIssue"]["PubDate"].get("Year", "Unknown")

        # DOI
        doi = None
        if "ELocationID" in article:
            for elocation in article["ELocationID"]:
                if elocation.attributes.get("EIdType") == "doi":
                    doi = str(elocation)

        return {
            "pmid": str(pmid),
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "year": year,
            "doi": doi,
            "methylation_mentions": self._count_methylation_terms(
                title + " " + abstract
            ),
            "sample_size": self._extract_sample_size(abstract),
            "study_type": self._classify_study_type(title + " " + abstract),
        }

    def _count_methylation_terms(self, text: str) -> int:
        """Count methylation-related terms"""
        terms = [
            "methylation",
            "epigenetic",
            "CpG",
            "DNAm",
            "5mC",
            "hypermethylation",
            "hypomethylation",
        ]
        text_lower = text.lower()
        return sum(text_lower.count(term) for term in terms)

    def _extract_sample_size(self, abstract: str) -> Optional[int]:
        """Try to extract sample size from abstract"""
        import re

        # Common patterns: "n = 123", "N=123", "123 participants", "123 subjects"
        patterns = [
            r"[nN]\s*=\s*(\d+)",
            r"(\d+)\s+(?:participants|subjects|samples|patients|individuals)",
            r"sample\s+size\s+of\s+(\d+)",
            r"(\d+)\s+(?:cases|controls)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, abstract)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue

        return None

    def _classify_study_type(self, text: str) -> str:
        """Classify study type based on keywords"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["meta-analysis", "systematic review"]):
            return "meta-analysis"
        elif any(
            word in text_lower for word in ["longitudinal", "prospective", "cohort"]
        ):
            return "longitudinal"
        elif any(word in text_lower for word in ["cross-sectional", "case-control"]):
            return "cross-sectional"
        elif any(word in text_lower for word in ["clinical trial", "randomized"]):
            return "clinical_trial"
        else:
            return "observational"

    def collect_data(self, config: Dict) -> pd.DataFrame:
        """Main collection method"""
        all_articles = []

        for query_config in config["queries"]:
            pmids = self.search_studies(
                query_config["term"],
                query_config["retmax"],
                config["date_range"]["start"],
                config["date_range"]["end"],
            )

            articles = self.fetch_details(pmids)
            all_articles.extend(articles)

        df = pd.DataFrame(all_articles)

        # Remove duplicates by PMID
        if not df.empty:
            df = df.drop_duplicates(subset=["pmid"])
            df = df.reset_index(drop=True)

        print(f"[PubMed] Collected {len(df)} unique articles")
        return df
