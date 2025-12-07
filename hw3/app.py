from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

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
    for f in forms.find({"owner": user_id}):
        f["_id"] = str(f["_id"])
        result.append(f)
    return jsonify(result)


# ---------------------------------------------------
# API: Add Row
# ---------------------------------------------------
@app.route("/add_row", methods=["POST"])
def add_row():
    data = request.get_json()
    form_id = data["form_id"]

    row = {
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

    return jsonify({"success": True})


# ---------------------------------------------------
# API: Update Row
# ---------------------------------------------------
@app.post("/api/update_row")
def update_row():
    data = request.json
    form_id = data["form_id"]
    index = data["index"]

    new_row = {
        "buyer": data["buyer"],
        "item": data["item"],
        "quantity": data["quantity"],
        "price": data["price"]
    }

    forms.update_one(
        {"_id": ObjectId(form_id)},
        {f"$set": {f"rows.{index}": new_row}}
    )

    return jsonify({"status": "ok"})



# ---------------------------------------------------
# API: Delete Row
# ---------------------------------------------------
@app.post("/api/delete_row")
def delete_row():
    data = request.json
    form_id = data["form_id"]
    index = data["index"]

    # 用 $unset 清空，再拉起來避免 null 破壞格式
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
