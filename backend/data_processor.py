import pandas as pd
import datetime
import math
import uuid
from sqlalchemy.orm import Session
from . import models

def process_sales_file(filepath: str, owner_id: int, db: Session):
    """
    Reads an uploaded file (CSV or Excel) and populates Product and Sale models.
    Tries heuristics to detect names, quantity, and prices.
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
        
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    # Heuristics naming matches
    col_map = {
        'name': None,
        'qty': None,
        'price': None,
        'date': None
    }
    
    for col in df.columns:
        if 'product' in col or 'item' in col or 'name' in col or 'description' in col:
            if not col_map['name']: col_map['name'] = col
        if 'qty' in col or 'quantity' in col or 'amount' in col:
            if not col_map['qty']: col_map['qty'] = col
        if 'price' in col or 'unit' in col or 'px' in col or 'revenue' in col:
            if not col_map['price']: col_map['price'] = col
        if 'date' in col or 'time' in col or 'trx' in col:
            if not col_map['date']: col_map['date'] = col
            
    # Default fallback names if heuristics miss
    if not col_map['name'] and len(df.columns) > 0: col_map['name'] = df.columns[0]
    if not col_map['qty'] and len(df.columns) > 1: col_map['qty'] = df.columns[1]
    if not col_map['price'] and len(df.columns) > 2: col_map['price'] = df.columns[2]
            
    added_sales = 0
    records = df.to_dict('records')
    
    # Optimization: Pre-load DB mapping into memory to avoid N+1 remote database hits
    all_products = db.query(models.Product).filter(models.Product.owner_id == owner_id).all()
    product_dict = {p.name: p for p in all_products}
    
    for row in records:
        name_val = str(row.get(col_map['name'], 'Unknown Product'))
        qty_val = row.get(col_map['qty'], 1)
        price_val = row.get(col_map['price'], 0.0)
        
        if pd.isna(name_val): continue
        if pd.isna(qty_val) or type(qty_val) == str: qty_val = 1
        if pd.isna(price_val) or type(price_val) == str: price_val = 0.0
        
        # Ensure quantities and prices are standard
        try:
            qty_val = int(qty_val)
            price_val = float(price_val)
        except ValueError:
            qty_val = 1
            price_val = 0.0
            
        date_raw = row.get(col_map.get('date')) if col_map.get('date') else None
        sale_date_val = datetime.datetime.utcnow()
        if date_raw and not pd.isna(date_raw):
            try:
                # Optimized pandas parsing rules
                parsed = pd.to_datetime(date_raw, dayfirst=True, errors='coerce')
                if pd.notna(parsed):
                    sale_date_val = parsed.to_pydatetime()
            except Exception:
                pass
                
        # Check if product exists for owner in memory array
        db_product = product_dict.get(name_val)
        
        if not db_product:
            db_product = models.Product(
                name=name_val,
                sku=f"SKU-{uuid.uuid4().hex[:8].upper()}",
                category="General",
                current_stock=100, # Starting default
                reorder_level=10,
                price=price_val,
                owner_id=owner_id
            )
            db.add(db_product)
            db.flush() # Safe single-session ID hook
            product_dict[name_val] = db_product
            
        # Add sale record
        new_sale = models.Sale(
            owner_id=owner_id,
            product_id=db_product.id,
            quantity=qty_val,
            unit_price=price_val,
            total_price=qty_val * price_val,
            sale_date=sale_date_val
        )
        db.add(new_sale)
        
        # Deduct from inventory stock securely
        if db_product.current_stock > 0:
            db_product.current_stock = max(0, db_product.current_stock - qty_val)
            
        
    db.commit()
    return {"message": f"Processed {len(records)} sales mapping them to {col_map['name']}, {col_map['qty']}, {col_map['price']}."}

def process_inventory_file(filepath: str, owner_id: int, db: Session):
    """
    Reads an uploaded inventory file (CSV/Excel) to prepopulate database products and statuses.
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
        
    df.columns = [str(c).lower().strip() for c in df.columns]
    
    col_map = {
        'name': None,
        'stock': None,
        'price': None,
        'category': None
    }
    
    for col in df.columns:
        if 'product' in col or 'item' in col or 'name' in col or 'description' in col:
            if not col_map['name']: col_map['name'] = col
        if 'qty' in col or 'quantity' in col or 'stock' in col or 'inventory' in col:
            if not col_map['stock']: col_map['stock'] = col
        if 'price' in col or 'cost' in col or 'value' in col:
            if not col_map['price']: col_map['price'] = col
        if 'category' in col or 'type' in col or 'group' in col:
            if not col_map['category']: col_map['category'] = col
            
    # Default fallback names if heuristics miss
    if not col_map['name'] and len(df.columns) > 0: col_map['name'] = df.columns[0]
    if not col_map['stock'] and len(df.columns) > 1: col_map['stock'] = df.columns[1]
    
    records = df.to_dict('records')
    
    # Optmization: Load products dynamically in one hit
    user_inventory = db.query(models.Product).filter(models.Product.owner_id == owner_id).all()
    inventory_dict = {p.name: p for p in user_inventory}
    
    for row in records:
        name_val = str(row.get(col_map['name'], 'Unknown Product'))
        if pd.isna(name_val): continue
        
        stock_val = row.get(col_map['stock'], 0)
        price_val = 0.0
        if col_map['price']: 
            price_val = row.get(col_map['price'], 0.0)
            
        category_val = "General"
        if col_map['category']: 
            category_val = str(row.get(col_map['category'], 'General'))
            
        try:
            stock_val = int(stock_val)
            price_val = float(price_val)
        except ValueError:
            stock_val = 0
            price_val = 0.0
            
        db_product = inventory_dict.get(name_val)
        
        if not db_product:
            db_product = models.Product(
                name=name_val,
                sku=f"SKU-{uuid.uuid4().hex[:8].upper()}",
                category=category_val,
                current_stock=stock_val,
                reorder_level=10,
                price=price_val,
                owner_id=owner_id
            )
            db.add(db_product)
            inventory_dict[name_val] = db_product
        else:
            db_product.current_stock = stock_val
            db_product.price = price_val
            db_product.category = category_val
            
    db.commit()
    return {"message": "Success"}
