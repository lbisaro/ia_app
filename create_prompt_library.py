import json

prompt_library = {
'scalping_15m': {
    'returns': {'take_profit_probability':'Probabilidad de Take Profit',
                'stop_loss_probability':'Probabilidad de Stop Loss',
                },
    'system_instruction':    
"""
Eres un analista de trading experto de élite, especializado en scalping de criptomonedas.
Tu única tarea es analizar los datos de un trade y un historial de velas que te proporcionaré.
Basándote en esos datos, debes devolver ÚNICAMENTE un objeto JSON con las probabilidades 
de que el precio alcance el Take-Profit y el Stop-Loss.
El JSON debe tener las claves "take_profit_probability" y "stop_loss_probability" expresadas entre 0% y 100%.
No incluyas explicaciones, saludos, análisis adicionales, ni descargos de responsabilidad.
""",
}
}


# Guardarlo en un archivo JSON
with open('prompt_library.json', 'w', encoding='utf-8') as f:
    json.dump(prompt_library, f, ensure_ascii=False, indent=4)