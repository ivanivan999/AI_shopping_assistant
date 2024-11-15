# app/models/product.py

import sqlite3
from typing import Dict, Optional, List
import json
from langchain_core.tools import tool

def get_db():
    return sqlite3.connect('data/shopping.db')

@tool
def search_products(
    name: Optional[str] = None,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_inventory: Optional[int] = None
) -> str:
    """Search products with filters and word matching"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        print("search_products")
        query = """
        SELECT 
            p.*,
            pc.name as category_name
        FROM products p
        LEFT JOIN product_categories pc ON p.category_id = pc.id
        WHERE 1=1
        """
        params = []
        
        if name:
            # Split search terms and check both product and category
            search_words = name.lower().split()
            like_conditions = []
            
            for word in search_words:
                like_conditions.append("""
                    (
                        LOWER(p.name) LIKE ? 
                        OR LOWER(p.description) LIKE ?
                        OR LOWER(pc.name) LIKE ?
                    )
                """)
                params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
            
            if like_conditions:
                query += " AND (" + " AND ".join(like_conditions) + ")"
        
        if min_price is not None:
            query += " AND p.price >= ?"
            params.append(float(min_price))
            
        if max_price is not None:
            query += " AND p.price <= ?"
            params.append(float(max_price))
            
        if min_inventory:
            query += " AND p.inventory >= ?"
            params.append(min_inventory)
            
        cursor.execute(query, params)
        results = [
            dict(zip(
                ('id', 'name', 'description', 'price', 'category_id', 'inventory', 'category_name'),
                row
            ))
            for row in cursor.fetchall()
        ]
        
        return json.dumps({
            "status": "success",
            "data": results
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
def get_product_details(product_id: str) -> str:
    """Get detailed product information"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            p.*,
            pc.name as category_name,
            (
                SELECT COUNT(*)
                FROM order_items oi
                WHERE oi.product_id = p.id
            ) as times_purchased
        FROM products p
        LEFT JOIN product_categories pc ON p.category_id = pc.id
        WHERE p.id = ?
        """, (product_id,))
        
        result = cursor.fetchone()
        if not result:
            return json.dumps({
                "status": "error",
                "message": f"Product {product_id} not found"
            })

        return json.dumps({
            "status": "success",
            "data": dict(zip(
                ('id', 'name', 'description', 'price', 'category_id', 'inventory', 
                 'category_name', 'times_purchased'),
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

@tool
def search_products_with_recommendations(
    search_term: str,
    limit: int = 5,
) -> List[Dict]:
    """
    Search products by name/description similarity and include recommendations
    
    Args:
        search_term: Text to search for in product name/description
        limit: Maximum number of results to return
    Returns:
        List of products sorted by relevance score
    """
    conn = get_db()
    cursor = conn.cursor()
    print("search_products_with_recommendations")

    try:
        # Using LIKE with wildcards for basic text matching
        # Adding relevance scoring based on match location
        query = """
        WITH matched_products AS (
            SELECT 
                p.*,
                CASE 
                    WHEN p.name LIKE ? THEN 3  -- Exact name match
                    WHEN p.name LIKE ? THEN 2  -- Name contains term
                    WHEN p.description LIKE ? THEN 1  -- Description contains term
                    ELSE 0
                END as relevance_score,
                pc.name as category_name
            FROM products p
            LEFT JOIN product_categories pc ON p.category_id = pc.id
            WHERE 
                p.name LIKE ? OR 
                p.name LIKE ? OR 
                p.description LIKE ?
        )
        SELECT 
            id, name, description, price, 
            category_id, inventory, 
            category_name, relevance_score
        FROM matched_products
        ORDER BY relevance_score DESC, name ASC
        LIMIT ?
        """
        
        search_patterns = [
            f"{search_term}",         # Exact match
            f"%{search_term}%",       # Contains term
            f"%{search_term}%"        # Description contains
        ]
        
        cursor.execute(query, 
                      search_patterns + 
                      search_patterns + 
                      [limit])

        columns = [
            'id', 'name', 'description', 'price',
            'category_id', 'inventory', 'category_name',
            'relevance_score'
        ]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    except Exception as e:
        return f"Error searching products: {str(e)}"
    finally:
        cursor.close()
        conn.close()