# Llibreries necessaries
# pip install python-telegram-bot

# importa l'API de Telegram
from telegram.ext import Application, CommandHandler,ContextTypes
from telegram import Update
from pymongo import MongoClient
from urllib import request
from pymongo import MongoClient
from bson.json_util import dumps

client_atlas = MongoClient('mongodb+srv://Benito:Ornitorrinco1234@cluster0.djylb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client_atlas.supermercats


categorias_collection = db['categories']
productos_collection = db['productes']

      
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

        # Enviem la resposta al xat amb un format més visual
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

        producte_id = str(context.args[0])

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
            grup_compra[user_id] = {}

        # Comprovem que s'han passat tots dos arguments (ID del producte i quantitat)
        if len(context.args) < 2:
            await update.message.reply_text(
                f"⚠️ Proporciona un ID de producte i una quantitat. Suma actual: {grup_compra[user_id]}"
            )
            return

        # Recuperem l'ID de producte i la quantitat de l'argument
        producte_id = str(context.args[0]) 
        quantitat = int(context.args[1])  

        producte = productos_collection.find_one({'id': producte_id})

        if not producte:
            await update.message.reply_text(f"No s'ha trobat cap producte amb l'ID {producte_id}.")
            return

        if producte_id in grup_compra[user_id]:
            grup_compra[user_id][producte_id] += quantitat
        else:
            grup_compra[user_id][producte_id] = quantitat 
        
        # Calcula el total acumulat de la compra
        total = sum(
            float(producte.get('preu', 0)) * quantitat
            for producte_id, quantitat in grup_compra[user_id].items()
            if (producte := productos_collection.find_one({'id': producte_id}))
        )
        resposta = "Carro" 
        resposta += f"💰 *Total acumulat:* {total:.2f}€"
        
                # Enviem la suma acumulada a l'usuari
        await update.message.reply_text(
            f"✅ Compra actualitzada:\n {resposta}"
        )
        
    except ValueError:
        await update.message.reply_text("⚠️ Proporciona una quantitat vàlida com a segon argument.")
    except Exception as e:
        # Captura d'altres errors inesperats
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error en la compra.")

async def factura(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Obtenim l'ID de l'usuari
        user_id = update.effective_user.id
        
        # Comprovem si l'usuari té compres registrades
        if user_id not in grup_compra or not grup_compra[user_id]:
            await update.message.reply_text("⚠️ Encara no tens cap compra registrada.")
            return

        # Generem la factura detallada
        factura_text = "🧾 Factura:\n\n"
        total = 0

        for producte_id, quantitat in grup_compra[user_id].items():
            producte = productos_collection.find_one({'id': producte_id})
            if not producte:
                continue  # Si el producte no es troba, l'ignorem

            preu = float(producte.get('preu', 0))
            subtotal = preu * quantitat
            total += subtotal

            # Afegim línia del producte a la factura
            factura_text += f"- {producte.get('nom', 'Producte')} (ID: {producte_id}): {quantitat} x {preu:.2f}€ = {subtotal:.2f}€\n"

        factura_text += f"\n💰 Total: {total:.2f}€"

        # Enviem la factura al xat
        await update.message.reply_text(factura_text)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("💥 Ha ocorregut un error generant la factura.")
    

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