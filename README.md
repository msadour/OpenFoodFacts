# OpenFoodFacts
## Installation
* Récupérer le projet : En ligne de commande, dans le répertoire souhaité, lancer la commande : "git clone https://github.com/msadour/OpenFoodFacts.git"
* Installer les dépendance : Une fois le projet récupéré, en ligne de commande, placer vous dans le dossier du projet et lancer la commande suivante : "pip install -r requirements.txt".
* Initialisation de la base de données :
	* Posséder (ou installer) une base de données MySQL.
	* Lancer MySQL (en ligne de commande) via la commande "mysql".
	* Exécuter la commande : "SOURCE chemin_du_fichier_create_database".
* Configuration de la base de données : dans le fichier config.py, à la racine du projet. Vous pouvez modifier les variables qui sont relatives à la base de données :
	* HOST : nom de domaine de l'emplacement de la base de données (par défaut '127.0.0.1').
	* USER : le login utilisateur.
	* PASSWD : le mot de passe utilisateur.
	* DB : Le nom de la base de donnée.
	* ENCODAGE : l'encodage de la base de donnée (Pour un meilleur fonctionnement du programme, veuillez la laisser à 'UTF-8').

## Utilisation du programme
Le programme se lance via le fichier main.py (se trouvant à la racine du projet). Une fois lancé, Voici ce que propose le programme :
* L'authentification :
	* Se connecter.
	* S'inscrire (si pas de compte créé).
* Une fois authentifié, on atterrit au menu principal du programme. Le menu propose :
	* De choisir un aliment à remplacer (en sélectionnant son numéro associé) :
		* D'abord on choisi le numéro d'un type de catégorie (Remplissage de la base de données si inexistant).
		* Ensuite on sélectionne le numéro d'une categorie.
		* puis on sélectionne le numéro de l'aliment souhaité.
		* Enfin on sélectionne (ou non) un aliment proposé par la liste d'aliment plus sain.
		
	* De retrouver des aliments substitués :
		* Visualisation des aliments substitués.
		* Possibilité de suppression des aliments substitués (en sélectionnant son numéro associé).
		
	* De se déconnecter.
