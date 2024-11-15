# app/models/cart.py

import sqlite3
from typing import Dict, Optional
from datetime import datetime
import json
from langchain_core.tools import tool
import time

def get_db():
    return sqlite3.connect('data/shopping.db')

@tool
def add_product_to_cartitems(
    product_id: str,
    quantity: int = 1,
    *,
    config: Dict
) -> str:
    """Add products to cart with inventory validation"""
    try:
        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return json.dumps({
                "status": "error",
                "message": "No user ID configured"
            })

        conn = get_db()
        cursor = conn.cursor()

        # Check inventory
        cursor.execute(
            "SELECT price, inventory FROM products WHERE id = ?",
            (product_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return json.dumps({
                "status": "error",
                "message": f"Product {product_id} not found"
            })
        
        price, available_inventory = result
        quantity = int(quantity)
        
        if quantity <= 0:
            return json.dumps({
                "status": "error",
                "message": "Quantity must be positive"
            })
            
        if quantity > available_inventory:
            return json.dumps({
                "status": "error",
                "message": f"Not enough inventory. Only {available_inventory} units available"
            })

        # Check existing cart
        cursor.execute("""
            SELECT id, quantity FROM cart_items 
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        
        cart_item = cursor.fetchone()
        if cart_item:
            cart_id, current_qty = cart_item
            new_qty = current_qty + quantity
            
            if new_qty > available_inventory:
                return json.dumps({
                    "status": "error",
                    "message": f"Cannot add {quantity} more units. Cart has {current_qty} units and only {available_inventory} available"
                })
                
            cursor.execute("""
                UPDATE cart_items 
                SET quantity = ?, price_at_time = ?
                WHERE id = ?
            """, (new_qty, price, cart_id))
        else:
            cart_id = f"CART_{product_id}_{int(time.time())}"
            cursor.execute("""
                INSERT INTO cart_items (id, user_id, product_id, quantity, price_at_time)
                VALUES (?, ?, ?, ?, ?)
            """, (cart_id, user_id, product_id, quantity, price))

        conn.commit()
        return json.dumps({
            "status": "success",
            "message": f"Successfully added {quantity} of product {product_id} to cart"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
    finally:
        cursor.close()
        conn.close()

@tool
def remove_product_from_cartitems(
    product_id: str,
    quantity: Optional[int] = None,
    *,
    config: Dict
) -> str:
    """Remove products from cart"""
    try:
        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return json.dumps({
                "status": "error",
                "message": "No user ID configured"
            })

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, quantity FROM cart_items 
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        
        cart_item = cursor.fetchone()
        if not cart_item:
            return json.dumps({
                "status": "error",
                "message": f"Product {product_id} not found in cart"
            })

        cart_id, current_qty = cart_item

        if quantity is None or quantity >= current_qty:
            cursor.execute("DELETE FROM cart_items WHERE id = ?", (cart_id,))
            msg = f"Removed all {current_qty} units of product {product_id} from cart"
        else:
            new_qty = current_qty - quantity
            cursor.execute("""
                UPDATE cart_items 
                SET quantity = ? 
                WHERE id = ?
            """, (new_qty, cart_id))
            msg = f"Removed {quantity} units of product {product_id} from cart"

        conn.commit()
        return json.dumps({
            "status": "success",
            "message": msg
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
    finally:
        cursor.close()
        conn.close()