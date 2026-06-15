import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import subprocess

class DataHandler:
    """Handles all data operations for the supplier order entry system."""
    
    def __init__(self, data_dir="supplier_data", github_repo=None):
        """
        Initialize the data handler.
        
        Args:
            data_dir: Directory to store supplier JSON files
            github_repo: GitHub repository URL for syncing (optional)
        """
        self.data_dir = data_dir
        self.github_repo = github_repo or os.getenv('GITHUB_REPO_URL', '')
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        
        # Create data directory if it doesn't exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        self.config_file = os.path.join(self.data_dir, 'config.json')
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'suppliers': []
            }
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_all_suppliers(self):
        """Get list of all supplier names."""
        suppliers = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.json') and file != 'config.json':
                supplier_name = file.replace('.json', '')
                suppliers.append(supplier_name)
        return sorted(suppliers)
    
    def create_supplier(self, supplier_name, description=""):
        """
        Create a new supplier.
        
        Args:
            supplier_name: Name of the supplier
            description: Description of the supplier
            
        Returns:
            bool: True if successful
        """
        try:
            supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
            
            if os.path.exists(supplier_file):
                return False  # Supplier already exists
            
            supplier_data = {
                'supplier_name': supplier_name,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'rules': []
            }
            
            with open(supplier_file, 'w') as f:
                json.dump(supplier_data, f, indent=2)
            
            # Update config
            if supplier_name not in self.config['suppliers']:
                self.config['suppliers'].append(supplier_name)
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return False
    
    def get_supplier_info(self, supplier_name):
        """Get supplier information."""
        supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
        
        try:
            with open(supplier_file, 'r') as f:
                data = json.load(f)
            
            return {
                'supplier_name': data.get('supplier_name', supplier_name),
                'description': data.get('description', ''),
                'created_at': data.get('created_at', 'N/A'),
                'last_updated': data.get('last_updated', 'N/A')
            }
        except Exception as e:
            print(f"Error getting supplier info: {e}")
            return {}
    
    def get_supplier_rules(self, supplier_name):
        """Get all rules for a supplier."""
        supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
        
        try:
            with open(supplier_file, 'r') as f:
                data = json.load(f)
            return data.get('rules', [])
        except Exception as e:
            print(f"Error getting supplier rules: {e}")
            return []
    
    def add_rule(self, supplier_name, rule):
        """
        Add a new rule to a supplier.
        
        Args:
            supplier_name: Name of the supplier
            rule: Dictionary containing rule data
            
        Returns:
            bool: True if successful
        """
        try:
            supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
            
            with open(supplier_file, 'r') as f:
                data = json.load(f)
            
            data['rules'].append(rule)
            data['last_updated'] = datetime.now().isoformat()
            
            with open(supplier_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding rule: {e}")
            return False
    
    def update_supplier_rules(self, supplier_name, rules):
        """
        Update all rules for a supplier.
        
        Args:
            supplier_name: Name of the supplier
            rules: List of rule dictionaries
            
        Returns:
            bool: True if successful
        """
        try:
            supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
            
            with open(supplier_file, 'r') as f:
                data = json.load(f)
            
            data['rules'] = rules
            data['last_updated'] = datetime.now().isoformat()
            
            with open(supplier_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating rules: {e}")
            return False
    
    def delete_supplier_rules(self, supplier_name):
        """Delete all rules for a supplier."""
        try:
            supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
            
            with open(supplier_file, 'r') as f:
                data = json.load(f)
            
            data['rules'] = []
            data['last_updated'] = datetime.now().isoformat()
            
            with open(supplier_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting rules: {e}")
            return False
    
    def delete_supplier(self, supplier_name):
        """Delete entire supplier and all its rules."""
        try:
            supplier_file = os.path.join(self.data_dir, f'{supplier_name}.json')
            
            if os.path.exists(supplier_file):
                os.remove(supplier_file)
            
            # Update config
            if supplier_name in self.config['suppliers']:
                self.config['suppliers'].remove(supplier_name)
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False
    
    def rename_supplier(self, old_name, new_name):
        """Rename a supplier."""
        try:
            old_file = os.path.join(self.data_dir, f'{old_name}.json')
            new_file = os.path.join(self.data_dir, f'{new_name}.json')
            
            if os.path.exists(new_file):
                return False  # New name already exists
            
            with open(old_file, 'r') as f:
                data = json.load(f)
            
            data['supplier_name'] = new_name
            data['last_updated'] = datetime.now().isoformat()
            
            with open(new_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            os.remove(old_file)
            
            # Update config
            if old_name in self.config['suppliers']:
                idx = self.config['suppliers'].index(old_name)
                self.config['suppliers'][idx] = new_name
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error renaming supplier: {e}")
            return False
    
    def push_to_github(self):
        """
        Push data to GitHub repository.
        
        Returns:
            bool: True if successful
        """
        if not self.github_repo:
            print("GitHub repository URL not configured")
            return False
        
        try:
            # Run git commands
            os.system(f'cd {self.data_dir} && git add -A')
            os.system(f'cd {self.data_dir} && git commit -m "Update supplier data - {datetime.now().isoformat()}"')
            os.system(f'cd {self.data_dir} && git push origin main')
            
            return True
        except Exception as e:
            print(f"Error pushing to GitHub: {e}")
            return False
    
    def pull_from_github(self):
        """
        Pull data from GitHub repository.
        
        Returns:
            bool: True if successful
        """
        if not self.github_repo:
            print("GitHub repository URL not configured")
            return False
        
        try:
            os.system(f'cd {self.data_dir} && git pull origin main')
            self._load_config()  # Reload config after pulling
            return True
        except Exception as e:
            print(f"Error pulling from GitHub: {e}")
            return False
    
    def export_to_csv(self, supplier_name):
        """Export supplier rules to CSV."""
        try:
            rules = self.get_supplier_rules(supplier_name)
            
            if not rules:
                return None
            
            df = pd.DataFrame(rules)
            csv_path = os.path.join(self.data_dir, f'{supplier_name}_export.csv')
            df.to_csv(csv_path, index=False)
            
            return csv_path
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None
    
    def import_from_csv(self, supplier_name, csv_path):
        """Import supplier rules from CSV."""
        try:
            df = pd.read_csv(csv_path)
            rules = df.to_dict('records')
            
            # Add timestamps
            for rule in rules:
                if 'created_at' not in rule:
                    rule['created_at'] = datetime.now().isoformat()
            
            return self.update_supplier_rules(supplier_name, rules)
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False
    
    def get_customer_rules(self, customer_name):
        """Get all rules for a specific customer across all suppliers."""
        results = []
        
        for supplier in self.get_all_suppliers():
            rules = self.get_supplier_rules(supplier)
            
            for rule in rules:
                if customer_name.lower() in rule.get('customer', '').lower():
                    rule['supplier'] = supplier
                    results.append(rule)
        
        return results
    
    def get_product_rules(self, product_name):
        """Get all rules for a specific product across all suppliers."""
        results = []
        
        for supplier in self.get_all_suppliers():
            rules = self.get_supplier_rules(supplier)
            
            for rule in rules:
                if product_name.lower() in rule.get('ordered_product', '').lower():
                    rule['supplier'] = supplier
                    results.append(rule)
        
        return results
    
    def get_statistics(self):
        """Get system-wide statistics."""
        stats = {
            'total_suppliers': len(self.get_all_suppliers()),
            'total_rules': 0,
            'total_customers': set(),
            'total_products': set()
        }
        
        for supplier in self.get_all_suppliers():
            rules = self.get_supplier_rules(supplier)
            stats['total_rules'] += len(rules)
            
            for rule in rules:
                stats['total_customers'].add(rule.get('customer', ''))
                stats['total_products'].add(rule.get('ordered_product', ''))
        
        stats['total_customers'] = len(stats['total_customers'])
        stats['total_products'] = len(stats['total_products'])
        
        return stats

# Example usage
if __name__ == "__main__":
    handler = DataHandler()
    
    # Create a sample supplier
    handler.create_supplier("Fresho Supplies", "Fresh produce supplier")
    
    # Add some sample rules
    sample_rule = {
        'customer': 'All Saints Hotel The View',
        'ordered_product': 'Cherry heritage tomatoes',
        'ordered_unit': 'box',
        'fresho_product': 'Send 1 yellow cherry toma and 1 cherry red toma',
        'fresho_qty': '12',
        'other_comments': 'Special handling required',
        'created_at': datetime.now().isoformat()
    }
    
    handler.add_rule("Fresho Supplies", sample_rule)
    
    # Get statistics
    stats = handler.get_statistics()
    print(f"System Statistics: {stats}")
