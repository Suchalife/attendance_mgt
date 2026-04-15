"""
CSV Service for handling CSV file operations
Simple utility for reading and writing CSV files
"""
import csv
import os
from typing import List, Dict


class CSVService:
    """Service for CSV file operations"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Use absolute path relative to this file
            self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        else:
            self.data_dir = data_dir
        
        # Normalize the path
        self.data_dir = os.path.abspath(self.data_dir)
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"CSVService initialized with data directory: {self.data_dir}")
    
    def read_csv(self, filename: str) -> List[Dict]:
        """
        Read CSV file and return list of dictionaries
        Returns empty list if file doesn't exist
        """
        filepath = os.path.join(self.data_dir, filename)
        print(f"Reading CSV from: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"CSV file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                print(f"Successfully read {len(data)} records from {filename}")
                return data
        except Exception as e:
            print(f"Error reading CSV {filename}: {e}")
            return []
    
    def write_csv(self, filename: str, data: List[Dict], fieldnames: List[str]):
        """
        Write data to CSV file
        Creates file with headers if it doesn't exist
        """
        filepath = os.path.join(self.data_dir, filename)
        print(f"Writing CSV to: {filepath}")
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"Successfully wrote {len(data)} records to {filename}")
            return True
        except Exception as e:
            print(f"Error writing CSV {filename}: {e}")
            return False
    
    def append_csv(self, filename: str, data: Dict, fieldnames: List[str]):
        """
        Append single row to CSV file
        Creates file with headers if it doesn't exist
        """
        filepath = os.path.join(self.data_dir, filename)
        print(f"Appending to CSV: {filepath}")
        file_exists = os.path.exists(filepath)
        
        try:
            with open(filepath, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    print(f"Created new CSV file with headers: {filename}")
                
                writer.writerow(data)
            print(f"Successfully appended record to {filename}")
            return True
        except Exception as e:
            print(f"Error appending to CSV {filename}: {e}")
            return False
    
    def file_exists(self, filename: str) -> bool:
        """Check if CSV file exists"""
        filepath = os.path.join(self.data_dir, filename)
        exists = os.path.exists(filepath)
        print(f"CSV file exists check - {filepath}: {exists}")
        return exists
