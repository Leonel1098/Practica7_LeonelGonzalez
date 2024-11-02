def calculate_nomina(data):
    # Cálculo del salario bruto
    data['Salario Bruto'] = data['Salario por Hora'] * data['Horas Trabajadas']
    
    # Cálculo de las deducciones
    data['Deduccion IGSS'] = data['Salario Bruto'] * 0.0483  # 4.83%
    data['Deduccion ISR'] = data['Salario Bruto'].apply(calculate_isr)  # Usando función específica para ISR
    
    # Calcular salario neto
    data['Salario Neto'] = data['Salario Bruto'] - (data['Deduccion IGSS'] + data['Deduccion ISR'])
    
    return data

def calculate_isr(salario_bruto):
    # Implementación de lógica ISR basada en las tablas comunes en Guatemala (actualízalas según sea necesario)
    if salario_bruto <= 25000:
        return salario_bruto * 0.05  # ISR de 5% para ingresos menores o iguales a 25,000
    elif salario_bruto <= 50000:
        return (salario_bruto - 25000) * 0.07 + 1250  # 7% sobre ingresos mayores a 25,000 hasta 50,000
    else:
        return (salario_bruto - 50000) * 0.10 + 3000  # 10% para ingresos mayores a 50,000

