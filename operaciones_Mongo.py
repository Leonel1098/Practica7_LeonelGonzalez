from statistics import median
import pandas as pd
from pymongo import MongoClient

def save_to_mongo(db, collection_name, data):
    collection = db[collection_name]
    if not data.empty:
        # Insertar los registros como documentos en MongoDB
        collection.insert_many(data.to_dict('records'))
        print("Datos guardados en MongoDB")  # Confirmación de que los datos se guardaron
    else:
        print("El DataFrame está vacío, no se guardaron datos en MongoDB")


def load_mongo_data(db, collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {'_id': 0}))
    return pd.DataFrame(data)

def update_mongo_data(db, collection_name, nombre, salario_por_hora, horas_trabajadas):
    # Encuentra y actualiza el empleado por nombre
    resultado = db[collection_name].update_one(
        {"nombre": nombre},  # Condición de búsqueda
        {
            "$set": {
                "salario_por_hora": salario_por_hora,
                "horas_trabajadas": horas_trabajadas
            }
        }
    )
    # Verifica si la actualización se realizó o si el documento no fue encontrado
    if resultado.matched_count == 0:
        raise ValueError("No se encontró ningún empleado con ese nombre o no se realizaron cambios.")
    print("Actualizando empleado:", nombre, salario_por_hora, horas_trabajadas)



def delete_from_mongo(db, collection_name, nombre):
    collection = db[collection_name]
    collection.delete_one({'Nombre': nombre})
