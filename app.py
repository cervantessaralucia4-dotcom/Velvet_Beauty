from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'velvet_beauty_secret_2024'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# CONFIG MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'velvet_beauty'

mysql = MySQL(app)

# ─────────────────────────────────────────
# HOME
# ─────────────────────────────────────────

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, name, brand, description, price, stock, category_id, main_image
        FROM products
    """)
    products = cursor.fetchall()
    cursor.close()
    return render_template('index.html', products=products)

# ─────────────────────────────────────────
# DETALLE DE PRODUCTO
# ─────────────────────────────────────────

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.brand, p.description, p.price, p.stock,
               p.category_id, p.main_image, c.name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
    """, (product_id,))

    product = cursor.fetchone()
    cursor.close()

    if not product:
        return redirect('/')

    category_name = product[8] if product[8] else 'Sin categoría'

    return render_template('product.html', product=product, category_name=category_name)

# ─────────────────────────────────────────
# CARRITO (usando sesión)
# ─────────────────────────────────────────

@app.route('/cart')
def cart():
    cart = session.get('cart', {})

    if not cart:
        return render_template('cart.html', items=[], total=0)

    cursor = mysql.connection.cursor()
    items = []
    total = 0

    for product_id, quantity in cart.items():
        cursor.execute("""
            SELECT id, name, brand, price, main_image
            FROM products WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if product:
            subtotal = float(product[3]) * quantity
            total += subtotal
            items.append({
                'product_id': product[0],
                'name':       product[1],
                'brand':      product[2],
                'price':      float(product[3]),
                'image':      product[4],
                'quantity':   quantity,
                'subtotal':   subtotal
            })

    cursor.close()
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = str(request.form['product_id'])
    quantity   = int(request.form.get('quantity', 1))

    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart

    return redirect('/cart')


@app.route('/cart/update', methods=['POST'])
def cart_update():
    product_id = str(request.form['product_id'])
    quantity   = int(request.form['quantity'])

    cart = session.get('cart', {})
    if quantity > 0:
        cart[product_id] = quantity
    else:
        cart.pop(product_id, None)
    session['cart'] = cart

    return redirect('/cart')


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    product_id = str(request.form['product_id'])
    cart = session.get('cart', {})
    cart.pop(product_id, None)
    session['cart'] = cart

    return redirect('/cart')

# ─────────────────────────────────────────
# ADMIN — DASHBOARD
# ─────────────────────────────────────────

@app.route('/admin/dashboard')
def dashboard():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT name, brand, price, stock
        FROM products ORDER BY id DESC LIMIT 5
    """)
    recent_products = cursor.fetchall()

    cursor.close()
    return render_template('admin/dashboard.html',
                           total_products=total_products,
                           recent_products=recent_products)

# ─────────────────────────────────────────
# ADMIN — LISTA DE PRODUCTOS
# ─────────────────────────────────────────

@app.route('/admin/products')
def admin_products():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.brand, p.price, p.stock,
               p.main_image, c.name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
    """)
    products = cursor.fetchall()
    cursor.close()
    return render_template('admin/products.html', products=products)

# ─────────────────────────────────────────
# ADMIN — AGREGAR PRODUCTO
# ─────────────────────────────────────────

@app.route('/admin/add-product')
def add_product():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    return render_template('admin/add_product.html', categories=categories)


@app.route('/save-product', methods=['POST'])
def save_product():
    name        = request.form['name']
    brand       = request.form['brand']
    description = request.form['description']
    price       = request.form['price']
    stock       = request.form['stock']
    category_id = request.form['category_id']

    image    = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    db_path = f"uploads/{filename}"

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO products(name, brand, description, price, stock, category_id, main_image)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """, (name, brand, description, price, stock, category_id, db_path))
    mysql.connection.commit()
    cursor.close()

    return redirect('/admin/products')

# ─────────────────────────────────────────
# ADMIN — EDITAR PRODUCTO
# ─────────────────────────────────────────

@app.route('/admin/edit-product/<int:product_id>')
def edit_product(product_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, name, brand, description, price, stock, category_id, main_image
        FROM products WHERE id = %s
    """, (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    cursor.close()
    return render_template('admin/edit_product.html',
                           product=product,
                           categories=categories)


@app.route('/update-product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    name        = request.form['name']
    brand       = request.form['brand']
    description = request.form['description']
    price       = request.form['price']
    stock       = request.form['stock']
    category_id = request.form['category_id']

    cursor = mysql.connection.cursor()

    image = request.files.get('image')
    if image and image.filename:
        filename  = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        db_path = f"uploads/{filename}"
        cursor.execute("""
            UPDATE products
            SET name=%s, brand=%s, description=%s, price=%s,
                stock=%s, category_id=%s, main_image=%s
            WHERE id=%s
        """, (name, brand, description, price, stock, category_id, db_path, product_id))
    else:
        cursor.execute("""
            UPDATE products
            SET name=%s, brand=%s, description=%s,
                price=%s, stock=%s, category_id=%s
            WHERE id=%s
        """, (name, brand, description, price, stock, category_id, product_id))

    mysql.connection.commit()
    cursor.close()

    return redirect('/admin/products')

# ─────────────────────────────────────────
# ADMIN — ELIMINAR PRODUCTO
# ─────────────────────────────────────────

@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/admin/products')


if __name__ == '__main__':
    app.run(debug=True)