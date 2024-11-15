# app/models/order.py

import sqlite3
from typing import Dict, List, Any
from datetime import datetime
import json
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

def get_db():
    return sqlite3.connect('data/shopping.db')

@tool
def fetch_customer_relate_information(config: RunnableConfig) -> list[dict]:
    """Fetch all information for the user along with corresponding cart information.

    Returns:
        A list of dictionaries where each dictionary contains the order details,
        associated cart details belonging to the user.
    """
    try:
        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return json.dumps({
                "status": "error",
                "message": "No user ID configured"
            })

        conn = get_db()
        cursor = conn.cursor()

        query = """
        SELECT 
            u.id as user_id, u.name as user_name,u.email,
            o.id as order_id,o.total_amount,o.status as order_status,o.created_at as order_date,
            oi.product_id,oi.quantity as order_quantity,oi.price_at_time as order_price,
            ci.id as cart_item_id,ci.quantity as cart_quantity,ci.price_at_time as cart_price,
            p.name as product_name,p.description as product_description
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN cart_items ci ON u.id = ci.user_id
        LEFT JOIN products p ON p.id = COALESCE(oi.product_id, ci.product_id)
        WHERE u.id = ?
        """
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        return json.dumps({
            "status": "success",
            "data": {
                "user_info": results[0] if results else {},
                "orders": [r for r in results if r.get('order_id')],
                "cart_items": [r for r in results if r.get('cart_item_id')]
            }
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
def get_order_status(order_id: str, *, config: Dict) -> str:
    """Get detailed order status"""
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
            SELECT 
                o.*,
                json_group_array(
                    json_object(
                        'product_id', oi.product_id,
                        'quantity', oi.quantity,
                        'price', oi.price_at_time,
                        'product_name', p.name
                    )
                ) as items
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.id = ? AND o.user_id = ?
            GROUP BY o.id
        """, (order_id, user_id))

        result = cursor.fetchone()
        if not result:
            return json.dumps({
                "status": "error",
                "message": f"Order {order_id} not found"
            })

        return json.dumps({
            "status": "success",
            "data": dict(zip(
                ['id', 'user_id', 'total_amount', 'status', 'created_at', 'items'],
                result
            ))
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
    finally:
        cursor.close()
        conn.close()