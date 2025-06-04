import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from local__config import GENAI_APK as GEMINI_API_KEY

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

genai.configure(api_key=GEMINI_API_KEY)

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

# Inicializar el modelo
# Asegúrate de que 'gemini-pro' es el modelo que quieres usar y está disponible.
# Otros modelos podrían ser 'gemini-1.0-pro', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest' etc.
# Verifica la documentación de Google para los nombres de modelos actuales.
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest", # o el modelo que prefieras
        generation_config=generation_config,
        safety_settings=safety_settings
    )
except Exception as e:
    print(f"Error inicializando el modelo Gemini: {e}")
    # Podrías querer manejar esto de forma más robusta,
    # por ejemplo, no iniciando el servidor Flask si el modelo no carga.
    model = None


@app.route('/ia_prompt', methods=['POST'])
def analizar_texto():
    if not model:
        return jsonify({"error": "Modelo Gemini no inicializado correctamente."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body debe ser JSON"}), 400

        prompt = data.get('prompt')
        #json_prms = data.get('json_prms', '{}') # Ejemplo de parámetro adicional

        if not prompt:
            return jsonify({"error": "El campo 'prompt' es requerido"}), 400

        # Aquí puedes usar el parametro_adicional para modificar el prompt o el comportamiento
        #prompt_completo = f"Analiza el siguiente texto: '{prompt}'. Parámetro adicional: {json_prms}"
        # O puedes construir un prompt más estructurado si es necesario

        # Generar contenido con Gemini
        # Para un chat simple, puedes usar model.generate_content
        # Si necesitas un historial de conversación, usa chat_session = model.start_chat(history=[])
        # y luego chat_session.send_message(...)

        response = model.generate_content(prompt)

        # Extraer el texto de la respuesta
        # La estructura de response.text puede variar ligeramente.
        # A veces es directamente response.text, otras response.parts[0].text
        # Imprime response para ver su estructura si tienes dudas: print(response)
        if response.parts:
            ia_response = response.parts[0].text
        elif hasattr(response, 'text'):
            ia_response = response.text
        else:
            # Si la respuesta no tiene 'parts' ni 'text', podría ser un error o un formato inesperado
            # Intenta imprimir la respuesta completa para depurar
            print("Respuesta inesperada de Gemini:", response)
            # Intenta acceder a candidates si existe, común en versiones anteriores o configuraciones específicas
            if response.candidates and response.candidates[0].content.parts:
                 ia_response = response.candidates[0].content.parts[0].text
            else:
                return jsonify({"error": "Formato de respuesta de Gemini no reconocido o vacío."}), 500


        return jsonify({
            "prompt": prompt,
            "ia_response": ia_response
        })

    except Exception as e:
        # Loguea el error para depuración
        app.logger.error(f"Error durante el análisis: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Solo para desarrollo local, no usar en producción
    app.run(debug=True, host='127.0.0.1', port=5000)