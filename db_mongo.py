import pandas as pd
from pymongo import MongoClient

def load_csv_data(file_path):
    # Cargar datos del archivo CSV usando Pandas
    data = pd.read_csv(file_path)
    return data

def load_mongo_data(db, collection_name):
    # Conectar con la colección de MongoDB
    collection = db[collection_name]
    # Obtener los datos de la colección
    data = list(collection.find({}, {'_id': 0}))  # Excluir el campo '_id'
    return pd.DataFrame(data)  # Convertir a DataFrame para consistencia
