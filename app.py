from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from pymongo import MongoClient
from db_mongo import load_csv_data, load_mongo_data
from calculos import calculate_nomina
from operaciones_Mongo import save_to_mongo, get_aggregation_results, update_mongo_data

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Conexión a MongoDB
client = MongoClient('mongodb+srv://gonzalezleonel1098:Leonel10@cluster0.uapuf.mongodb.net/?authMechanism=DEFAULT')
db = client['Empresa']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Procesar archivo CSV y guardar en MongoDB
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    data = load_csv_data(file)
    data = calculate_nomina(data)
    save_to_mongo(db, 'nomina_resultados', data)
    
    flash('Archivo procesado y datos almacenados exitosamente')
    return redirect(url_for('view_results'))

@app.route('/view_results')
def view_results():
    # Consultar los resultados de la nómina en MongoDB
    data = load_mongo_data(db, 'nomina_resultados')
    return render_template('resultados.html', data=data)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        nuevo_salario = float(request.form['salario'])
        nuevas_horas = int(request.form['horas'])
        update_mongo_data(db, 'nomina_resultados', nombre, nuevo_salario, nuevas_horas)
        
        flash('Datos actualizados exitosamente')
        return redirect(url_for('view_results'))
    
    return render_template('actualizar.html')

@app.route('/aggregations')
def aggregations():
    # Realizar consultas de agregación
    results = get_aggregation_results(db, 'nomina_resultados')
    return render_template('resultados.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
