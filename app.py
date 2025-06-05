from flask import Flask, flash, redirect, render_template, request, url_for, jsonify
import psycopg2

# Connect DATABASE
host = "localhost"
port = "5432"
database = "rauchim_db"
user = "lavr"
password = "2587"
conn_str = "host={} port={} dbname={} user={} password={}".format(host, port, database, user, password)

res_data_products = []*0
res_add_products = []*0

app = Flask(__name__)
app.secret_key = 'some_secret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_form', methods=['POST'])
def load_form():
    data_form = request.get_json()
    data = render_template('form_' + data_form + '.html')
    return jsonify({'data': data})

@app.route('/get_record', methods=['POST'])
def get_record():
    data_request = request.get_json()
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(("SELECT * FROM {} WHERE id = {}").format(data_request['name_table'], data_request['id']))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'data': data})

@app.route('/get_record_column', methods=['POST'])
def get_record_column():
    data_request = request.get_json()
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(("SELECT {} FROM {} WHERE id = {}").format(data_request['name_column'], data_request['name_table'], data_request['id']))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'data': data})

@app.route('/get_records', methods=['POST'])
def get_records():
    data_request = request.get_json()
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(("SELECT * FROM {}").format(data_request))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'data': data})

@app.route('/get_records_technical_map', methods=['POST'])
def get_records_technical_map():
    data_request = request.get_json()
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(("SELECT * FROM technical_maps WHERE product_id = {}").format(data_request))
    data_tm = cur.fetchall()

    data_la = []
    for i in range(len(data_tm)):
        cur.execute(("SELECT * FROM list_of_actions WHERE technical_maps_id = {}").format(data_tm[i][0]))
        data_la.append(cur.fetchall())
    
    cur.close()
    conn.close()
    return jsonify({'data_tm': data_tm, 'data_la': data_la})

@app.route('/get_records_recipes', methods=['POST'])
def get_records_recipes():
    data_request = request.get_json()
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(("SELECT * FROM recipes WHERE recipes_id = {}").format(data_request))
    data_tm = cur.fetchall()

    data_la = []
    for i in range(len(data_tm)):
        cur.execute(("SELECT * FROM list_of_raw_materials WHERE recipes_id = {}").format(data_tm[i][0]))
        data_la.append(cur.fetchall())
    
    cur.close()
    conn.close()
    return jsonify({'data_tm': data_tm, 'data_la': data_la})

@app.route('/add_record', methods=['POST'])
def add_record():
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    data_request = request.get_json()

    # Проверка ключа на уникальность
    cur.execute("SELECT id FROM {} WHERE id = {}".format(data_request['name_table'], data_request['id']))
    data = cur.fetchall()
    if (len(data) != 0):
        return jsonify({'data': 0})
    
    # Сохранение данных
    cur.execute("INSERT INTO {} VALUES({})".format(data_request['name_table'], data_request['str_req']))
    data = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'data': data})

@app.route('/get_records_file', methods=['POST'])
def get_records_file():
    data_request = request.get_json()
    print(data_request['name_table'])

    with open('rules_file.txt', 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if lines[i].strip() == data_request['name_table']:
                if i + 1 < len(lines):
                    d_table = lines[i + 1].strip()
                else:
                    print("Следующей строки нет.")
            elif lines[i].strip() == data_request['name_column']:
                if i + 1 < len(lines):
                    d_column = lines[i + 1].strip()
                else:
                    print("Следующей строки нет.")
        
    return jsonify({'data_table': d_table, 'data_column': d_column})

@app.route('/remove_record', methods=['POST'])
def remove_record():
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    data_form = request.get_json()
    rem_id = data_form['formRemId']
    name_table = data_form['nameTable']
    
    # Поиск записи
    cur.execute("SELECT id FROM {} WHERE id = {}".format(name_table, rem_id))
    data = cur.fetchall()
    if (len(data) == 0):
        return jsonify({'data': 0})
    
    # Удаление записи
    cur.execute("DELETE FROM {} WHERE id = {}".format(name_table, rem_id))
    data = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'data': data})

if __name__ == "__main__":
    app.run(debug=True)
