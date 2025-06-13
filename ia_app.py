import google.generativeai as genai
from flask import Flask, request, jsonify
from local__config import GENAI_APK
import json

ia_app = Flask(__name__)

genai.configure(api_key=GENAI_APK)

#generation_config optimizado para obtener datos crudos en formato json
generation_config = {
    # Temperatura muy baja para respuestas consistentes y basadas en datos.
    # No queremos que "invente" o sea creativo.
    "temperature": 0.1, 

    # IMPORTANTE: Forzamos al modelo a devolver una respuesta en formato JSON.
    # Esto elimina la necesidad de parsear texto y reduce errores.
    "response_mime_type": "application/json",

    # Un límite más ajustado. Para un JSON simple, no necesitas 2048 tokens.
    # Esto ahorra recursos y puede acelerar ligeramente la respuesta.
    "max_output_tokens": 512, 
}
#safety_settings solo se utiliza como buena práctica
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

with open('prompt_library.json', 'r', encoding='utf-8') as f:
    PROMPT_LIBRARY = json.load(f)


try:
    models = {}
    for k in PROMPT_LIBRARY:
        system_instruction = PROMPT_LIBRARY[k]['system_instruction']
        models[k] = genai.GenerativeModel(
            # 'gemini-1.0-pro', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest' 
            model_name="gemini-1.5-flash-latest", 
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction
        )

except Exception as e:
    print(f"Error inicializando el modelo Gemini: {e}")
    # Podrías querer manejar esto de forma más robusta,
    # por ejemplo, no iniciando el servidor Flask si el modelo no carga.
    model = None


@ia_app.route('/prompt/', methods=['POST'])
def prompt():
    
    #try:
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body debe ser JSON"}), 400
    elif 'prompt' not in data:
        return jsonify({"error": "JSON Request must contain prompt value"}), 400
    elif 'instruction' not in data:
        return jsonify({"error": "JSON Request must contain instruction value"}), 400
    prompt = data.get('prompt')
    instruction = data.get('instruction')
    
    if not prompt:
        return jsonify({"error": "El campo 'prompt' es requerido"}), 400
    if not instruction:
        return jsonify({"error": "El campo 'instruction' es requerido"}), 400
    if instruction not in models:
        return jsonify({"error": f"La instruction {instruction} no es valida"}), 400

    model = models[instruction]
    if not model:
        return jsonify({"error": "Modelo Gemini no inicializado correctamente."}), 500
    response = model.generate_content(prompt)
    
    if response.parts:
        ia_response = response.parts[0].text
    elif hasattr(response, 'text'):
        ia_response = response.text
    else:
        if response.candidates and response.candidates[0].content.parts:
                ia_response = response.candidates[0].content.parts[0].text
        else:
            return jsonify({"error": "Formato de respuesta de Gemini no reconocido o vacío."}), 500
    
    ia_response_json = eval(ia_response)
    response_json = jsonify({
        "ia_response": ia_response_json,
        "instruction": instruction,
        "prompt": prompt,
        "returns": PROMPT_LIBRARY[instruction]['returns'],
        "ok": 1,
    })
        
    return response_json 

    #except Exception as e:
    #    ia_app.logger.error(f"Error durante el análisis: {e}")
    #    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    ia_app.run(debug=True, host='127.0.0.1', port=5000)