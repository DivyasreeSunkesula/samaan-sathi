"""
Synthetic Data Generator for Samaan Sathi
Generates realistic shop data for demo and testing
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

class MockDataGenerator:
    """Generate realistic synthetic data for demo"""
    
    # Indian names for customers
    CUSTOMER_NAMES = [
        "Ramesh Kumar", "Suresh Sharma", "Rajesh Patel", "Mukesh Gupta",
        "Priya Singh", "Anjali Verma", "Sunita Devi", "Geeta Rani",
        "Vijay Kumar", "Amit Shah", "Ravi Yadav", "Sanjay Joshi",
        "Meena Kumari", "Rekha Devi", "Savita Sharma", "Pooja Gupta",
        "Manoj Kumar", "Anil Verma", "Deepak Singh", "Rahul Patel"
    ]
    
    # Common grocery items with realistic prices
    INVENTORY_ITEMS = [
        # Groceries
        {"name": "Rice 1kg", "category": "groceries", "costPrice": 40, "sellingPrice": 50, "unit": "kg"},
        {"name": "Wheat Flour 1kg", "category": "groceries", "costPrice": 35, "sellingPrice": 45, "unit": "kg"},
        {"name": "Sugar 1kg", "category": "groceries", "costPrice": 38, "sellingPrice": 48, "unit": "kg"},
        {"name": "Salt 1kg", "category": "groceries", "costPrice": 18, "sellingPrice": 25, "unit": "kg"},
        {"name": "Cooking Oil 1L", "category": "groceries", "costPrice": 120, "sellingPrice": 150, "unit": "L"},
        {"name": "Toor Dal 1kg", "category": "groceries", "costPrice": 90, "sellingPrice": 110, "unit": "kg"},
        {"name": "Moong Dal 1kg", "category": "groceries", "costPrice": 85, "sellingPrice": 105, "unit": "kg"},
        {"name": "Tea Powder 250g", "category": "groceries", "costPrice": 80, "sellingPrice": 100, "unit": "g"},
        
        # Beverages
        {"name": "Coca Cola 600ml", "category": "beverages", "costPrice": 30, "sellingPrice": 40, "unit": "ml"},
        {"name": "Pepsi 600ml", "category": "beverages", "costPrice": 30, "sellingPrice": 40, "unit": "ml"},
        {"name": "Sprite 600ml", "category": "beverages", "costPrice": 30, "sellingPrice": 40, "unit": "ml"},
        {"name": "Thums Up 600ml", "category": "beverages", "costPrice": 30, "sellingPrice": 40, "unit": "ml"},
        {"name": "Mineral Water 1L", "category": "beverages", "costPrice": 15, "sellingPrice": 20, "unit": "L"},
        
        # Snacks
        {"name": "Parle-G Biscuits", "category": "snacks", "costPrice": 8, "sellingPrice": 10, "unit": "pack"},
        {"name": "Kurkure", "category": "snacks", "costPrice": 8, "sellingPrice": 10, "unit": "pack"},
        {"name": "Lays Chips", "category": "snacks", "costPrice": 8, "sellingPrice": 10, "unit": "pack"},
        {"name": "Maggi Noodles", "category": "snacks", "costPrice": 10, "sellingPrice": 14, "unit": "pack"},
        {"name": "Britannia Cake", "category": "snacks", "costPrice": 18, "sellingPrice": 25, "unit": "pack"},
        
        # Personal Care
        {"name": "Colgate Toothpaste", "category": "personal-care", "costPrice": 35, "sellingPrice": 45, "unit": "piece"},
        {"name": "Lux Soap", "category": "personal-care", "costPrice": 25, "sellingPrice": 35, "unit": "piece"},
        {"name": "Clinic Plus Shampoo", "category": "personal-care", "costPrice": 60, "sellingPrice": 75, "unit": "piece"},
        {"name": "Fair & Lovely Cream", "category": "personal-care", "costPrice": 80, "sellingPrice": 100, "unit": "piece"},
        
        # Household
        {"name": "Vim Bar", "category": "household", "costPrice": 8, "sellingPrice": 10, "unit": "piece"},
        {"name": "Surf Excel 500g", "category": "household", "costPrice": 80, "sellingPrice": 100, "unit": "g"},
        {"name": "Harpic Toilet Cleaner", "category": "household", "costPrice": 70, "sellingPrice": 90, "unit": "piece"},
    ]
    
    def __init__(self, shop_id: str = "SHOP001"):
        self.shop_id = shop_id
        self.start_date = datetime.now() - timedelta(days=90)  # 90 days of history
    
    def generate_complete_shop_data(self) -> Dict[str, Any]:
        """Generate complete shop data with all components"""
        print("Generating inventory...")
        inventory = self.generate_inventory()
        
        print("Generating customers...")
        customers = self.generate_customers()
        
        print("Generating sales history...")
        sales_history = self.generate_sales_history(inventory, customers, days=90)
        
        print("Generating udhaar records...")
        udhaar_records = self.generate_udhaar_records(customers, sales_history)
        
        # Calculate current cash (simplified)
        total_sales = sum(s['totalAmount'] for s in sales_history)
        total_costs = sum(s.get('totalCost', s['totalAmount'] * 0.7) for s in sales_history)
        cash_available = total_sales - total_costs - sum(
            u.get('amount', 0) - u.get('paidAmount', 0)
            for u in udhaar_records
            if u.get('status') != 'PAID'
        )
        cash_available = max(5000, cash_available)  # Minimum 5000
        
        return {
            'shopId': self.shop_id,
            'shopName': 'Ramesh General Store',
            'ownerName': 'Ramesh Kumar',
            'phone': '+91-9876543210',
            'address': 'Main Market, Village Rampur, District Meerut, UP',
            'cashAvailable': round(cash_available, 2),
            'inventory': inventory,
            'customers': customers,
            'salesHistory': sales_history,
            'udhaarRecords': udhaar_records,
            'generatedAt': datetime.now().isoformat()
        }
    
    def generate_inventory(self) -> List[Dict[str, Any]]:
        """Generate inventory with realistic stock levels"""
        inventory = []
        
        for item_template in self.INVENTORY_ITEMS:
            item_id = f"ITEM{len(inventory)+1:03d}"
            
            # Random stock levels
            quantity = random.randint(10, 100)
            
            # Calculate sales velocity (units per day)
            if item_template['category'] == 'groceries':
                sales_velocity = random.uniform(3, 10)
            elif item_template['category'] == 'beverages':
                sales_velocity = random.uniform(5, 15)
            elif item_template['category'] == 'snacks':
                sales_velocity = random.uniform(4, 12)
            else:
                sales_velocity = random.uniform(2, 6)
            
            inventory.append({
                'itemId': item_id,
                'name': item_template['name'],
                'category': item_template['category'],
                'quantity': quantity,
                'unit': item_template['unit'],
                'costPrice': item_template['costPrice'],
                'sellingPrice': item_template['sellingPrice'],
                'minStockLevel': int(sales_velocity * 3),  # 3 days buffer
                'maxStockLevel': int(sales_velocity * 14),  # 2 weeks max
                'salesVelocity': round(sales_velocity, 2),
                'lastRestockDate': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'expiryDate': (datetime.now() + timedelta(days=random.randint(60, 365))).isoformat() if item_template['category'] in ['groceries', 'snacks'] else None
            })
        
        return inventory
    
    def generate_customers(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate customer profiles"""
        customers = []
        
        for i, name in enumerate(self.CUSTOMER_NAMES[:count]):
            customer_id = f"CUST{i+1:03d}"
            
            customers.append({
                'customerId': customer_id,
                'customerName': name,
                'phone': f"+91-{random.randint(7000000000, 9999999999)}",
                'address': f"House {random.randint(1, 200)}, {random.choice(['Main Road', 'Market Street', 'Village Center'])}",
                'registeredDate': (self.start_date + timedelta(days=random.randint(0, 30))).isoformat(),
                'totalPurchases': 0,  # Will be calculated
                'totalOutstanding': 0  # Will be calculated
            })
        
        return customers
    
    def generate_sales_history(self, inventory: List[Dict], customers: List[Dict], days: int = 90) -> List[Dict[str, Any]]:
        """Generate realistic sales history"""
        sales_history = []
        
        for day in range(days):
            sale_date = self.start_date + timedelta(days=day)
            
            # Number of sales per day (more on weekends)
            is_weekend = sale_date.weekday() in [5, 6]
            daily_sales = random.randint(15, 25) if is_weekend else random.randint(8, 15)
            
            # Festival boost (simplified)
            month = sale_date.month
            if month in [10, 11]:  # Diwali season
                daily_sales = int(daily_sales * 1.5)
            elif month in [3]:  # Holi
                daily_sales = int(daily_sales * 1.3)
            
            for _ in range(daily_sales):
                sale = self._generate_single_sale(inventory, customers, sale_date)
                sales_history.append(sale)
        
        return sales_history
    
    def _generate_single_sale(self, inventory: List[Dict], customers: List[Dict], sale_date: datetime) -> Dict[str, Any]:
        """Generate a single sale transaction"""
        sale_id = f"SALE{str(uuid.uuid4())[:8].upper()}"
        
        # Random customer (80% registered, 20% walk-in)
        if random.random() < 0.8 and customers:
            customer = random.choice(customers)
            customer_id = customer['customerId']
            customer_name = customer['customerName']
        else:
            customer_id = None
            customer_name = "Walk-in Customer"
        
        # Number of items in basket (1-5)
        num_items = random.choices([1, 2, 3, 4, 5], weights=[30, 35, 20, 10, 5])[0]
        
        # Select items
        selected_items = random.sample(inventory, min(num_items, len(inventory)))
        
        items = []
        total_amount = 0
        total_cost = 0
        
        for item in selected_items:
            # Quantity (1-5 for most items)
            if item['category'] == 'groceries':
                quantity = random.choices([1, 2, 3, 5], weights=[40, 30, 20, 10])[0]
            else:
                quantity = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            
            price = item['sellingPrice']
            cost = item['costPrice']
            
            items.append({
                'itemId': item['itemId'],
                'name': item['name'],
                'quantity': quantity,
                'price': price,
                'cost': cost,
                'subtotal': price * quantity
            })
            
            total_amount += price * quantity
            total_cost += cost * quantity
        
        # Payment method
        payment_method = random.choices(
            ['CASH', 'UPI', 'UDHAAR'],
            weights=[50, 30, 20]
        )[0]
        
        return {
            'saleId': sale_id,
            'shopId': self.shop_id,
            'customerId': customer_id,
            'customerName': customer_name,
            'items': items,
            'totalAmount': round(total_amount, 2),
            'totalCost': round(total_cost, 2),
            'profit': round(total_amount - total_cost, 2),
            'margin': round((total_amount - total_cost) / total_amount * 100, 1) if total_amount > 0 else 0,
            'paymentMethod': payment_method,
            'timestamp': sale_date.isoformat(),
            'createdAt': sale_date.isoformat()
        }
    
    def generate_udhaar_records(self, customers: List[Dict], sales_history: List[Dict]) -> List[Dict[str, Any]]:
        """Generate udhaar (credit) records from sales"""
        udhaar_records = []
        
        # Filter udhaar sales
        udhaar_sales = [s for s in sales_history if s.get('paymentMethod') == 'UDHAAR']
        
        for sale in udhaar_sales:
            if not sale.get('customerId'):
                continue  # Skip walk-in udhaar
            
            udhaar_id = f"UDHAAR{str(uuid.uuid4())[:8].upper()}"
            amount = sale['totalAmount']
            created_date = datetime.fromisoformat(sale['timestamp'])
            
            # Determine payment status based on customer behavior
            # Some customers pay quickly, some delay, some don't pay
            customer_behavior = random.random()
            
            if customer_behavior < 0.6:  # 60% paid
                status = 'PAID'
                days_to_pay = random.randint(1, 45)
                paid_date = created_date + timedelta(days=days_to_pay)
                paid_amount = amount
            elif customer_behavior < 0.85:  # 25% pending
                status = 'PENDING'
                paid_date = None
                paid_amount = 0
            else:  # 15% overdue
                status = 'OVERDUE'
                paid_date = None
                paid_amount = 0
            
            udhaar_records.append({
                'udhaarId': udhaar_id,
                'shopId': self.shop_id,
                'customerId': sale['customerId'],
                'customerName': sale['customerName'],
                'saleId': sale['saleId'],
                'amount': amount,
                'paidAmount': paid_amount,
                'remainingAmount': amount - paid_amount,
                'status': status,
                'createdAt': created_date.isoformat(),
                'paidAt': paid_date.isoformat() if paid_date else None,
                'dueDate': (created_date + timedelta(days=30)).isoformat(),
                'notes': ''
            })
        
        return udhaar_records
    
    def save_to_file(self, data: Dict[str, Any], filename: str = 'mock_shop_data.json'):
        """Save generated data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_sales = sum(s['totalAmount'] for s in data['salesHistory'])
        total_profit = sum(s['profit'] for s in data['salesHistory'])
        total_udhaar = sum(
            u['amount'] - u['paidAmount']
            for u in data['udhaarRecords']
            if u['status'] != 'PAID'
        )
        
        return {
            'totalInventoryItems': len(data['inventory']),
            'totalCustomers': len(data['customers']),
            'totalSales': len(data['salesHistory']),
            'totalRevenue': round(total_sales, 2),
            'totalProfit': round(total_profit, 2),
            'avgMargin': round(total_profit / total_sales * 100, 1) if total_sales > 0 else 0,
            'totalUdhaarRecords': len(data['udhaarRecords']),
            'outstandingUdhaar': round(total_udhaar, 2),
            'cashAvailable': data['cashAvailable'],
            'dataGeneratedAt': data['generatedAt']
        }


def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        body = json.loads(event.get('body', '{}'))
        shop_id = body.get('shopId', 'SHOP001')
        
        generator = MockDataGenerator(shop_id)
        data = generator.generate_complete_shop_data()
        summary = generator.generate_summary(data)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'data': data,
                'summary': summary
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


# For local testing
if __name__ == '__main__':
    generator = MockDataGenerator('SHOP001')
    data = generator.generate_complete_shop_data()
    summary = generator.generate_summary(data)
    
    print("\n=== MOCK DATA SUMMARY ===")
    print(json.dumps(summary, indent=2))
    
    generator.save_to_file(data, 'mock_shop_data.json')
    print("\n✅ Mock data generated successfully!")
