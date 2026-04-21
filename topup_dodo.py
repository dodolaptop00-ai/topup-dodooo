import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "kunci_rahasia_anda_123"

# --- DATABASE CONFIGURATION (SQLite) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'store.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50)) # 'rental' atau 'topup'
    game_name = db.Column(db.String(100))
    item_name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    detail = db.Column(db.String(200)) # durasi atau jumlah diamond

# --- LOGIN PROTECTOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- CSS STYLING (UI PREMIUM) ---
CSS = """
<style>
    :root { --primary: #3b82f6; --accent: #10b981; --dark: #0f172a; --card: #1e293b; --text: #f8fafc; }
    body { font-family: 'Poppins', sans-serif; background: var(--dark); color: var(--text); margin: 0; }
    .navbar { background: var(--card); padding: 1rem 5%; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--primary); sticky: top; }
    .navbar a { color: var(--text); text-decoration: none; font-weight: bold; margin-left: 20px; }
    .container { width: 90%; max-width: 1000px; margin: 30px auto; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .card { background: var(--card); border-radius: 15px; padding: 20px; border: 1px solid #334155; transition: 0.3s; position: relative; overflow: hidden; }
    .card:hover { transform: translateY(-5px); border-color: var(--primary); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    .badge { background: var(--primary); padding: 5px 12px; border-radius: 20px; font-size: 0.7rem; text-transform: uppercase; }
    .price { font-size: 1.5rem; color: var(--accent); font-weight: 800; margin: 15px 0; }
    .btn { display: block; width: 100%; text-align: center; background: var(--primary); color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; border: none; cursor: pointer; }
    .btn-wa { background: #25d366; }
    .btn-admin { background: #ef4444; margin-top: 10px; }
    input, select { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; }
    table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 10px; overflow: hidden; }
    th, td { padding: 15px; text-align: left; border-bottom: 1px solid #334155; }
    .form-box { background: var(--card); padding: 30px; border-radius: 15px; max-width: 500px; margin: auto; }
</style>
"""

# --- ROUTES ---

@app.route('/')
def buyer_home():
    products = Product.query.all()
    rental = [p for p in products if p.category == 'rental']
    topup = [p for p in products if p.category == 'topup']
    
    html = f"""
    {CSS}
    <div class="navbar">
        <div style="font-size: 1.5rem;">🎮 <b>GAMESTORE</b></div>
        <div><a href="/">HOME</a><a href="/admin">ADMIN</a></div>
    </div>
    <div class="container">
        <h2 style="border-left: 5px solid var(--primary); padding-left: 15px;">🔥 RENTAL AKUN FREE FIRE</h2>
        <div class="grid">
            {" ".join([f'''
            <div class="card">
                <span class="badge">FF RENTAL</span>
                <h3>{p.item_name}</h3>
                <p><small>Durasi: {p.detail}</small></p>
                <div class="price">Rp {p.price:,}</div>
                <a href="https://wa.me Admin, saya ingin sewa {p.item_name}" class="btn btn-wa">Sewa Via WA</a>
            </div>
            ''' for p in rental])}
        </div>

        <h2 style="border-left: 5px solid var(--accent); padding-left: 15px; margin-top: 50px;">💎 TOPUP ALL GAME</h2>
        <div class="grid">
            {" ".join([f'''
            <div class="card">
                <span class="badge" style="background:var(--accent)">{p.game_name}</span>
                <h3>{p.item_name}</h3>
                <p><small>Layanan: {p.game_name}</small></p>
                <div class="price">Rp {p.price:,}</div>
                <a href="https://wa.me Admin, saya ingin beli {p.item_name} {p.game_name}" class="btn btn-wa">Beli Via WA</a>
            </div>
            ''' for p in topup])}
        </div>
    </div>
    """
    return html

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['pass'] == '123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Salah Username/Password!")
    
    return f"""
    {CSS}
    <div class="container" style="margin-top: 100px;">
        <div class="form-box">
            <h2 style="text-align:center">Admin Login</h2>
            <form method="post">
                <input type="text" name="user" placeholder="Username" required>
                <input type="password" name="pass" placeholder="Password" required>
                <button type="submit" class="btn">MASUK KE PANEL</button>
            </form>
        </div>
    </div>
    """

@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    rows = ""
    for p in products:
        rows += f"""
        <tr>
            <td>{p.id}</td>
            <td>{p.category.upper()}</td>
            <td>{p.game_name if p.game_name else '-'}</td>
            <td>{p.item_name}</td>
            <td>Rp {p.price:,}</td>
            <td>
                <a href="/delete/{p.id}" class="btn btn-admin" style="display:inline; padding: 5px 10px;">Hapus</a>
            </td>
        </tr>
        """

    return f"""
    {CSS}
    <div class="navbar">
        <b>PANEL KONTROL ADMIN</b>
        <div><a href="/">LIHAT TOKO</a><a href="/logout" style="color: #ef4444;">LOGOUT</a></div>
    </div>
    <div class="container">
        <div class="form-box" style="max-width: 100%; margin-bottom: 30px;">
            <h3>➕ Tambah Produk Baru</h3>
            <form action="/add" method="post" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <select name="category" style="width: 150px;"><option value="rental">Rental</option><option value="topup">Topup</option></select>
                <input type="text" name="game_name" placeholder="Nama Game (Misal: Free Fire)" style="width: 200px;">
                <input type="text" name="item_name" placeholder="Nama Item (Misal: 140 DM)" style="width: 200px;" required>
                <input type="number" name="price" placeholder="Harga" style="width: 150px;" required>
                <input type="text" name="detail" placeholder="Detail (Misal: 24 Jam)" style="width: 150px;">
                <button type="submit" class="btn" style="width: 120px;">Tambah</button>
            </form>
        </div>
        <table>
            <tr><th>ID</th><th>Tipe</th><th>Game</th><th>Item</th><th>Harga</th><th>Aksi</th></tr>
            {rows}
        </table>
    </div>
    """

@app.route('/add', methods=['POST'])
@login_required
def add_product():
    new_p = Product(
        category=request.form['category'],
        game_name=request.form['game_name'],
        item_name=request.form['item_name'],
        price=int(request.form['price']),
        detail=request.form['detail']
    )
    db.session.add(new_p)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:id>')
@login_required
def delete_product(id):
    p = Product.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('buyer_home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Membuat database otomatis jika belum ada
    app.run(debug=True)
