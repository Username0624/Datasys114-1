from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# ------------------ MySQL 連線設定 ------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="41271223H",  
    database="hw2_db"    
)
cursor = db.cursor(dictionary=True)


# =====================================================
#  customers CRUD
# =====================================================
@app.post("/customers")
def create_customer():
    data = request.json
    sql = "INSERT INTO customers (name, phone) VALUES (%s, %s)"
    cursor.execute(sql, (data["name"], data["phone"]))
    db.commit()
    return jsonify({"message": "Customer created"})


@app.get("/customers")
def get_customers():
    cursor.execute("SELECT * FROM customers")
    return jsonify(cursor.fetchall())


@app.put("/customers/<int:id>")
def update_customer(id):
    data = request.json
    sql = "UPDATE customers SET name=%s, phone=%s WHERE id=%s"
    cursor.execute(sql, (data["name"], data["phone"], id))
    db.commit()
    return jsonify({"message": "Customer updated"})


@app.delete("/customers/<int:id>")
def delete_customer(id):
    cursor.execute("DELETE FROM customers WHERE id=%s", (id,))
    db.commit()
    return jsonify({"message": "Customer deleted"})


# =====================================================
#  orders CRUD
# =====================================================
@app.post("/orders")
def create_order():
    data = request.json
    sql = "INSERT INTO orders (customer_id, order_date, total_amount) VALUES (%s, %s, %s)"
    cursor.execute(sql, (data["customer_id"], data["order_date"], data["total_amount"]))
    db.commit()
    return jsonify({"message": "Order created"})


@app.get("/orders")
def get_orders():
    cursor.execute("SELECT * FROM orders")
    return jsonify(cursor.fetchall())


@app.put("/orders/<int:id>")
def update_order(id):
    data = request.json
    sql = "UPDATE orders SET customer_id=%s, order_date=%s, total_amount=%s WHERE id=%s"
    cursor.execute(sql, (data["customer_id"], data["order_date"], data["total_amount"], id))
    db.commit()
    return jsonify({"message": "Order updated"})


@app.delete("/orders/<int:id>")
def delete_order(id):
    cursor.execute("DELETE FROM orders WHERE id=%s", (id,))
    db.commit()
    return jsonify({"message": "Order deleted"})


# =====================================================
#  order_items CRUD
# =====================================================
@app.post("/order_items")
def create_item():
    data = request.json
    sql = "INSERT INTO order_items (order_id, product_name, price, qty) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (data["order_id"], data["product_name"], data["price"], data["qty"]))
    db.commit()
    return jsonify({"message": "Item created"})


@app.get("/order_items")
def get_items():
    cursor.execute("SELECT * FROM order_items")
    return jsonify(cursor.fetchall())


@app.put("/order_items/<int:id>")
def update_item(id):
    data = request.json
    sql = "UPDATE order_items SET order_id=%s, product_name=%s, price=%s, qty=%s WHERE id=%s"
    cursor.execute(sql, (data["order_id"], data["product_name"], data["price"], data["qty"], id))
    db.commit()
    return jsonify({"message": "Item updated"})


@app.delete("/order_items/<int:id>")
def delete_item(id):
    cursor.execute("DELETE FROM order_items WHERE id=%s", (id,))
    db.commit()
    return jsonify({"message": "Item deleted"})


# =====================================================
#  JOIN API（作業要求）
# =====================================================
@app.get("/orders_with_customer")
def orders_with_customer():
    cursor.execute("""
        SELECT 
            orders.id AS order_id,
            customers.name AS customer_name,
            orders.order_date,
            orders.total_amount
        FROM orders
        INNER JOIN customers ON orders.customer_id = customers.id
    """)
    return jsonify(cursor.fetchall())


# ------------------ 啟動 Flask ------------------
if __name__ == "__main__":
    app.run(debug=True)
