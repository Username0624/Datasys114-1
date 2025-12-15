from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
# 引入 uuid 用於生成 row 的唯一 ID，替代使用 ObjectId() 轉字串，讓 row ID 更好辨識
import uuid 

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ---------------------------------------------------
# MongoDB Connection
# ---------------------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["datasys114"]
users = db["users"]
forms = db["forms"]

# ---------------------------------------------------
# Pages
# ---------------------------------------------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/form", methods=["GET"])
def form_page():
    return render_template("form.html")


# ---------------------------------------------------
# API: Register
# ---------------------------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email 已被使用"})

    users.insert_one({
        "username": username,
        "email": email,
        "password": password
    })

    return jsonify({"success": True, "message": "註冊成功"})


# ---------------------------------------------------
# API: Login
# ---------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email, "password": password})

    if not user:
        return jsonify({"success": False, "message": "帳號或密碼錯誤"})

    return jsonify({
        "success": True,
        "message": "登入成功",
        "user_id": str(user["_id"]),
        "username": user["username"]
    })


# ---------------------------------------------------
# API: Create Form
# ---------------------------------------------------
@app.route("/create_form", methods=["POST"])
def create_form():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")

    forms.insert_one({
        "title": title,
        "owner": user_id,
        "rows": []
    })

    return jsonify({"success": True, "message": "表單建立成功"})


# ---------------------------------------------------
# API: Get All Forms for User
# ---------------------------------------------------
@app.route("/my_forms/<user_id>", methods=["GET"])
def my_forms(user_id):
    result = []
    # 注意：如果 user_id 是字串形式的 ObjectId，這裡需要轉換
    # 假設您的 user_id 在 forms 裡是字串形式
    for f in forms.find({"owner": user_id}):
        f["_id"] = str(f["_id"])
        result.append(f)
    return jsonify(result)


# ---------------------------------------------------
# API: Add Row (Single)
# ---------------------------------------------------
@app.route("/add_row", methods=["POST"])
def add_row():
    data = request.get_json()
    form_id = data["form_id"]

    row = {
        # 確保 row 有唯一 ID
        "_id": str(ObjectId()), 
        "buyer": data.get("buyer"),
        "item": data.get("item"),
        "quantity": data.get("quantity"),
        "price": data.get("price")
    }

    forms.update_one(
        {"_id": ObjectId(form_id)},
        {"$push": {"rows": row}}
    )

    return jsonify({"success": True, "row_id": row["_id"]})


# ---------------------------------------------------
# 🚀 API: Batch Add Rows (批次新增)
# ---------------------------------------------------
@app.route("/batch_add_rows", methods=["POST"])
def batch_add_rows():
    data = request.get_json()
    form_id = data.get("form_id")
    new_rows_data = data.get("rows", [])
    
    if not form_id or not new_rows_data:
        return jsonify({"success": False, "message": "缺少表單 ID 或新增資料"}), 400

    rows_to_insert = []
    inserted_ids = []
    
    for row_data in new_rows_data:
        # 使用 uuid 確保 row ID 唯一，如果 ObjectId 夠用也可以
        row_id = str(ObjectId()) 
        row = {
            "_id": row_id,
            "buyer": row_data.get("buyer"),
            "item": row_data.get("item"),
            "quantity": row_data.get("quantity"),
            "price": row_data.get("price")
        }
        rows_to_insert.append(row)
        inserted_ids.append(row_id)
        
    # 使用 $push 配合 $each 一次性新增多個元素
    forms.update_one(
        {"_id": ObjectId(form_id)}, 
        {"$push": {"rows": {"$each": rows_to_insert}}}
    )
    
    return jsonify({"success": True, "count": len(rows_to_insert), "inserted_ids": inserted_ids})


# ---------------------------------------------------
# API: Update Row
# ---------------------------------------------------
@app.post("/api/update_row")
def update_row():
    data = request.json
    form_id = data["form_id"]
    index = data["index"]
    
    # 為了保持 _id，需要先找到舊的 row
    form = forms.find_one({"_id": ObjectId(form_id)}, {"rows": 1})
    if not form or index >= len(form.get("rows", [])):
        return jsonify({"status": "error", "message": "找不到表單或索引無效"}), 404
        
    old_row = form["rows"][index]

    new_row = {
        "_id": old_row.get("_id", str(ObjectId())), # 保留舊的 _id
        "buyer": data["buyer"],
        "item": data["item"],
        "quantity": data["quantity"],
        "price": data["price"]
    }

    # 使用 $set 配合陣列索引更新
    forms.update_one(
        {"_id": ObjectId(form_id)},
        {f"$set": {f"rows.{index}": new_row}}
    )

    return jsonify({"status": "ok"})


# ---------------------------------------------------
# API: Delete Row (Single, by Index)
# ---------------------------------------------------
@app.post("/api/delete_row")
def delete_row():
    data = request.json
    form_id = data["form_id"]
    index = data["index"]

    # 用 $unset 清空，再 $pull 移除 null 元素 (這是從索引刪除的標準方式)
    forms.update_one(
        {"_id": ObjectId(form_id)},
        {f"$unset": {f"rows.{index}": 1}}
    )

    forms.update_one(
        {"_id": ObjectId(form_id)},
        {"$pull": {"rows": None}}
    )

    return jsonify({"status": "ok"})


# ---------------------------------------------------
# 🚀 API: Batch Delete Rows (批次刪除)
# ---------------------------------------------------
@app.route("/batch_delete_rows", methods=["POST"])
def batch_delete_rows():
    data = request.get_json()
    form_id = data.get("form_id")
    row_ids_to_delete = data.get("row_ids", []) # 預期傳入要刪除的 row 的 _id (字串列表)

    if not form_id or not row_ids_to_delete:
        return jsonify({"success": False, "message": "缺少表單 ID 或刪除列表"}), 400
    
    # 使用 $pull operator 根據 rows 陣列中元素的 _id 欄位來移除匹配的元素
    forms.update_one(
        {"_id": ObjectId(form_id)},
        {"$pull": {"rows": {"_id": {"$in": row_ids_to_delete}}}}
    )
    
    return jsonify({"success": True, "message": f"嘗試刪除 {len(row_ids_to_delete)} 筆資料"})


# ---------------------------------------------------
# API: Clear All Rows (Assignment)
# ---------------------------------------------------
@app.route("/clear_form/<form_id>", methods=["DELETE"])
def clear_form(form_id):
    forms.update_one(
        {"_id": ObjectId(form_id)},
        {"$set": {"rows": []}}
    )
    return jsonify({"success": True})


# ---------------------------------------------------
# Run Server
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)