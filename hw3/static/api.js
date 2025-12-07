const API = "http://127.0.0.1:5000";

async function apiRegister(username, email, password){
    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, email, password})
    });
    return res.json();
}

async function apiLogin(email, password){
    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });
    return res.json();
}

async function apiCreateForm(user_id, title){
    const res = await fetch(`${API}/create_form`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id, title})
    });
    return res.json();
}

async function apiGetMyForms(user_id){
    const res = await fetch(`${API}/my_forms/${user_id}`);
    return res.json();
}

async function apiAddRow(form_id, buyer, item, quantity, price){
    const res = await fetch(`${API}/add_row`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({form_id, buyer, item, quantity, price})
    });
    return res.json();
}

async function apiUpdateRow(form_id, index, buyer, item, quantity, price){
    const res = await fetch(`${API}/api/update_row`, {
        method: "POST",   // ★ 重要：後端用 POST，不是 PUT
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({form_id, index, buyer, item, quantity, price})
    });
    return res.json();
}

async function apiDeleteRow(form_id, index){
    const res = await fetch(`${API}/api/delete_row`, {   // ← 多 /api
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({form_id, index})
    });
    return res.json();
}

async function apiClearForm(form_id){
    const res = await fetch(`${API}/clear_form/${form_id}`, {
        method: "DELETE"
    });
    return res.json();
}
