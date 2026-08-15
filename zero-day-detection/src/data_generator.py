"""
Sample Data Generator
Generates synthetic network traffic data for testing and training
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class DataGenerator:
    """Generate synthetic network traffic data"""
    
    ATTACK_TYPES = ['DoS', 'Probe', 'R2L', 'U2R', 'Normal']
    PROTOCOLS = ['tcp', 'udp', 'icmp']
    FLAGS = ['SF', 'S0', 'REJ', 'RSTO', 'SH', 'RSTR', 'S1', 'S2', 'S3']
    SERVICES = ['http', 'ftp', 'smtp', 'ssh', 'telnet', 'dns', 'other']
    
    @staticmethod
    def generate_normal_traffic(n_samples: int = 1000) -> pd.DataFrame:
        """Generate normal network traffic samples"""
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='1s'),
            'packet_size': np.random.normal(500, 200, n_samples).clip(50, 1500),
            'byte_count': np.random.normal(2000, 500, n_samples).clip(100, 5000),
            'duration_seconds': np.random.exponential(2, n_samples).clip(0.1, 10),
            'protocol_type': np.random.choice(DataGenerator.PROTOCOLS, n_samples, p=[0.7, 0.2, 0.1]),
            'flag_status': np.random.choice(DataGenerator.FLAGS, n_samples, p=[0.6, 0.1, 0.1, 0.05, 0.05, 0.03, 0.03, 0.02, 0.02]),
            'service_type': np.random.choice(DataGenerator.SERVICES, n_samples, p=[0.4, 0.1, 0.1, 0.15, 0.05, 0.1, 0.1]),
            'label': ['Normal'] * n_samples
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_dos_attack(n_samples: int = 200) -> pd.DataFrame:
        """Generate DoS attack samples - High volume, short duration"""
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='100ms'),
            'packet_size': np.random.normal(1200, 300, n_samples).clip(800, 1500),
            'byte_count': np.random.normal(8000, 2000, n_samples).clip(5000, 15000),
            'duration_seconds': np.random.exponential(0.5, n_samples).clip(0.01, 2),
            'protocol_type': np.random.choice(['tcp', 'udp'], n_samples, p=[0.3, 0.7]),
            'flag_status': np.random.choice(['S0', 'REJ', 'RSTO'], n_samples, p=[0.6, 0.2, 0.2]),
            'service_type': np.random.choice(['http', 'other'], n_samples, p=[0.8, 0.2]),
            'label': ['DoS'] * n_samples
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_probe_attack(n_samples: int = 150) -> pd.DataFrame:
        """Generate Probe attack samples - Many small packets"""
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='500ms'),
            'packet_size': np.random.normal(100, 50, n_samples).clip(40, 300),
            'byte_count': np.random.normal(500, 200, n_samples).clip(50, 1000),
            'duration_seconds': np.random.exponential(0.3, n_samples).clip(0.01, 1),
            'protocol_type': np.random.choice(['tcp', 'icmp'], n_samples, p=[0.6, 0.4]),
            'flag_status': np.random.choice(['S0', 'REJ', 'SF'], n_samples, p=[0.5, 0.3, 0.2]),
            'service_type': np.random.choice(['other', 'telnet', 'ssh'], n_samples, p=[0.6, 0.2, 0.2]),
            'label': ['Probe'] * n_samples
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_r2l_attack(n_samples: int = 100) -> pd.DataFrame:
        """Generate R2L attack samples - Unusual protocols and services"""
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='2s'),
            'packet_size': np.random.normal(800, 300, n_samples).clip(200, 1400),
            'byte_count': np.random.normal(4000, 1500, n_samples).clip(1000, 8000),
            'duration_seconds': np.random.normal(5, 2, n_samples).clip(1, 15),
            'protocol_type': np.random.choice(DataGenerator.PROTOCOLS, n_samples, p=[0.8, 0.15, 0.05]),
            'flag_status': np.random.choice(['SF', 'S0', 'RSTO'], n_samples, p=[0.5, 0.3, 0.2]),
            'service_type': np.random.choice(['ftp', 'telnet', 'other'], n_samples, p=[0.4, 0.4, 0.2]),
            'label': ['R2L'] * n_samples
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_u2r_attack(n_samples: int = 50) -> pd.DataFrame:
        """Generate U2R attack samples - Similar to normal but with specific patterns"""
        data = {
            'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='10s'),
            'packet_size': np.random.normal(600, 250, n_samples).clip(200, 1200),
            'byte_count': np.random.normal(3000, 1000, n_samples).clip(500, 6000),
            'duration_seconds': np.random.normal(8, 3, n_samples).clip(2, 20),
            'protocol_type': np.random.choice(['tcp', 'udp'], n_samples, p=[0.9, 0.1]),
            'flag_status': np.random.choice(['SF', 'S1', 'RSTO'], n_samples, p=[0.7, 0.2, 0.1]),
            'service_type': np.random.choice(['ssh', 'telnet', 'other'], n_samples, p=[0.5, 0.3, 0.2]),
            'label': ['U2R'] * n_samples
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_dataset(normal: int = 1000, dos: int = 200, probe: int = 150, 
                        r2l: int = 100, u2r: int = 50, shuffle: bool = True) -> pd.DataFrame:
        """
        Generate complete dataset with all attack types
        
        Args:
            normal: Number of normal samples
            dos: Number of DoS attack samples
            probe: Number of Probe attack samples
            r2l: Number of R2L attack samples
            u2r: Number of U2R attack samples
            shuffle: Whether to shuffle the dataset
            
        Returns:
            Complete dataset DataFrame
        """
        datasets = []
        
        if normal > 0:
            datasets.append(DataGenerator.generate_normal_traffic(normal))
        if dos > 0:
            datasets.append(DataGenerator.generate_dos_attack(dos))
        if probe > 0:
            datasets.append(DataGenerator.generate_probe_attack(probe))
        if r2l > 0:
            datasets.append(DataGenerator.generate_r2l_attack(r2l))
        if u2r > 0:
            datasets.append(DataGenerator.generate_u2r_attack(u2r))
        
        # Combine all datasets
        complete_dataset = pd.concat(datasets, ignore_index=True)
        
        if shuffle:
            complete_dataset = complete_dataset.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return complete_dataset
    
    @staticmethod
    def save_dataset(df: pd.DataFrame, filepath: str, format: str = 'csv'):
        """
        Save dataset to file
        
        Args:
            df: Dataset DataFrame
            filepath: Output file path
            format: File format ('csv' or 'json')
        """
        if format == 'csv':
            df.to_csv(filepath, index=False)
        elif format == 'json':
            df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Dataset saved to {filepath}")
