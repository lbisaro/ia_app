import google.generativeai as genai
from flask import Flask, request, jsonify
from local__config import GENAI_APK

ia_app = Flask(__name__)

genai.configure(api_key=GENAI_APK)

# Configuración opcional del modelo (ajusta según necesites)
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

try:
    model = genai.GenerativeModel(
        # 'gemini-1.0-pro', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest' 
        model_name="gemini-1.5-flash-latest", 
        generation_config=generation_config,
        safety_settings=safety_settings
    )
except Exception as e:
    print(f"Error inicializando el modelo Gemini: {e}")
    # Podrías querer manejar esto de forma más robusta,
    # por ejemplo, no iniciando el servidor Flask si el modelo no carga.
    model = None


@ia_app.route('/prompt/', methods=['POST'])
def prompt():
    if not model:
        return jsonify({"error": "Modelo Gemini no inicializado correctamente."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body debe ser JSON"}), 400
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "El campo 'prompt' es requerido"}), 400
        response = model.generate_content(prompt)

        if response.parts:
            ia_response = response.parts[0].text
        elif hasattr(response, 'text'):
            ia_response = response.text
        else:
            print("Respuesta inesperada de Gemini:", response)
            if response.candidates and response.candidates[0].content.parts:
                 ia_response = response.candidates[0].content.parts[0].text
            else:
                return jsonify({"error": "Formato de respuesta de Gemini no reconocido o vacío."}), 500

        return jsonify({
            "prompt": prompt,
            "ia_response": ia_response
        })

    except Exception as e:
        ia_app.logger.error(f"Error durante el análisis: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    ia_app.run(debug=True, host='127.0.0.1', port=5000)