# Llibreries necessaries
# pip install python-telegram-bot

# importa l'API de Telegram
from telegram.ext import Application, CommandHandler,ContextTypes
from telegram import Update
import datetime
import json
from pymongo import MongoClient
import requests
from urllib import request
from pymongo import MongoClient
from bson.json_util import dumps

client_atlas = MongoClient('mongodb+srv://Benito:Ornitorrinco1234@cluster0.djylb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client_atlas.supermercats


categorias_collection = db['categories']
productos_collection = db['productes']


def get_data_from_api():
    url = "https://tienda.mercadona.es/api/categories/112"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
    except Exception as e:
        print(f"Error recuperant dades de l'api: {e}")
    return None

data = get_data_from_api().json()

def importar_dades(data):
    for result in data['categories']:
        categoria_id = result['id']
        categoria_layout = result['layout']    
        for categoria in result['products']:
            nou_producte = categoria['price_instructions']
            productos_collection.insert_one({
                'id': categoria['id'],
                'display_name': categoria['display_name'],
                'categoria_id': categoria_id,
                'nivell': categoria_layout,
                'nou_producte': nou_producte['is_new'],
                'preu': nou_producte['unit_price']
            })
    return print ("Dades importades")




      
# defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
    "👏👏 Felicitats! Tot el món mundial ja pot parlar amb el bot!!! 🎉 🎊")
    await update.message.reply_text(
        "Utilitza  /help per veure les comandes disponibles"
    )

    
# async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Soc un bot amb comandes /start, /help , /hora, /encuesta, /photo, /productes")

# async def hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     missatge = str(datetime.datetime.now())
#     await update.message.reply_text(missatge)
    
# async def respondre(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     respondre = str(datetime.datetime.now())
#     await update.message.reply_text(respondre)
    
# async def suma(update, context):
#     try:
#         x = float(context.args[0])
#         y = float(context.args[1])
#         s = x + y
#         message = await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=str(s))
#     except Exception as e:
#         print(e)
#         message = await context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text='💣')
        
async def productes(update, context):
    try:
        # Recuperem la categoria ID
        if len(context.args) == 0:
            await update.message.reply_text("⚠️ Proporcioni un ID de categoria com a argument.")
            return

        categoria_id = int(context.args[0])

        # Cerquem productes a la base de dades
        cursor = productos_collection.find({'categoria_id': categoria_id})
        resultats = [
            f"🛒 {producte.get('display_name', 'Sense nom')}\n"
            f"💶 Preu: {producte.get('preu', 'No disponible')}€\n"
            f"🆕 Nou: {'Sí' if producte.get('nou_producte', False) else 'No'}\n"
            f"🖼️ Imatge: {producte.get('thumbnail', 'No disponible')}\n"
            for producte in cursor
        ]

        # Comprovem si hi ha resultats
        if not resultats:
            await update.message.reply_text(f"No s'han trobat productes per a la categoria ID {categoria_id}.")
            return

        # Dividim els missatges en blocs per evitar excedir el límit de caràcters
        message = "\n\n".join(resultats)
        await update.message.reply_text(message)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error en recuperar els productes.")


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a predefined poll"""
    questions = ["Muy Malo", "Malo", "Bueno", "Muy Bueno"]
    message = await context.bot.send_poll(
        update.effective_chat.id,
        "Que tipo de estudiante eres?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a predefined poll"""
    
    message = await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('./bicing.png', 'rb')
                    )
    

def main():
    # declara una constant amb el access token que llegeix de token.txt
    TOKEN = open('./token.txt').read().strip()
    print(TOKEN)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("photo", photo))
    application.add_handler(CommandHandler("productes", productes))
    application.add_handler(CommandHandler("encuesta", poll))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()