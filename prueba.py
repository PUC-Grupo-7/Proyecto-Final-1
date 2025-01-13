import openai
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Verificar la clave API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("No se encontró la clave API en las variables de entorno.")
else:
    print(f"Clave API cargada: {api_key[:5]}***")  # Imprimir parte de la clave para verificar
