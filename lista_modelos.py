import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyAn_nJ7G_I5cYNyOmk4KSmRWnJ_6RQ6ojc"))

try:
    print("Buscando modelos disponibles...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Modelo encontrado: {m.name}")
except Exception as e:
    print(f"❌ Error al listar modelos: {e}")