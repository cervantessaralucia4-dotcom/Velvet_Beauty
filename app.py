from flask import Flask, render_template
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# CONFIG MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'velvet_beauty'

mysql = MySQL(app)

# HOME 

@app.route('/')
def home():
    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT
        id,
        name,
        brand,
        description,
        price,
        stock,
        category_id,
        main_image
    FROM products
""")

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        'index.html',
        products=products
        )

@app.route('/admin/add-product')
def add_product():

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM categories")

    categories = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin/add_product.html',
        categories=categories
    )

from flask import request, redirect

@app.route('/save-product', methods=['POST'])
def save_product():

    name = request.form['name']
    brand = request.form['brand']
    description = request.form['description']
    price = request.form['price']
    stock = request.form['stock']
    category_id = request.form['category_id']

    image = request.files['image']

    filename = secure_filename(image.filename)

    image_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )

    image.save(image_path)

    db_path = f"uploads/products/{filename}"

    cursor = mysql.connection.cursor()

    query = """
        INSERT INTO products(
            name,
            brand,
            description,
            price,
            stock,
            category_id,
            main_image
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        name,
        brand,
        description,
        price,
        stock,
        category_id,
        db_path
    )

    cursor.execute(query, values)

    mysql.connection.commit()

    cursor.close()

    return redirect('/')

@app.route('/admin/dashboard')
def dashboard():

    cursor = mysql.connection.cursor()

    # TOTAL PRODUCTOS

    cursor.execute("SELECT COUNT(*) FROM products")

    total_products = cursor.fetchone()[0]

    # PRODUCTOS RECIENTES

    cursor.execute("""SELECT name, brand, price, stock FROM products ORDER BY id DESC LIMIT 5""")

    recent_products = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        recent_products=recent_products
    )

@app.route('/admin/products')
def admin_products():

    cursor = mysql.connection.cursor()

    query = """
       SELECT 
       products.id, 
       products.name, 
       products.brand, 
       products.price, 
       products.stock, 
       products.main_image,
       categories.name 

       FROM products 
    
       LEFT JOIN categories 
       ON products.category_id = categories.id
       ORDER BY products.id DESC
    """
    cursor.execute(query)

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin/products.html',
        products=products
    )

if __name__ == '__main__':
    app.run(debug=True)
