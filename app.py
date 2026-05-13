from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

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

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        'index.html',
        products=products
        )

if __name__ == '__main__':
    app.run(debug=True)