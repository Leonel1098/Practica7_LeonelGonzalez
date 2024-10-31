from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from pymongo import MongoClient
from db_mongo import load_csv_data, load_mongo_data
from calculos import calculate_nomina
from operaciones_Mongo import save_to_mongo, load_mongo_data, update_mongo_data, delete_from_mongo
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Realizando la Conexión a MongoDB
client = MongoClient('mongodb+srv://gonzalezleonel1098:Leonel10@cluster0.uapuf.mongodb.net/?authMechanism=DEFAULT')
db = client['Empresa']
collection_name = 'Empleados'
csv_file_path = 'Empleados.csv'

def save_to_csv(data, file_path):
    data.to_csv(file_path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Cargar y guardar datos desde el archivo CSV
    data = load_csv_data(file)
    save_to_mongo(db, collection_name, data)
    save_to_csv(data, csv_file_path)
    
    flash('Archivo cargado y datos almacenados exitosamente')
    return redirect(url_for('view_raw_data'))

@app.route('/view_raw_data')
def view_raw_data():
    # Obtener datos de MongoDB
    data = load_mongo_data(db, collection_name)
    return render_template('mostrar.html', data=data)

@app.route('/create', methods=['POST'])
def create_employee():
    # Crear un nuevo empleado
    nombre = request.form['nombre']
    salario_por_hora = float(request.form['salario_por_hora'])
    horas_trabajadas = int(request.form['horas_trabajadas'])
    
    new_data = pd.DataFrame([{
        'Nombre': nombre,
        'Salario por Hora': salario_por_hora,
        'Horas Trabajadas': horas_trabajadas
    }])
    
    save_to_mongo(db, collection_name, new_data)
    
    # Actualizar CSV
    current_data = load_mongo_data(db, collection_name)
    save_to_csv(current_data, csv_file_path)
    
    flash('Empleado creado exitosamente')
    return redirect(url_for('view_raw_data'))

@app.route('/update_employee', methods=['POST'])
def update_employee():
    # Actualizar datos del empleado
    nombre = request.form['nombre']
    salario_por_hora = float(request.form['salario_por_hora'])
    horas_trabajadas = int(request.form['horas_trabajadas'])
    
    update_mongo_data(db, collection_name, nombre, salario_por_hora, horas_trabajadas)
    
    # Actualizar CSV
    current_data = load_mongo_data(db, collection_name)
    save_to_csv(current_data, csv_file_path)
    
    flash('Empleado actualizado exitosamente')
    return redirect(url_for('view_raw_data'))

@app.route('/delete_employee/<nombre>', methods=['POST'])
def delete_employee(nombre):
    # Eliminar empleado
    delete_from_mongo(db, collection_name, nombre)
    
    # Actualizar CSV
    current_data = load_mongo_data(db, collection_name)
    save_to_csv(current_data, csv_file_path)
    
    flash(f'Empleado {nombre} eliminado exitosamente')
    return redirect(url_for('view_raw_data'))

@app.route('/view_results')
def view_results():
    # Cargar los datos de nómina desde MongoDB para visualizarlos
    data = load_mongo_data(db, 'nomina_resultados')
    #print("Datos de nómina recuperados:", data)
    return render_template('resultados.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)


# Distribución de Deducciones print("\nDistribución de Deducciones (Total y Porcentaje Promedio):") distribucion_deducciones = collection.aggregate([ { "$group": { "_id": None, "Total_IGSS": {"$sum": "$Deducciones.IGSS"}, "Total_ISR": {"$sum": "$Deducciones.ISR"}, "Total_Deducciones": {"$sum": "$Deducciones.Total Deducciones"}, "Promedio_IGSS": {"$avg": "$Deducciones.IGSS"}, "Promedio_ISR": {"$avg": "$Deducciones.ISR"} } }, { "$project": { "Total_IGSS": 1, "Total_ISR": 1, "Promedio_IGSS": 1, "Promedio_ISR": 1, "Porcentaje_IGSS": {"$multiply": [{"$divide": ["$Promedio_IGSS", "$Total_Deducciones"]}, 100]}, "Porcentaje_ISR": {"$multiply": [{"$divide": ["$Promedio_ISR", "$Total_Deducciones"]}, 100]} } } ])
#for deduccion in distribucion_deducciones: print(f"Total IGSS: {deduccion['Total_IGSS']}") print(f"Total ISR: {deduccion['Total_ISR']}") print(f"Porcentaje Promedio IGSS: {deduccion['Porcentaje_IGSS']:.2f}%") print(f"Porcentaje Promedio ISR: {deduccion['Porcentaje_ISR']:.2f}%")
#db.Planilla.aggregate([
    #{$group:{_id:null,totalIGSS:{$sum:"$Detalle de Deducciones.IGSS"},promedioIGSS:{$avg:"$Detalle de Deducciones.IGSS"},
    #totalISR:{$sum:"$Detalle de Deducciones.ISR"},promedioISR:{$avg:"$Detalle de Deducciones.ISR"}}},
    #{$project:{_id:0}}
#])