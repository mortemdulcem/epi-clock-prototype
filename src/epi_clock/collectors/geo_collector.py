import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import GEOparse
import requests
from tqdm import tqdm
import gzip
import io

class GEOCollector:
    def __init__(self, cache_dir: str = "data/geo_cache"):
        """
        GEO datasets collector for methylation data
        
        Args:
            cache_dir: Directory to cache downloaded files
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_dataset(self, accession: str) -> Optional[Dict]:
        """
        Fetch GEO dataset by accession number
        
        Args:
            accession: GEO accession (e.g., 'GSE42861')
            
        Returns:
            Dictionary with dataset information and data
        """
        cache_path = os.path.join(self.cache_dir, f"{accession}.pkl")
        
        # Check cache first
        if os.path.exists(cache_path):
            print(f"[GEO] Loading cached dataset: {accession}")
            try:
                import pickle
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"[GEO] Cache read error: {e}")
        
        try:
            print(f"[GEO] Downloading dataset: {accession}")
            gse = GEOparse.get_GEO(geo=accession, destdir=self.cache_dir)
            
            dataset_info = {
                'accession': accession,
                'title': gse.metadata.get('title', ['Unknown'])[0],
                'summary': gse.metadata.get('summary', [''])[0],
                'organism': gse.metadata.get('taxon', ['Unknown'])[0],
                'platform': gse.metadata.get('platform_id', ['Unknown'])[0],
                'samples': [],
                'methylation_data': None,
                'sample_metadata': None
            }
            
            # Extract sample information
            sample_data = []
            methylation_matrices = []
            
            for gsm_name, gsm in gse.gsms.items():
                sample_info = {
                    'sample_id': gsm_name,
                    'title': gsm.metadata.get('title', [''])[0],
                    'source': gsm.metadata.get('source_name_ch1', [''])[0],
                    'characteristics': self._parse_characteristics(gsm.metadata),
                    'supplementary_files': gsm.metadata.get('supplementary_file', [])
                }
                sample_data.append(sample_info)
                
                # Try to get methylation data
                if hasattr(gsm, 'table') and gsm.table is not None:
                    # This is simplified - real implementation would handle different platforms
                    if 'VALUE' in gsm.table.columns or 'Beta_value' in gsm.table.columns:
                        methylation_matrices.append(gsm.table)
            
            dataset_info['samples'] = sample_data
            dataset_info['sample_metadata'] = pd.DataFrame(sample_data)
            
            # Combine methylation data if available
            if methylation_matrices:
                print(f"[GEO] Processing methylation data for {len(methylation_matrices)} samples")
                dataset_info['methylation_data'] = self._combine_methylation_data(methylation_matrices)
            
            # Cache the result
            try:
                import pickle
                with open(cache_path, 'wb') as f:
                    pickle.dump(dataset_info, f)
                print(f"[GEO] Cached dataset: {cache_path}")
            except Exception as e:
                print(f"[GEO] Cache write error: {e}")
                
            return dataset_info
            
        except Exception as e:
            print(f"[GEO] Error fetching {accession}: {e}")
            return None
    
    def _parse_characteristics(self, metadata: Dict) -> Dict:
        """Parse sample characteristics from metadata"""
        characteristics = {}
        
        # Common characteristic fields
        char_fields = [key for key in metadata.keys() if 'characteristics' in key.lower()]
        
        for field in char_fields:
            values = metadata[field]
            for value in values:
                if ':' in value:
                    key, val = value.split(':', 1)
                    characteristics[key.strip()] = val.strip()
                else:
                    characteristics[field] = value
        
        # Parse other relevant fields
        for key in ['age', 'gender', 'tissue', 'disease_state', 'treatment']:
            if key in metadata:
                characteristics[key] = metadata[key][0] if metadata[key] else None
        
        return characteristics
    
    def _combine_methylation_data(self, matrices: List[pd.DataFrame]) -> pd.DataFrame:
        """Combine methylation data from multiple samples"""
        if not matrices:
            return None
        
        # Find common CpG sites across all samples
        common_cpgs = None
        for matrix in matrices:
            cpg_sites = set(matrix.index) if hasattr(matrix, 'index') else set(matrix.iloc[:, 0])
            if common_cpgs is None:
                common_cpgs = cpg_sites
            else:
                common_cpgs = common_cpgs.intersection(cpg_sites)
        
        if not common_cpgs:
            print("[GEO] Warning: No common CpG sites found")
            return None
        
        print(f"[GEO] Found {len(common_cpgs)} common CpG sites")
        
        # Create combined matrix
        combined_data = {}
        for i, matrix in enumerate(matrices):
            sample_name = f"sample_{i}"
            
            # Extract beta values for common CpGs
            if 'VALUE' in matrix.columns:
                values = matrix.set_index(matrix.columns[0])['VALUE']
            elif 'Beta_value' in matrix.columns:
                values = matrix.set_index(matrix.columns[0])['Beta_value']
            else:
                # Take the second column as values
                values = matrix.set_index(matrix.columns[0]).iloc[:, 0]
            
            # Filter to common CpGs
            common_values = values.loc[list(common_cpgs)]
            combined_data[sample_name] = common_values
        
        return pd.DataFrame(combined_data)
    
    def collect_datasets(self, config: Dict) -> Dict[str, Dict]:
        """Collect multiple GEO datasets"""
        datasets = {}
        
        for dataset_config in config['datasets']:
            accession = dataset_config['accession']
            print(f"\n[GEO] Processing {accession}: {dataset_config.get('title', 'Unknown')}")
            
            dataset = self.fetch_dataset(accession)
            if dataset:
                datasets[accession] = dataset
            else:
                print(f"[GEO] Failed to fetch {accession}")
        
        print(f"\n[GEO] Successfully collected {len(datasets)} datasets")
        return datasets
    
    def extract_cpg_sites(self, datasets: Dict[str, Dict]) -> pd.DataFrame:
        """Extract CpG site information across datasets"""
        all_cpgs = set()
        dataset_cpgs = {}
        
        for accession, dataset in datasets.items():
            if dataset['methylation_data'] is not None:
                cpgs = set(dataset['methylation_data'].index)
                all_cpgs.update(cpgs)
                dataset_cpgs[accession] = cpgs
        
        # Create summary DataFrame
        cpg_summary = []
        for cpg in all_cpgs:
            present_in = [acc for acc, cpgs in dataset_cpgs.items() if cpg in cpgs]
            cpg_summary.append({
                'cpg_site': cpg,
                'present_in_datasets': len(present_in),
                'datasets': present_in
            })
        
        return pd.DataFrame(cpg_summary).sort_values('present_in_datasets', ascending=False)
