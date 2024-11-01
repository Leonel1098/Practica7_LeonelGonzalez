from statistics import median
import pandas as pd
from pymongo import MongoClient

def save_to_mongo(db, collection_name, data):
    collection = db[collection_name]
    collection.insert_many(data.to_dict('records'))

def load_mongo_data(db, collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {'_id': 0}))
    return pd.DataFrame(data)

def update_mongo_data(db, collection_name, nombre, salario_por_hora, horas_trabajadas):
    collection = db[collection_name]
    collection.update_one(
        {'Nombre': nombre},
        {'$set': {'Salario por Hora': salario_por_hora, 'Horas Trabajadas': horas_trabajadas}}
    )

def delete_from_mongo(db, collection_name, nombre):
    collection = db[collection_name]
    collection.delete_one({'Nombre': nombre})

def get_aggregation_results(db, collection_name):
    collection = db[collection_name]
    
     # Total y Promedio de Horas Trabajadas
    horas_aggregation = collection.aggregate([
        {"$group": {
            "_id": None,
            "total_horas_trabajadas": {"$sum": "$horas_trabajadas"},
            "promedio_horas_trabajadas": {"$avg": "$horas_trabajadas"}
        }}
    ])

    # Total y Promedio de Salario por Hora
    salario_hora_aggregation = collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_por_hora": {"$sum": "$salario_por_hora"},
            "promedio_salario_por_hora": {"$avg": "$salario_por_hora"}
        }}
    ])

    # Salario Bruto Total y Promedio
    salario_bruto_aggregation = collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_bruto": {"$sum": "$salario_bruto"},
            "promedio_salario_bruto": {"$avg": "$salario_bruto"}
        }}
    ])

    # Salario Neto Total y Promedio
    salario_neto_aggregation = collection.aggregate([
        {"$group": {
            "_id": None,
            "total_salario_neto": {"$sum": "$salario_neto"},
            "promedio_salario_neto": {"$avg": "$salario_neto"}
        }}
    ])

    # Salario Neto Más Alto y Más Bajo
    salario_neto_min_max = collection.aggregate([
        {"$group": {
            "_id": None,
            "salario_neto_mas_alto": {"$max": "$salario_neto"},
            "salario_neto_mas_bajo": {"$min": "$salario_neto"}
        }}
    ])

    # Mediana de Salario Neto
    salarios_neto = list(collection.find({}, {"salario_neto": 1, "_id": 0}))
    salario_neto_mediana = median([s["salario_neto"] for s in salarios_neto])

    # Distribución de Deducciones
    deducciones_aggregation = collection.aggregate([
        {"$unwind": "$deducciones"},
        {"$group": {
            "_id": "$deducciones.tipo",
            "total_deducciones": {"$sum": "$deducciones.monto"},
            "promedio_deduccion": {"$avg": "$deducciones.monto"}
        }}
    ])

    # Convertir resultados a diccionario
    resultados = {
        "horas": next(horas_aggregation, {}),
        "salario_hora": next(salario_hora_aggregation, {}),
        "salario_bruto": next(salario_bruto_aggregation, {}),
        "salario_neto": next(salario_neto_aggregation, {}),
        "salario_neto_min_max": next(salario_neto_min_max, {}),
        "salario_neto_mediana": salario_neto_mediana,
        "deducciones": list(deducciones_aggregation)
    }

    return resultados
    
    # Consultas similares se pueden hacer para otros resultados
    # Retornar resultados para mostrarlos o usarlos en una interfaz
    return list(total_hours)
