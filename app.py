from statistics import median
from bson import ObjectId
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
collection_name = "Empleados"
collection_name2 = db["Empleados"]
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
    
    # Cargar datos desde el archivo CSV
    data = load_csv_data(file)
    
    # Guardar los datos originales en la colección 'Empleados'
    save_to_mongo(db, collection_name, data)
    
    # Guardar los datos en el archivo CSV localmente
    save_to_csv(data, csv_file_path)
    
    # Calcular nómina
    calculated_data = calculate_nomina(data)  # Aplica la función de cálculo de nómina
    
    # Guardar los datos calculados en la colección 'nomina_resultados'
    save_to_mongo(db, 'nomina_resultados', calculated_data)
    
    flash('Archivo cargado, datos almacenados y nómina calculada exitosamente')
    return redirect(url_for('view_raw_data'))


@app.route('/view_raw_data')
def view_raw_data():
    # Cargar datos desde MongoDB
    data = load_mongo_data(db, collection_name)
    print("Datos cargados desde MongoDB:", data)  # Para verificar la carga

    return render_template('mostrar.html', data=data.to_dict(orient='records'))


@app.route('/create', methods=['POST'])
def create_employee():
    # Crear un nuevo empleado
    nombre = request.form['nombre']
    salario_por_hora = float(request.form['salario_por_hora'])
    horas_trabajadas = int(request.form['horas_trabajadas'])
    
    # Crear un DataFrame con la información del nuevo empleado
    new_data = pd.DataFrame([{
        'Nombre': nombre,
        'Salario por Hora': salario_por_hora,
        'Horas Trabajadas': horas_trabajadas
    }])
    
    # Guardar el nuevo empleado en la colección 'Empleados'
    save_to_mongo(db, collection_name, new_data)
    
    # Calcular la nómina para el nuevo empleado y guardarla en 'nomina_resultados'
    nomina_data = calculate_nomina(new_data)
    save_to_mongo(db, 'nomina_resultados', nomina_data)
    
    # Actualizar el archivo CSV con todos los empleados
    current_data = load_mongo_data(db, collection_name)
    save_to_csv(current_data, csv_file_path)
    
    flash('Empleado creado y nómina actualizada exitosamente')
    return redirect(url_for('view_raw_data'))

@app.route('/empleados/editar/<nombre>', methods=['GET', 'POST'])
def editar_empleado(nombre):
    empleado = collection_name2.find_one({"NombreEmpleado": nombre})

    if request.method == 'POST':
        if 'nombre' in request.form:
            nuevo_nombre = request.form['nombre']
            salario_hora = float(request.form['salario_por_hora'])
            horas_trabajadas = int(request.form['horas_trabajadas'])

            collection_name2.update_one(
                {"NombreEmpleado": nombre},
                {"$set": {
                    "NombreEmpleado": nuevo_nombre,
                    "SalarioPorHora": salario_hora,
                    "HorasTrabajadas": horas_trabajadas,
                }}
            )
            flash('Empleado actualizado exitosamente.')
            return redirect(url_for('view_raw_data'))

        else:
            flash('El campo nombre es requerido.')
            return render_template('actualizarEmpleados.html', empleado=empleado)

    return render_template('actualizarEmpleados.html', empleado=empleado)





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
    
    # Verificar si se cargaron datos y transformarlos a lista de diccionarios si es un DataFrame
    if data is not None and not data.empty:
        data = data.to_dict(orient='records')  # Convertir a lista de diccionarios para Jinja2
    else:
        data = []  # Asegurarse de que data sea una lista vacía si no hay datos
    
    # Imprimir los datos para depurar
    print("Datos de nómina recuperados:", data)

    # Renderizar la plantilla con los datos cargados
    return render_template('resultados.html', data=data)


from statistics import median

def get_aggregation_results(db,collection_name2="nomina_resultados"):
    collection = db[collection_name2]  # Cambia a la colección correcta

    # Total y Promedio de Horas Trabajadas
    horas_aggregation = list(collection.aggregate([
        {"$group": {
            "_id": None,
            "total_horas_trabajadas": {"$sum": "$Horas Trabajadas"},
            "promedio_horas_trabajadas": {"$avg": "$Horas Trabajadas"}
        }}
    ]))

    print("Horas Aggregation:", horas_aggregation)  # Depuración

    # Total y Promedio de Salario por Hora
    salario_hora_aggregation = list(collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_por_hora": {"$sum": "$Salario por Hora"},
            "promedio_salario_por_hora": {"$avg": "$Salario por Hora"}
        }}
    ]))

    print("Salario Hora Aggregation:", salario_hora_aggregation)  # Depuración

    # Salario Bruto Total y Promedio
    salario_bruto_aggregation = list(collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_bruto": {"$sum": "$Salario Bruto"},
            "promedio_salario_bruto": {"$avg": "$Salario Bruto"}
        }}
    ]))

    print("Salario Bruto Aggregation:", salario_bruto_aggregation)  # Depuración

    # Salario Neto Total y Promedio
    salario_neto_aggregation = list(collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_neto": {"$sum": "$Salario Neto"},
            "promedio_salario_neto": {"$avg": "$Salario Neto"}
        }}
    ]))

    print("Salario Neto Aggregation:", salario_neto_aggregation)  # Depuración

    # Salario Neto Más Alto y Más Bajo
    salario_neto_min_max = list(collection.aggregate([
        {"$group": {
            "_id": None,
            "salario_neto_mas_alto": {"$max": "$Salario Neto"},
            "salario_neto_mas_bajo": {"$min": "$Salario Neto"}
        }}
    ]))

    print("Salario Neto Min Max:", salario_neto_min_max)  # Depuración

    # Mediana de Salario Neto
    salarios_neto = list(collection.find({}, {"Salario Neto": 1, "_id": 0}))  # Asegúrate del nombre correcto del campo
    if salarios_neto:  # Solo calcula la mediana si hay resultados
        salario_neto_mediana = median([s["Salario Neto"] for s in salarios_neto])
    else:
        salario_neto_mediana = 0  # O un valor que consideres adecuado

    print("Salario Neto Mediana:", salario_neto_mediana)  # Depuración

    # Distribución de Deducciones
    deducciones_aggregation = list(collection.aggregate([
        {"$unwind": "$deducciones"},
        {"$group": {
            "_id": "$deducciones.tipo",
            "total_deducciones": {"$sum": "$Deduccion IGSS"},
            "promedio_deduccion": {"$avg": "$Deduccion IGSS"}
        }}
    ]))

    print("Deducciones Aggregation:", deducciones_aggregation)  # Depuración

    # Convertir resultados a diccionario
    resultados = {
        "horas": horas_aggregation[0] if horas_aggregation else {},
        "salario_hora": salario_hora_aggregation[0] if salario_hora_aggregation else {},
        "salario_bruto": salario_bruto_aggregation[0] if salario_bruto_aggregation else {},
        "salario_neto": salario_neto_aggregation[0] if salario_neto_aggregation else {},
        "salario_neto_min_max": salario_neto_min_max[0] if salario_neto_min_max else {},
        "salario_neto_mediana": salario_neto_mediana,
        "deducciones": deducciones_aggregation
    }

    return resultados



@app.route('/resultados_agregacion')
def resultados_agregacion():
    resultados = get_aggregation_results(db, "nomina_resultados")
    return render_template('mostrar_Consultas.html', resultados=resultados)





if __name__ == '__main__':
    app.run(debug=True)


