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

    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Soc un bot amb comandes /start, /productes, /imatge, /carro_compra, /factura")

        
async def productes(update, context):
    try:
        # Comprovem si s'ha passat un argument
        if len(context.args) == 0:
            await update.message.reply_text("⚠️ Proporcioni un ID de producte com a argument.")
            return

        # Recuperem l'ID de producte de l'argument
        producte_id = str(context.args[0])

        # Cerquem el producte a la base de dades
        producte = productos_collection.find_one({'id': producte_id})

        # Comprovem si s'ha trobat el producte
        if not producte:
            await update.message.reply_text(f"No s'ha trobat cap producte amb l'ID {producte_id}.")
            return

        # Preparem la resposta amb la informació del producte
        resposta = (
            f"🛒 *Id*: {producte.get('id', 'Sense ID')}\n"
            f"🛒 *Nom*: {producte.get('display_name', 'Sense nom')}\n"
            f"💶 *Preu*: {producte.get('preu', 'No disponible')}€\n"
            f"🆕 *Nou*: {'Sí' if producte.get('nou_producte', False) else 'No'}\n"
        )

        # Enviem la resposta al xat
        await update.message.reply_text(resposta, parse_mode='Markdown')

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error en recuperar el producte.")

async def imatge(update, context):
    try:
        # Comprovem si s'ha passat un argument
        if len(context.args) == 0:
            await update.message.reply_text("⚠️ Proporcioni un ID de producte com a argument.")
            return

        # Recuperem l'ID de producte de l'argument
        producte_id = str(context.args[0])

        # Cerquem el producte a la base de dades
        producte = productos_collection.find_one({'id': producte_id})

        # Comprovem si s'ha trobat el producte
        if not producte:
            await update.message.reply_text(f"No s'ha trobat cap producte amb l'ID {producte_id}.")
            return

        # Preparem la resposta amb la imatge del producte
        resposta = (
            f"🖼️ *Imatge*: [Enllaç a la imatge]({producte.get('thumbnail', 'No disponible')})"
        )

        # Enviem la resposta al xat
        await update.message.reply_text(resposta, parse_mode='Markdown')

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error en recuperar el producte.")

# Diccionari global per guardar l'estat de cada usuari
grup_compra = {}

async def carro_compra(update, context):
    try:
        # Obtenim l'ID de l'usuari
        user_id = update.effective_user.id

        # Inicialitzem la suma de l'usuari si no existeix
        if user_id not in grup_compra:
            grup_compra[user_id] = 0  # Inicialitzem a 0

        # Comprovem que s'han passat tots dos arguments (ID del producte i quantitat)
        if len(context.args) < 2:
            await update.message.reply_text(
                f"⚠️ Proporciona un ID de producte i una quantitat. Suma actual: {grup_compra[user_id]}"
            )
            return

        # Recuperem l'ID de producte i la quantitat de l'argument
        producte_id = str(context.args[0])  # El primer argument és l'ID del producte
        quantitat = int(context.args[1])  # El segon argument és la quantitat a afegir

        # Cerquem el producte a la base de dades
        producte = productos_collection.find_one({'id': producte_id})

        # Comprovem si s'ha trobat el producte
        if not producte:
            await update.message.reply_text(f"No s'ha trobat cap producte amb l'ID {producte_id}.")
            return

        # Recuperem el preu del producte
        preu = float(producte.get('preu', 0))

        # Calculem el cost total per la quantitat
        cost = preu * quantitat

        # Actualitzem la suma acumulada per l'usuari
        grup_compra[user_id] += cost

        # Enviem la suma acumulada a l'usuari
        await update.message.reply_text(
            f"✅ Compra actualitzada: {grup_compra[user_id]:.2f}€"
        )

    except ValueError:
        # Això captura errors en la conversió a números (ex. si la quantitat no és un enter)
        await update.message.reply_text("⚠️ Proporciona una quantitat vàlida com a segon argument.")
    except Exception as e:
        # Captura d'altres errors inesperats
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error processant la compra.")

async def factura(update, context):
    try:
        # Enviem la suma acumulada a l'usuari
        await update.message.reply_text(
            f"✅ Compra actualitzada: {grup_compra}€"
        )

    except ValueError:
        # Això captura errors en la conversió a números (ex. si la quantitat no és un enter)
        await update.message.reply_text("⚠️ Proporciona una quantitat vàlida com a segon argument.")
    except Exception as e:
        # Captura d'altres errors inesperats
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error processant la compra.")



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
    application.add_handler(CommandHandler("productes", productes))
    application.add_handler(CommandHandler("imatge", imatge))
    application.add_handler(CommandHandler("carro_compra", carro_compra))
    application.add_handler(CommandHandler("factura", factura))

    
    application.run_polling()


if __name__ == "__main__":
    main()