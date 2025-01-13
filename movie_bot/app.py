import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Asegura que Flask-Migrate esté importado
from .db import db, db_config
from .models import User, Message
from .forms import ProfileForm
import openai
from openai.error import AuthenticationError, RateLimitError, OpenAIError  # Corrección de importación
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import logging

# Cargar configuración del entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización de Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_predeterminada")
db_config(app)
Bootstrap5(app)

# Configurar la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configurar Flask-Migrate
migrate = Migrate(app, db)

@app.route("/")
def landing():
    """Página principal de bienvenida."""
    return render_template("landing.html", title="Página de Inicio")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """
    Página de chat con MovieBot.
    Permite enviar mensajes al bot y guardar el historial.
    """
    try:
        user_id = session.get("user_id")
        if not user_id:
            user = User.query.first()
            if not user:
                user = User(email="test@example.com", favorite_genre="Acción", disliked_genre="Terror")
                db.session.add(user)
                db.session.commit()
            session["user_id"] = user.id
        else:
            user = User.query.get(user_id)

        if request.method == "POST":
            user_message = request.form.get("message")
            if not user_message or user_message.strip() == "":
                flash("El mensaje no puede estar vacío.", "danger")
                messages = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp.asc()).all()
                return render_template("chat.html", messages=messages, title="Chat")

            # Guardar el mensaje del usuario
            db.session.add(Message(content=user_message, author="user", user=user))
            db.session.commit()

            # Crear el prompt para el bot
            prompt = f"""
            Eres un bot recomendador de películas llamado MovieBot.
            Género favorito del usuario: {user.favorite_genre or 'No especificado'}.
            Género que debe evitar: {user.disliked_genre or 'No especificado'}.
            Responde de forma breve y clara.
            """

            try:
                # Llamada a OpenAI (versión 1.0.0+)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Cambiar a "gpt-4" si tienes acceso
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                bot_reply = response['choices'][0]['message']['content']
            except AuthenticationError:
                bot_reply = "Error de autenticación. Verifica tu clave API."
                logger.error("Error de autenticación con OpenAI.")
            except RateLimitError:
                bot_reply = "Has excedido el límite de solicitudes. Intenta nuevamente más tarde."
                logger.error("Límite de solicitudes excedido a OpenAI.")
            except OpenAIError as e:
                bot_reply = f"Error general de OpenAI: {e}"
                logger.error(f"Error general de OpenAI: {e}")
            except Exception as e:
                bot_reply = f"Error inesperado: {e}"
                logger.error(f"Error inesperado: {e}")

            # Guardar respuesta del bot
            db.session.add(Message(content=bot_reply, author="assistant", user=user))
            db.session.commit()

        # Consultar mensajes del historial
        messages = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp.asc()).all()
        return render_template("chat.html", messages=messages, title="Chat")

    except Exception as e:
        logger.error(f"Error en /chat: {e}")
        return "Ha ocurrido un error interno en el servidor.", 500

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    """
    Página para editar el perfil del usuario.
    Permite actualizar preferencias como género favorito y género a evitar.
    """
    try:
        user_id = session.get("user_id")
        if not user_id:
            user = User.query.first()
            if not user:
                user = User(email="test@example.com", favorite_genre="Acción", disliked_genre="Terror")
                db.session.add(user)
                db.session.commit()
            session["user_id"] = user.id
        else:
            user = User.query.get(user_id)

        form = ProfileForm(obj=user)

        if form.validate_on_submit():
            user.favorite_genre = form.favorite_genre.data
            user.disliked_genre = form.disliked_genre.data
            db.session.commit()
            flash("Perfil actualizado exitosamente.", "success")
            return redirect(url_for('perfil'))

        return render_template("perfil.html", form=form, title="Editar Perfil")
    except Exception as e:
        logger.error(f"Error en /perfil: {e}")
        return "Ha ocurrido un error interno en el servidor.", 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
