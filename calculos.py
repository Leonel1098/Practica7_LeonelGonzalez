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
    # Aquí se implementa la lógica de ISR según las tablas vigentes de Guatemala
    if  salario_bruto <= 25000:
        return salario_bruto * 0.05
    elif salario_bruto <= 9000:
        return (salario_bruto * 0.07)+15000