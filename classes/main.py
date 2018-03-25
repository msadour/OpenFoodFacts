"""
Contain the class for run application.
"""

import pymysql
import requests
import pdb


class Main:
    """
    Class Main
    """

    @staticmethod
    def run():
        """
        Run application
        :return:
        """
        connexion = Main.get_connection_db()
        cursor = connexion.cursor()
        cursor.execute("SELECT * FROM Food ;")
        if cursor.fetchone() is None:
            # We filled database
            cursor.execute("ALTER DATABASE openfoodfacts CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
            connexion.commit()
            Main.put_food_in_db(connexion)
        id_user = Main.identification(connexion)
        deconnection = False
        while not deconnection:
            choice = Main.get_choice_user()
            finish = False
            while not finish:
                if choice == "1":
                    Main.choose_food_from_category(connexion, id_user)
                elif choice == "2":
                    Main.get_user_foods(connexion, id_user)
                elif choice == "3":
                    deconnection = True
                finish = True

    @staticmethod
    def get_connection_db():
        """
        Get a connexion of database
        :return: connexion
        """
        connexion = pymysql.connect(host='127.0.0.1', user='root', passwd='azerty',
                                    db='OpenFoodFacts', charset='utf8')
        return connexion

    @staticmethod
    def identification(connexion):
        """
        Identification of a user
        :return:
        """
        while True:
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
        """
        Inscription for use application
        :return: cursor
        """
        while True:
            login = input("Saisir votre login : ")
            password = input("Saisir votre mot de passe : ")
            cursor = connexion.cursor()
            cursor.execute("SELECT * FROM User WHERE login = '" + login + "';")
            # We check if the user is not already exist.
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO User (login, password) "
                               "VALUES ('" + login +"', '" + password + "');")
                connexion.commit()
                cursor.execute("SELECT id FROM User WHERE login = '" + login + "';")
                return cursor.fetchone()[0]
            else:
                print('Ce login existe deja ! \n\n')

    @staticmethod
    def connexion_user(connexion):
        """
        Connect a user
        :return: id of user
        """
        while True:
            login = input("\nSaisir votre login : ")
            password = input("Saisir votre mot de passe : ")
            cursor = connexion.cursor()
            cursor.execute("SELECT * "
                           "FROM User "
                           "WHERE login = '" + login + "' "
                           "AND password = '" + password + "';")
            if cursor.fetchone():
                cursor.execute("SELECT id FROM User WHERE login = '" + login + "';")
                return cursor.fetchone()[0]
            else:
                print("Login et/ou mot de passe erroné")

    @staticmethod
    def get_food_with_better_score(current_score):
        """
        Return a list (string) with better score than a score of food what we want replace
        :return:
        """
        list_better_score = []
        better_score_str = ''
        table_nutri_score = {'a': 5, 'b': 4, 'c': 3, 'd': 2, 'e': 1}
        score_my_food = table_nutri_score[current_score]
        for letter, score in table_nutri_score.items():
            if score > score_my_food:
                list_better_score.append(letter)
        for letter in list_better_score:
            better_score_str = better_score_str + "'" + letter + "',"
        # for delete the last comma :
        better_score_str = better_score_str[:-1]
        return better_score_str

    @staticmethod
    def sort_dict(dict_no_sorted, sens="asc"):
        """
        This function sort keys of a dict.
        :return:
        """

        dict_sorted = {}
        lst_keys = sorted([int(key) for key, value in dict_no_sorted.items()])
        if sens == "desc":
            lst_keys = reversed(lst_keys)
        for k in lst_keys:
            value_sorted = dict_no_sorted[str(k)]
            dict_sorted[k] = value_sorted
        return dict_sorted

    @staticmethod
    def get_choice_user():
        """
        Ask to user if he want replace a food, show them replaces foods or deconnexion.
        :return:
        """
        while True:
            print("1 - Remplacer un aliment ? \n"
                  "2 - Retrouver mes aliments substitués.\n"
                  "3 - Deconnexion")
            choice_user = input("")
            if choice_user == "1" or choice_user == "2" or choice_user == "3":
                return choice_user

    @staticmethod
    def convert_choice_user(message):
        """
        Check if choice user is right.
        :return: choice
        """
        choice = input(message)
        try:
            choice = int(choice)
        except ValueError:
            # In the case if user choice other things that a number.
            if choice == 'N' or choice == 'n':
                return choice
        else:
            return choice

    @staticmethod
    def make_dict_element(cursor, request, index=None, is_row=False, list_index=None):
        """
        Make a dictionnary with sorted keys (number who a user input) and them values
        for display a number with them value like this : 1 - value ..
        :return: Dictionnary with sorted keys
        """
        cursor.execute(request)
        list_element = {}
        num_element = 1
        list_name_element = []
        for element in cursor.fetchall():
            if not is_row:
                list_name_element.append(element[index])
            else:
                tuple_element = tuple((element[i] for i in list_index))
                list_name_element.append(tuple_element)

        for element in sorted(list_name_element):
            list_element[str(num_element)] = element
            num_element += 1

        list_element = Main.sort_dict(list_element)
        return list_element

    @staticmethod
    def choose_food_from_category(connexion, id_user):
        """
        Display all categories and when a user select a categorie, all food with
        them categorie is display. When user selected a food, all substitute of them
        food (with better score) is display and he can replace this food or not.
        :return:
        """
        cursor = connexion.cursor()
        list_categories = Main.make_dict_element(cursor, "SELECT * FROM Category", 1)

        for num, name in list_categories.items():
            print(str(num) + " - " + name)

        while True:
            choosen_category = Main.convert_choice_user("Selectionner le numero de la categorie "
                                                        "(ou appuyez sur N pour annuler) : ")
            if choosen_category in list_categories.keys():
                category = list_categories[choosen_category]
                query_foods_from_category = "SELECT Food.name " \
                                            "FROM Category, Food, Food_Category " \
                                            "WHERE category.id = Food_Category.id_category " \
                                            "AND food.id = Food_Category.id_food " \
                                            "AND Category.name = '" + category + "';"
                list_food_category = Main.make_dict_element(cursor, query_foods_from_category, 0)

                for num, name in list_food_category.items():
                    print(str(num) + " - " + name)

                while True:
                    choosen_foods = Main.convert_choice_user(
                        "\nSelectionnez le numero d'un aliment (ou N pour annuler) : ")
                    if choosen_foods in list_food_category.keys():
                        food = list_food_category[choosen_foods]
                        cursor.execute("SELECT nutri_score FROM Food WHERE name = '"+food+"';")
                        list_betters_score = Main.get_food_with_better_score(cursor.fetchone()[0])
                        query_better_food = \
                            "SELECT Food.name " \
                            "FROM Category, Food, Food_Category " \
                            "WHERE category.id = Food_Category.id_category " \
                            "AND food.id = Food_Category.id_food " \
                            "AND Category.name = '" + category + "' " \
                            "AND nutri_score IN ( " + list_betters_score + ") " \
                            "AND Food.name != '" + food + "';"
                        cursor.execute(query_better_food)
                        if cursor.fetchone() is None:
                            print('Aucun aliment n\'est plus sain dans cette categorie ..')
                        else:
                            foods_substitute = Main.make_dict_element(cursor, query_better_food, 0)

                            print("Voici la liste des aliments substituable : ")
                            for num, food in foods_substitute.items():
                                print(str(num) + ' - ' + food)

                            while True:
                                choosen_foods_substitute = Main.convert_choice_user(
                                    "Choisissez un numero d'aliment (ou N pour annuler) : ")
                                if choosen_foods_substitute in foods_substitute.keys():
                                    food_select = foods_substitute[choosen_foods_substitute]
                                    print('Vous avez choisie : ' + food_select)
                                    cursor.execute("SELECT id "
                                                   "FROM Food "
                                                   "WHERE name = '"+food_select+"';")
                                    id_food = cursor.fetchone()[0]
                                    query_insert_food_user = "INSERT INTO Food_User " \
                                                             "(id_user, id_food) " \
                                                             "VALUES (" + str(id_user) + ", "\
                                                             + str(id_food)+");"
                                    cursor.execute(query_insert_food_user)
                                    connexion.commit()
                                    break
                                elif choosen_foods_substitute in ['N', 'n']:
                                    break
                                else:
                                    print("Saisie incorrecte ! \n")
                    elif choosen_foods == "N" or choosen_foods == "n":
                        break
                    else:
                        print("Veuillez choisir le bon numero de l'aliment souhaité .. \n")
            elif choosen_category == "N" or choosen_category == "n":
                break
            else:
                print("Veuillez choisir le bon numero de la categorie souhaitée .. \n")

    @staticmethod
    def get_user_foods(connexion, id_user):
        """
        Select the food what user selected.
        :return: list of the food what user replaced
        """
        cursor = connexion.cursor()
        query_select_food_user = "SELECT * " \
                                 "FROM Food, Food_User " \
                                 "WHERE Food.id = Food_User.id_food " \
                                 "AND Food_User.id_user = " + str(id_user) + ";"
        cursor.execute(query_select_food_user)
        if cursor.fetchone() is None:
            print("Vous n'avez substitué aucun aliment..\n")
        else:
            users_foods = Main.make_dict_element(cursor,
                                                 query_select_food_user,
                                                 None,
                                                 True,
                                                 [1, 2, 3, 4])
            print("liste des aliments que j'ai substitué :")
            for num_food in users_foods:
                current_food = users_foods[num_food]
                display_food = "  " + str(num_food) + " - " + current_food[0] + " - " \
                               + current_food[1] + " - " + current_food[2]

                if current_food[3] == '':
                    # some foods don't contain a place
                    display_food = '{}{}'.format(display_food, " - (Lieu non precisé)")
                else:
                    display_food = display_food + " - " + current_food[3]
                print(display_food)

            while True:
                do_want_remove = input("\nVoulez vous supprimer un aliment (O/N) ? ")
                if do_want_remove in ['O', 'o']:
                    food_is_selected = False
                    while not food_is_selected:
                        food_remove = Main.convert_choice_user(
                            "Selectionner le numero de l'aliment à supprimer (ou N pour annuler): ")
                        if food_remove in users_foods.keys():
                            food_selected_for_remove = users_foods[food_remove]
                            query_select_food = "SELECT id " \
                                                "FROM Food " \
                                                "WHERE name = '"+food_selected_for_remove[0]+"';"
                            cursor.execute(query_select_food)
                            query_remove_food = "DELETE FROM Food_User " \
                                                "WHERE id_food='"+str(cursor.fetchone()[0])+"' " \
                                                "AND id_user='"+str(id_user)+"';"
                            cursor.execute(query_remove_food)
                            connexion.commit()
                            food_is_selected = True
                        elif food_remove in ['N', 'n']:
                            break
                        else:
                            print("Saisie incorrecte ! ")
                elif do_want_remove in ['N', 'n']:
                    break
            print("\n")

    @staticmethod
    def put_food_in_db(connexion):
        """
        Get json files for put elements in database.
        :return:
        """
        food_category = {}
        list_categories_in_db = []
        list_food_in_db = []
        for num_page in range(1, 25):
            foods = requests.get(
                'https://fr-en.openfoodfacts.org/category/pizzas/' + str(num_page) + '.json').json()
            cursor = connexion.cursor()
            for food in foods['products']:
                # Products wihout nutrition grades not will insert in database.
                if 'nutrition_grades' in food.keys():
                    if 'product_name_fr' not in food.keys():
                        product_name = food['product_name']
                    else:
                        product_name = food['product_name_fr']
                    if '\'' in product_name:
                        product_name = product_name.replace('\'', '')

                    if 'purchase_places' in food.keys():
                        if '\'' in food['purchase_places']:
                            product_place = food['purchase_places'].replace('\'', '')
                        else:
                            product_place = food['purchase_places']
                    else:
                        product_place = ''

                    if product_name.lower() not in list_food_in_db:
                        list_food_in_db.append(product_name.lower())
                        if product_name != '':
                            request_insert = "INSERT INTO Food (name, nutri_score, web_link, place) " \
                                             "VALUES ('" + product_name + "', '" \
                                             + food['nutrition_grades'] + "', '"\
                                             + food['url'] + "', '" + product_place + "');"
                            cursor.execute(request_insert)
                            food_category[product_name] = []
                            # for each product, we get all categories which product is associate
                            list_categories = food['categories'].split(',')
                            list_categories = [category.lower() for category in list_categories]
                            for category in list_categories:
                                if 'en:' in category or 'fr:' in category or 'de' in category or 'it' in category:
                                    category = category[3:]
                                    if ':' in category:
                                        # In some case, categories have a ':' in the and of them name.
                                        category = category[1:]
                                if category not in list_categories_in_db:
                                    # We check if category is not exist for insert it
                                    list_categories_in_db.append(category)
                                    cursor.execute("INSERT INTO Category (name) "
                                                   "VALUES ('" + category + "');")
                                food_category[product_name].append(category)

                        connexion.commit()

                    # We associate each food with them categories
                    if product_name != '':
                        for food, list_category in food_category.items():
                            cursor.execute("SELECT id FROM Food WHERE name = '" + product_name + "';")
                            for id_food in cursor.fetchone():
                                for category in list_category:
                                    cursor.execute("SELECT id FROM Category WHERE name = '" + category + "';")
                                    for id_category in cursor.fetchall():
                                        cursor.execute("SELECT * "
                                                       "FROM Food_Category "
                                                       "WHERE id_food = '" + str(id_food) + "'"
                                                       "AND id_category = '" + str(id_category[0]) + "';")
                                        # We check if we don't have the same food associate at the same category
                                        if cursor.fetchone() is None:
                                            request_put_food_category = "INSERT INTO Food_Category" \
                                                                        "(id_food, id_category) " \
                                                                    "VALUES (" + str(id_food) + ", " \
                                                                    + str(id_category[0]) + ");"
                                            cursor.execute(request_put_food_category)
                        connexion.commit()
