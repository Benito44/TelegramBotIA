# Explicació del bot de Telegram

## Preparació
- Llibreries necesaries 
    **pip install python-telegram-bot**

- Entorn virtual

![alt text](versio_python.png)

## Funcionament

El funcionament del bot consta de varies funcions per executar el resultat final 

1. ### /start
    - Funció simple que serveix per enviar un missatge de confirmació d'execució correcte del bot de Telegram

![alt text](start.png)

2. ### /help
    - Funció que serveix per mostrar les funcions possibles

![alt text](help.png)

3. ### /productes
    - Aquesta funció que li pasem un id obté el primer parametre de la comanda i busca aquest parametre a la taula abans conectada per MongoAtlas.

    - Una vegada trobat el producte per l'ID obté els seus camps i el mostra per pantalla. També té una excepció per si ocurreix qualsevol error.

![alt text](producte.png)

4. ### /imatge
    - Aquesta funció fa el mateix que **/productes** pero mostra la imatge del producte

![alt text](imatge.png)

5. ### /carro_compra
    - Aquesta funció passant-li l'ID y la quantitat del producte agafa el preu amb el primer parametre i aquest li multipliquem pel segon parametre on trobem la quantitat que li volem aplicar. També obté l'ID per guardar-ho per després.

    - Després de fer el càlcul mostra el total, si es torna a executar amb un ID o una quantitat diferent, aquest càcul és sumarà al total complet, mostrant el progres.

![alt text](carro_compra.png)

6. ### /factura
    - Aquesta funció de millora s'executa sense cap parametre i mostra una factura més detallada amb l'ID del producte demanat, el seu preu inicial, la quantitat y el total calculat.

    - Obté l'ID i la quantitat guardat en la funció anterior per trobar el preu original y calcular el total

![alt text](factura.png)