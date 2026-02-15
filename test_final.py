import google.generativeai as genai

# PEGA TU LLAVE AQUÍ DENTRO DE LAS COMILLAS
mi_llave = "AIzaSyAn_nJ7G_I5cYNyOmk4KSmRWnJ_6RQ6ojc"

genai.configure(api_key=mi_llave)

try:
    print(f"Probando conexión con la llave: {mi_llave[:5]}...***")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Responde con la palabra: FUNCIONA")
    print(f"Resultado: {response.text}")
except Exception as e:
    print(f"❌ Error real: {e}")