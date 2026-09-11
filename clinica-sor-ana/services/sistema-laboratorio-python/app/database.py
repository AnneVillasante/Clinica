import os
from mysql.connector import pooling


_pool = pooling.MySQLConnectionPool(pool_name='laboratorio_pool', pool_size=5, host=os.getenv('DB_HOST', '127.0.0.1'), user=os.getenv('DB_USER', 'root'), password=os.getenv('DB_PASSWORD', 'Sapphire_27'), database='bd_laboratorio')

def connection():
    return _pool.get_connection()
