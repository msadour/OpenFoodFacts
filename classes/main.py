import pymysql
import requests
import pprint


class Main:
    """
    Class Main
    """

    @staticmethod
    def run():
        connexion = Main.get_connection_db()
        Main.put_food_in_db(connexion)
        id_user = Main.identification(connexion)
        deconnexion = False
        while not deconnexion:
            choice = Main.get_choice_user()
            finish = False
            while not finish:
                if choice == "1" :
                    Main.choose_food_from_category(connexion, id_user)
                    finish = True
                elif choice == "2":
                    Main.get_user_foods(connexion, id_user)
                    finish = True
                elif choice == "3":
                    finish = True
                    deconnexion = True

    @staticmethod
    def get_connection_db():
        connexion = pymysql.connect(host='127.0.0.1', user='root', passwd='azerty', db='OpenFoodFacts')
        return connexion

    @staticmethod
    def identification(connexion):
        while True :
            print('1 - connexion \n2 - Inscription')
            choice = input("")
            if choice == '1':
                return Main.connexion_user(connexion)
            elif choice == '2':
                return Main.inscription_user(connexion)
            else:
                print('Veuillez saisir un choix valide ! \n')

    @staticmethod
    def inscription_user(connexion):
        while True:
            login = input("Saisir votre login : ")
            password = input("Saisir votre mot de passe : ")
            cursor = connexion.cursor()
            cursor.execute("SELECT * FROM User WHERE login = '" +login+ "';")
            if len(cursor.fetchall()) == 0:
                cursor.execute("INSERT INTO User (login, password) VALUES ('" +login+"', '" +password+ "');")
                connexion.commit()
                cursor.execute("SELECT id FROM User WHERE login = '" +login+ "';")
                return cursor.fetchone()[0]
                break
            else:
                print('Ce login existe deja ! \n\n')

    @staticmethod
    def connexion_user(connexion):
        while True:
            login = input("\nSaisir votre login : ")
            password = input("Saisir votre mot de passe : ")
            cursor = connexion.cursor()
            cursor.execute("SELECT * FROM User WHERE login = '" + login + "' AND password = '"+ password +"';")
            if len(cursor.fetchall()) == 1:
                connexion.commit()
                cursor.execute("SELECT id FROM User WHERE login = '" + login + "';")
                return cursor.fetchone()[0]
            else:
                print("Login et/ou mot de passe erroné")

    @staticmethod
    def get_food_with_better_score(score):
        list_better_score = []
        better_score_str = ''
        table_nutri_score = {
            'a' : 5,
            'b' : 4,
            'c' : 3,
            'd' : 2,
            'e' : 1
        }
        score_my_food = table_nutri_score[score]
        for letter, score in table_nutri_score.items():
            if score > score_my_food:
                list_better_score.append(letter)
        for letter in list_better_score:
            better_score_str = better_score_str + "'" + letter + "',"
        better_score_str = better_score_str[:-1] #Pour supprimer la derniere virgule
        return better_score_str

    @staticmethod
    def sort_dict(dict_no_sorted, by_what, sens="asc"):
        """
        Cette fonction permet de trié le disctionnaire en parametre (dict_no_sorted).
        Elle trie les clés ou les valeur via l'argument "by_what". On peut egalement
        trié par ordre croissant (asc) ou decroissant (desc) via l'argument "sens".
        """

        dict_sorted = {}
        if by_what == "key":
            lst_keys = sorted([int(key) for key, value in dict_no_sorted.items()])
            if sens == "desc":
                lst_keys = reversed(lst_keys)
            for k in lst_keys:
                value_sorted = dict_no_sorted[str(k)]
                dict_sorted[k] = value_sorted
        elif by_what == "value":
            lst_key_value = [[value, key] for key, value in dict_no_sorted.items()]
            lst_value = sorted([value for key, value in dict_no_sorted.items()])
            if sens == "desc":
                lst_value = reversed(lst_value)
            for v in lst_value:
                for kv in lst_key_value:
                    if v in kv:
                        dict_sorted[kv[1]] = v
                        lst_key_value.remove(kv)
        else:
            return {"Erreur": "Veuillez saisir en parametre soit clé soit valeur !"}
        return dict_sorted

    @staticmethod
    def get_choice_user():
        while True:
            print("1 - Remplacer un aliment ? \n2 - Retrouver mes aliments substitués.\n3 - Deconnexion")
            choice_user = input("")
            if choice_user == "1" or choice_user == "2" or choice_user == "3":
                return choice_user
                break

    @staticmethod
    def convert_choice_user(choice):
        try:
            choice = int(choice)
        except:
            if choice == 'N' or choice == 'n':
                return choice
        else:
            return choice

    @staticmethod
    def choose_food_from_category(connexion, id_user):
        list_categories = {}
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM Category")
        num_category = 1
        for category in cursor.fetchall():
            list_categories[str(num_category)] = category[1]
            num_category += 1

        list_categories = Main.sort_dict(list_categories, "key")
        for num, name in list_categories.items():
            print(str(num) + " - " + name + "\n")

        while True:
            choosen_category = input("Selectionner le numero de la categorie (ou appuyez sur N pour annuler) : ")
            choosen_category = Main.convert_choice_user(choosen_category)
            if choosen_category in list_categories.keys():
                category = list_categories[choosen_category]
                list_food_category = {}
                query_foods_from_category = "SELECT Food.name " \
                              "FROM Category, Food, Food_Category " \
                              "WHERE category.id = Food_Category.id_category " \
                              "AND food.id = Food_Category.id_food " \
                              "AND Category.name = '" + category + "';"
                cursor.execute(query_foods_from_category)
                num_category = 1
                for food in cursor.fetchall():
                    list_food_category[str(num_category)] = food[0]
                    num_category += 1

                list_food_category = Main.sort_dict(list_food_category, 'key')
                for num, name in list_food_category.items():
                    print(str(num) + " - " + name)

                while True:
                    choosen_foods = input("\nSelectionner le numero de votre aliment (ou appuyez sur N pour annuler) : ")
                    choosen_foods = Main.convert_choice_user(choosen_foods)
                    if choosen_foods in list_food_category.keys():
                        food = list_food_category[choosen_foods]
                        cursor.execute("SELECT nutri_score FROM Food WHERE name = '"+food+"';")
                        list_good_score = Main.get_food_with_better_score(cursor.fetchone()[0])

                        query_foods_better_score = "SELECT Food.name " \
                                      "FROM Category, Food, Food_Category " \
                                      "WHERE category.id = Food_Category.id_category " \
                                      "AND food.id = Food_Category.id_food " \
                                      "AND Category.name = '" + category + "' " \
                                      "AND nutri_score IN ( " + list_good_score + ") " \
                                      "AND Food.name != '" + food + "';"

                        cursor.execute(query_foods_better_score)
                        if len(cursor.fetchall()) == 0 :
                            print('Aucun aliment n\'est plus sain dans cette categorie ..')
                        else:
                            cursor.execute(query_foods_better_score)
                            index_food = 1
                            foods_substitute = {}
                            for food_better_score in cursor.fetchall():
                                foods_substitute[str(index_food)] = food_better_score[0]
                                index_food += 1

                            print("Voici la liste des aliments substituable : ")
                            foods_substitute = Main.sort_dict(foods_substitute, 'key')
                            for num, food in foods_substitute.items():
                                print(str(num) + ' - ' + food + "\n")

                            while True:
                                choosen_foods_substitute = input("Choisissez un numero "
                                                                 "d'aliment (ou appuyez sur N pour annuler) : ")
                                choosen_foods_substitute = Main.convert_choice_user(choosen_foods_substitute)
                                if choosen_foods_substitute in foods_substitute.keys():
                                    food_select = foods_substitute[choosen_foods_substitute]
                                    print('Vous avez choisie : ' + food_select)
                                    cursor.execute("SELECT id FROM Food WHERE name = '"+food_select+"';")
                                    id_food = cursor.fetchone()[0]
                                    query_insert_food_user = "INSERT INTO Food_User (id_user, id_food) " \
                                                             "VALUES (" +str(id_user)+ ", "+str(id_food)+");"
                                    cursor.execute(query_insert_food_user)
                                    connexion.commit()
                                    break
                                elif choosen_foods_substitute == "N" or choosen_foods_substitute == "n":
                                    break
                                else:
                                    print("Veuillez choisir le bon numero de l'aliment souhaité .. \n")
                    elif choosen_foods == "N" or choosen_foods == "n":
                        break
                    else :
                        print("Veuillez choisir le bon numero de l'aliment souhaité .. \n")
            elif choosen_category == "N" or choosen_category == "n":
                break
            else:
                print("Veuillez choisir le bon numero de la categorie souhaitée .. \n")

    @staticmethod
    def get_user_foods(connexion, id_user):
        cursor = connexion.cursor()
        query_select_food_user = "SELECT * " \
                                 "FROM Food, Food_User " \
                                 "WHERE Food.id = Food_User.id_food " \
                                 "AND Food_User.id_user = " + str(id_user) + ";"
        cursor.execute(query_select_food_user)
        print("liste des aliments que j'ai substitué :")
        list_user_foods = {}
        num_food = 1
        for food in cursor.fetchall():
            list_user_foods[str(num_food)] = (food[1], food[2], food[3], food[4])
            num_food += 1

        users_foods = Main.sort_dict(list_user_foods, 'key')

        for num_food, food in users_foods.items():
            current_food = users_foods[num_food]
            display_food = "  " + str(num_food) + " - " + current_food[0] + " - " + current_food[1] + \
                              " - " + current_food[2]

            if current_food[3] == '':
                display_food = '{}{}'.format(display_food, " - (Lieu non precisé)")
            else:
                display_food = display_food + " - " + current_food[3]

            print(display_food)

        choosed = False
        while not choosed:
            do_want_remove = input("\nVoulez vous supprimer un aliment (O/N) ? ")
            if do_want_remove == "O" or do_want_remove == 'o':
                food_is_selected = False
                while not food_is_selected:
                    food_remove = input("Selectionner le numero de l'aliment à supprimer (ou N pour annuler): ")
                    if food_remove in list_user_foods.keys():
                        food_selected_for_remove = list_user_foods[food_remove]
                        query_select_food = "SELECT id FROM Food WHERE name = '"+food_selected_for_remove[0]+"';"
                        cursor.execute(query_select_food)
                        id_food_removed = cursor.fetchone()[0]
                        query_remove_food = "DELETE FROM Food_User " \
                                            "WHERE id_food='"+str(id_food_removed)+"' " \
                                            "AND id_user='"+str(id_user)+"';"
                        cursor.execute(query_remove_food)
                        connexion.commit()
                        food_is_selected = True
                        choosed = True
                    elif food_remove == 'N' or food_remove == 'n':
                        break
                    else:
                        print("Saisie incorrecte ! ")
            elif do_want_remove == 'N' or do_want_remove == 'n':
                choosed = True
        print("\n\n")

    @staticmethod
    def put_food_in_db(connexion):
        food_category = {}
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM Food ;")
        if len(cursor.fetchall()) == 0:
            foods = requests.get('https://fr-en.openfoodfacts.org/category/pizzas/1.json').json()
            cursor = connexion.cursor()
            list_categories_in_db = []
            for food in foods['products']:
                #Produit
                if 'nutrition_grades' in food.keys():
                    if '\'' in food['product_name_fr']:
                        food['product_name_fr'] = food['product_name_fr'].replace('\'', '')
                    request_insert = "INSERT INTO Food (name, nutri_score, web_link, place) " \
                                 "VALUES ('" + food['product_name_fr'] + "', '" + food['nutrition_grades'] + "', '" + food['url']\
                                     + "', '" + food['purchase_places']+ "');"
                    cursor.execute(request_insert)
                    food_category[food["product_name_fr"]] = []

                    #Categorie
                    list_categories = food['categories'].split(',')
                    list_categories = [category.lower() for category in list_categories]
                    for category in list_categories :
                        if 'en:' in category or 'fr:' in category:
                            category = category[3:]
                            if ':' in category:
                                category = category[1:]
                        if category not in list_categories_in_db:
                            list_categories_in_db.append(category)
                            cursor.execute("INSERT INTO Category (name) VALUES ('" + category + "');")

                        food_category[food["product_name_fr"]].append(category)

            connexion.commit()

            #Food Category
            for food, list_category in food_category.items():
                cursor.execute("SELECT id FROM Food WHERE name = '" + food + "';")
                for id_food in cursor.fetchone():
                    for category in list_category:
                        cursor.execute("SELECT id FROM Category WHERE name = '" + category + "';")
                        for id_category in cursor.fetchall():
                            request_put_food_category = "INSERT INTO Food_Category(id_food, id_category) " \
                                                    "VALUES (" + str(id_food)+ ", " +str(id_category[0])+ ");"
                            cursor.execute(request_put_food_category)
            connexion.commit()
