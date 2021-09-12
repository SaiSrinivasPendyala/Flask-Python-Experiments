from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'b27'
app.config['MYSQL_DATABASE_PASSWORD'] = 'b27'
app.config['MYSQL_DATABASE_DB'] = 'dbSrinivas'
app.config['MYSQL_DATABASE_HOST'] = '165.22.14.77'

mysql.init_app(app)