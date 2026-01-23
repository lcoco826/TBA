"""
Actions module - Gère toutes les actions exécutables par le joueur.

Ce module contient la classe Actions avec des méthodes statiques pour chaque commande.
Chaque action prend en paramètre:
- game (Game): L'instance du jeu
- list_of_words (list): Les mots saisis par l'utilisateur
- number_of_parameters (int): Le nombre de paramètres attendus

Les méthodes valident l'entrée et retournent True si l'action réussit.
"""

# Messages d'erreur informatifs
MSG0 = ("\n❌ Erreur: La commande '{command_word}' ne prend pas de paramètre.\n"
        "   Utilisation: {command_word}\n")
MSG1 = ("\n❌ Erreur: La commande '{command_word}' nécessite exactement 1 paramètre.\n"
        "   Utilisation: {command_word} <paramètre>\n")
MSG_HELP = "\n💡 Tapez 'help' pour voir toutes les commandes disponibles.\n"

def _validate_param_count(list_of_words, expected_count):
    """
    Valide le nombre de paramètres.
    
    Args:
        list_of_words (list): Liste des mots saisis
        expected_count (int): Nombre de paramètres attendus
        
    Returns:
        tuple: (est_valide, message_erreur)
    """
    actual_count = len(list_of_words) - 1  # Exclure la commande elle-même
    if actual_count != expected_count:
        return False, f"attendu {expected_count}, reçu {actual_count}"
    return True, ""

class Actions:
    """
    Classe contenant toutes les actions disponibles du jeu.
    
    Chaque méthode correspond à une commande et suit le pattern:
    - Valide les paramètres
    - Exécute l'action
    - Retourne True/False et affiche les messages appropriés
    """

    @staticmethod
    def go(game, list_of_words, number_of_parameters):
        """
        Se déplacer dans une direction cardinale.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["go", direction]
            number_of_parameters (int): 1
            
        Directions valides: N, S, E, O, U, D (et variantes: NORD, SUD, EST, OUEST, UP, DOWN)
        
        Returns:
            bool: True si le déplacement a réussi
            
        Exemples:
            >>> go(game, ["go", "N"], 1)  # Se déplacer au nord
            >>> go(game, ["go", "NORD"], 1)  # Fonctionne aussi
        """

        player = game.player
        length = len(list_of_words)

        # Validation du nombre de paramètres
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            print(MSG_HELP)
            return False

        direction = list_of_words[1].strip()

        # Validation: direction non vide
        if not direction:
            print("\n❌ Direction invalide: la direction ne peut pas être vide.\n")
            return False
        player.move(direction)
        return True

    @staticmethod
    def quit(game, list_of_words, number_of_parameters):
        """
        Quitter le jeu de manière propre.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["quit"]
            number_of_parameters (int): 0
            
        Returns:
            bool: True si la commande a réussi
            
        Exemples:
            >>> quit(game, ["quit"], 0)  # Quitter le jeu
        """
        length = len(list_of_words)

        # Validation
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            print(MSG_HELP)
            return False

        player = game.player
        if not player:
            print("\n❌ Erreur: Aucun joueur actif.\n")
            return False

        msg = f"\nMerci {player.name} d'avoir joué. À bientôt ! 👋\n"
        print(msg)
        game.finished = True
        return True

    @staticmethod
    def restart(game, list_of_words, number_of_parameters):
        """
        Recommencer le jeu depuis le début.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["restart"]
            number_of_parameters (int): 0
        """
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        print("\n🔄 Redémarrage du jeu...\n")

        # Réinitialisation complète de l'état du jeu
        game.rooms = []
        game.commands = {}
        game.valid_directions = set()
        game.player = None
        game.quest_manager = None
        game.finished = False
        game.victory = False

        # Relancer la configuration
        game.setup()

        # Afficher le message de bienvenue
        game.print_welcome()

        return False

    @staticmethod
    def help(game, list_of_words, number_of_parameters):
        """
        Afficher l'aide et la liste des commandes disponibles.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["help"]
            number_of_parameters (int): 0
            
        Returns:
            bool: True si la commande a réussi
            
        Exemples:
            >>> help(game, ["help"], 0)  # Voir toutes les commandes
        """
        length = len(list_of_words)

        # Validation
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        # Afficher la liste des commandes disponibles
        print("\n" + "="*50)
        print("📋 AIDE - Commandes disponibles :")
        print("="*50)
        for command in game.commands.values():
            print("\t- " + str(command))
        print("="*50 + "\n")
        return False


    @staticmethod
    def look(game, list_of_words, number_of_parameters):
        """
        Examiner la pièce actuelle en détail.
        
        Affiche:
        - La description longue de la pièce
        - Les sorties disponibles
        - Les items présents
        - Les personnages présents
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["look"]
            number_of_parameters (int): 0
            
        Exemples:
            >>> look(game, ["look"], 0)  # Examiner la pièce
        """
        length = len(list_of_words)

        # Validation
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        # Afficher la description longue de la pièce
        print(game.player.current_room.get_long_description())

        # Afficher les items présents dans la pièce
        room = game.player.current_room
        if not room.inventory:
            print("\n📭 Il n'y a aucun objet dans ce lieu.")
        else:
            print("\n📦 Vous voyez les objets suivants :")
            for item in room.inventory.values():
                print(f"    - {item}")

        return False


    @staticmethod
    def take(game, list_of_words, _number_of_parameters):
        """
        Prendre un objet dans la salle actuelle.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["take", nom_item]
            number_of_parameters (int): 1
            
        Validation:
        - L'item doit exister dans la salle
        - Le poids total ne doit pas dépasser la limite (10 kg)
        
        Erreurs possibles:
        - Item introuvable
        - Inventaire plein (poids)
        
        Exemples:
            >>> take(game, ["take", "tresor"], 1)  # Prendre un trésor
        """
        # Validation du nombre de paramètres
        if len(list_of_words) < 2:
            print("\n❌ Erreur: Prendre quoi ?")
            print("   Utilisation: take <nom_item>\n")
            return False

        item_name = list_of_words[1].strip().lower()

        # Validation: nom d'item non vide
        if not item_name:
            print("\n❌ Erreur: Le nom de l'item ne peut pas être vide.\n")
            return False

        # Vérifier si l'item existe dans la pièce
        room = game.player.current_room
        found_item = None
        for key, item in room.inventory.items():
            if key.lower() == item_name:
                found_item = key
                break

        if not found_item:
            print(f"\n❌ Il n'y a pas de '{item_name}' ici.")
            items_str = ', '.join(room.inventory.keys()) if room.inventory else 'aucun'
            print(f"   Items disponibles : {items_str}\n")
            return False

        item = room.inventory[found_item]

        # Vérifier si le joueur peut porter l'objet (poids)
        current_weight = sum(i.weight for i in game.player.inventory.values())
        max_weight = game.player.max_weight

        if current_weight + item.weight > max_weight:
            remaining_capacity = max_weight - current_weight
            print(f"\n❌ Vous ne pouvez pas porter '{found_item}'.")
            print(f"   Poids actuel : {current_weight:.1f} kg / {max_weight} kg")
            print(f"   Poids de l'item : {item.weight:.1f} kg")
            print(f"   Capacité restante : {remaining_capacity:.1f} kg\n")
            return False

        # Ajouter l'item à l'inventaire du joueur
        game.player.inventory[found_item] = item
        del room.inventory[found_item]

        print(f"\n✅ Vous avez pris l'objet '{found_item}'.")
        print(f"   Poids actuel : {current_weight + item.weight:.1f} kg / {max_weight} kg\n")

        # Vérifier les objectifs de quête
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("prendre", found_item)
        except Exception: # pylint: disable=broad-exception-caught
            pass

        return True


    @staticmethod
    def drop(game, list_of_words, _number_of_parameters):
        """
        Déposer un objet de l'inventaire dans la salle actuelle.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["drop", nom_item]
            number_of_parameters (int): 1
            
        Validation:
        - L'item doit être dans l'inventaire du joueur
        
        Exemples:
            >>> drop(game, ["drop", "tresor"], 1)  # Déposer un trésor
        """
        # Validation du nombre de paramètres
        if len(list_of_words) < 2:
            print("\n❌ Erreur: Déposer quoi ?")
            print("   Utilisation: drop <nom_item>\n")
            return False

        item_name = list_of_words[1].strip().lower()

        # Validation: nom d'item non vide
        if not item_name:
            print("\n❌ Erreur: Le nom de l'item ne peut pas être vide.\n")
            return False

        # Vérifier si l'item existe dans l'inventaire
        found_item = None
        for key, item in game.player.inventory.items():
            if key.lower() == item_name:
                found_item = key
                break

        if not found_item:
            print(f"\n❌ Vous n'avez pas de '{item_name}' dans votre inventaire.")
            inv_list = ', '.join(game.player.inventory.keys()) if game.player.inventory else 'vide'
            print(f"   Inventaire: {inv_list}\n")
            return False

        item = game.player.inventory[found_item]

        # Ajouter l'item à la pièce
        game.player.current_room.inventory[found_item] = item
        del game.player.inventory[found_item]

        print(f"\n✅ Vous avez déposé l'objet '{found_item}'.\n")

        # Interaction spécifique : Bananes -> Singes (via drop)
        if found_item == "bananes" and "Singes" in game.player.current_room.characters:
            print("Les singes se précipitent sur les bananes que vous avez laissées tomber !")
            print("Singes disent : 'Merci, tu peux désormais continuer ton aventure.'\n")

            # Mettre à jour le message des singes
            msg = ["Merci, tu peux désormais continuer ton aventure."]
            game.player.current_room.characters["Singes"].msgs = msg

            # Les singes prennent les bananes (on les retire du sol)
            if found_item in game.player.current_room.inventory:
                del game.player.current_room.inventory[found_item]

            # Valider l'objectif de quête "donner bananes"
            try:
                if hasattr(game, 'quest_manager'):
                    game.quest_manager.check_action_objectives("donner", found_item)
            except Exception: # pylint: disable=broad-exception-caught
                pass

        return True

    @staticmethod
    def check(game, list_of_words, number_of_parameters):
        """
        Vérifier le contenu de l'inventaire du joueur.
        
        Affiche:
        - La liste des items possédés
        - Le poids total
        - La capacité restante
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["check"]
            number_of_parameters (int): 0
            
        Exemples:
            >>> check(game, ["check"], 0)  # Voir l'inventaire
        """
        length = len(list_of_words)

        # Validation
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        player = game.player
        inventory = player.inventory

        # Afficher l'inventaire
        if not inventory:
            print("\n📭 Votre inventaire est vide.\n")
        else:
            current_weight = sum(i.weight for i in inventory.values())
            max_weight = player.max_weight
            remaining = max_weight - current_weight

            print("\n" + "="*50)
            print("📦 INVENTAIRE")
            print("="*50)
            for item in inventory.values():
                print(f"  - {item}")
            print("-" * 50)
            print(f"Poids total : {current_weight:.1f} kg / {max_weight} kg")
            print(f"Capacité restante : {remaining:.1f} kg")
            print("="*50 + "\n")

        return False

    # Charge the beamer

    @staticmethod
    def charge(game, _params, _n_params):
        """Charger le beamer si le joueur en possède un."""
        player = game.player

        # Vérifier si le joueur possède un beamer
        if "beamer" not in player.inventory:
            print("\nVous n'avez pas de beamer !\n")
            return False

        beamer = player.inventory["beamer"]

        if getattr(beamer, "fixed_destination", False):
            print("\nCe beamer est déjà programmé pour une destination précise.\n")
            return False

        # Enregistrer la salle actuelle
        beamer.saved_room = player.current_room
        print("\nLe beamer est chargé !\n")
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("charger", "beamer")
        except Exception: # pylint: disable=broad-exception-caught
            pass
        return True

    @staticmethod
    def fire(game, _params, _n_params):
        """Utiliser le beamer pour se téléporter."""
        player = game.player

        if "beamer" not in player.inventory:
            print("\nVous n'avez pas de beamer !\n")
            return False

        beamer = player.inventory["beamer"]

        # Le beamer n'a jamais été chargé
        if not hasattr(beamer, "saved_room"):
            print("\nLe beamer n'est pas chargé !\n")
            return False

        # Téléportation
        player.current_room = beamer.saved_room

        if player.current_room.name == "Beach":
            print("\nVous voilà de retour à la plage, Jacob semble vouloir parler.\n")

            jacob = None
            if "Jacob" in player.current_room.characters:
                jacob = player.current_room.characters["Jacob"]
            else:
                for room in game.rooms:
                    if "Jacob" in room.characters:
                        jacob = room.characters.pop("Jacob")
                        player.current_room.characters["Jacob"] = jacob
                        jacob.current_room = player.current_room
                        break

            if jacob:
                msg = ["Capitaine, vous et votre équipage avez réussi ! "
                       "Êtes-vous prêt à repartir ? (oui/non)"]
                jacob.msgs = msg
                player.endgame_ready = True
                player.endgame_awaiting_response = False
        else:
            print("\nVous êtes téléporté !\n")

        print(player.current_room.get_long_description())
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("utiliser", "beamer")
        except Exception: # pylint: disable=broad-exception-caught
            pass
        return True

    # Dans actions.py


    @staticmethod
    def talk(game, list_of_words, _number_of_parameters):
        """
        Parler avec un personnage non-joueur présent dans la pièce.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["talk", nom_personnage]
            number_of_parameters (int): 1
            
        Validation:
        - Le personnage doit être présent dans la pièce actuelle
        
        Exemples:
            >>> talk(game, ["talk", "Jacob"], 1)  # Parler au perroquet Jacob
        """
        # Validation du nombre de paramètres
        if len(list_of_words) < 2:
            print("\n❌ Erreur: Parler avec qui ?")
            print("   Utilisation: talk <nom_personnage>\n")
            room = game.player.current_room
            if room.characters:
                print(f"   Personnages disponibles : {', '.join(room.characters.keys())}\n")
            return False

        character_name = list_of_words[1].strip()
        room = game.player.current_room

        # Validation: nom du personnage non vide
        if not character_name:
            print("\n❌ Erreur: Le nom du personnage ne peut pas être vide.\n")
            return False

        # Recherche insensible à la casse
        found_key = None
        for key in room.characters.keys():
            if key.lower() == character_name.lower():
                found_key = key
                break

        # Vérifier si le personnage est dans la pièce actuelle
        if not found_key:
            print(f"\n❌ {character_name} n'est pas ici.")
            if room.characters:
                chars = ', '.join(room.characters.keys())
                print(f"   Personnages disponibles : {chars}\n")
            else:
                print("   Il n'y a personne à qui parler dans cette pièce.\n")
            return False

        # Récupérer le personnage et afficher son message
        character = room.characters[found_key]
        msg = character.get_msg()
        print(f"\n{msg}\n")

        # Activer la réponse oui/non si Jacob pose la question de fin
        if (character.name == "Jacob" and game.player.current_room.name == "Beach"
                and "Êtes-vous prêt à repartir" in msg):
            game.player.endgame_awaiting_response = True


        # Vérifier les objectifs de quête
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("parler", found_key)
        except Exception: # pylint: disable=broad-exception-caught
            pass

        return True

    @staticmethod
    def give(game, list_of_words, _number_of_parameters):
        """
        Donner un objet à un personnage.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["give", nom_item]
            number_of_parameters (int): 1
        """
        # Validation du nombre de paramètres
        if len(list_of_words) < 2:
            print("\n❌ Erreur: Donner quoi ?")
            print("   Utilisation: give <nom_item>\n")
            return False

        item_name = list_of_words[1].strip().lower()

        # Vérifier si l'item existe dans l'inventaire
        found_item = None
        for key in game.player.inventory:
            if key.lower() == item_name:
                found_item = key
                break

        if not found_item:
            print(f"\n❌ Vous n'avez pas de '{item_name}' dans votre inventaire.\n")
            return False

        # Vérifier s'il y a un personnage dans la pièce
        room = game.player.current_room
        if not room.characters:
            print("\n❌ Il n'y a personne à qui donner cela ici.\n")
            return False

        # Récupérer le premier personnage (simplification)
        target_char = list(room.characters.values())[0]

        # Retirer l'item de l'inventaire
        game.player.inventory.pop(found_item)

        print(f"\n✅ Vous donnez '{found_item}' à {target_char.name}.\n")

        # Interaction spécifique : Bananes -> Singes
        if found_item == "bananes" and target_char.name == "Singes":
            print(f"{target_char.name} disent : "
                  "'Merci, tu peux désormais continuer ton aventure.'\n")
            target_char.msgs = ["Merci, tu peux désormais continuer ton aventure."]

        # Vérifier les objectifs de quête
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("donner", found_item)
        except Exception: # pylint: disable=broad-exception-caught
            pass

        return True

    @staticmethod
    def debug(game, list_of_words, number_of_parameters):
        """Basculer le mode DEBUG du jeu (affiche/masque les messages DEBUG)."""
        # Ne prend pas de paramètre
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        # Toggle global DEBUG in the game module
        try:
            # game module stores DEBUG at top-level
            current = getattr(game, 'DEBUG', None)
            # pylint: disable=import-outside-toplevel
            import game as game_mod
            if current is None:
                current = getattr(game_mod, 'DEBUG', False)

            new = not current
            # Set both the instance attribute (if present) and module-level flag
            try:
                setattr(game, 'DEBUG', new)
            except Exception: # pylint: disable=broad-exception-caught
                pass
            setattr(game_mod, 'DEBUG', new)

            print(f"\nDEBUG : {'ON' if new else 'OFF'}\n")

            # If we just turned DEBUG ON, print the buffered messages
            if new:
                try:
                    buf = getattr(game_mod, 'DEBUG_LOG', [])
                    if buf:
                        print("--- Messages DEBUG enregistrés ---")
                        for m in buf:
                            print(m)
                        # Clear buffer after showing
                        game_mod.DEBUG_LOG = []
                except Exception: # pylint: disable=broad-exception-caught
                    pass

            return False
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"\nImpossible de basculer DEBUG : {e}\n")
            return False

    @staticmethod
    def back(game, list_of_words, number_of_parameters):
        """
        Revenir à la salle précédente.
        
        Paramètres:
            game (Game): L'instance du jeu
            list_of_words (list): ["back"]
            number_of_parameters (int): 0
            
        Validation:
        - L'historique doit avoir au moins une salle
        - Il doit exister un chemin de retour (pas de passage unidirectionnel)
        
        Erreurs possibles:
        - Aucune salle antérieure
        - Passage unidirectionnel (aucun retour possible)
        
        Exemples:
            >>> back(game, ["back"], 0)  # Revenir à la salle précédente
        """
        length = len(list_of_words)

        # Validation
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        success = game.player.back()
        return success

    @staticmethod
    def show_quests(game, list_of_words, number_of_parameters):
        """Afficher la liste des quêtes (commande `quests`)."""
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.show_quests()
            else:
                print("\nAucun gestionnaire de quêtes disponible.\n")
            return False
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"\nErreur lors de l'affichage des quêtes: {e}\n")
            return False

    @staticmethod
    def show_quest(game, list_of_words, _number_of_parameters):
        """Afficher les détails d'une quête (commande `quest <titre>`)."""
        # On accepte plusieurs mots pour le titre,
        # donc on vérifie juste qu'il y a au moins un paramètre
        if len(list_of_words) < 2:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Reconstituer le titre avec les espaces
        quest_title = " ".join(list_of_words[1:])
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.show_quest_details(quest_title)
            else:
                print("\nAucun gestionnaire de quêtes disponible.\n")
            return False
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"\nErreur lors de l'affichage de la quête: {e}\n")
            return False

    @staticmethod
    def show_rewards(game, list_of_words, number_of_parameters):
        """Afficher les récompenses obtenues par le joueur (commande `rewards`)."""
        length = len(list_of_words)
        if length != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        try:
            player = game.player
            if not player:
                print("\nAucun joueur chargé.\n")
                return False
            print(player.get_rewards())
            return False
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"\nErreur lors de l'affichage des récompenses: {e}\n")
            return False

    @staticmethod
    def yes(game, _list_of_words, _number_of_parameters):
        """Répondre 'oui' à une question."""
        player = game.player
        # Vérifier si on est en fin de jeu avec Jacob et qu'on a parlé avec lui
        if (getattr(player, "endgame_ready", False)
                and getattr(player, "endgame_awaiting_response", False)
                and player.current_room.name == "Beach"):
            print("\nJacob hoche la tête. Vous levez l'ancre et naviguez "
                  "vers de nouvelles aventures !")
            game.victory = True
            game.finished = True
            return True
        print("\nIl n'y a rien à confirmer ici.\n")
        return False

    @staticmethod
    def no(game, _list_of_words, _number_of_parameters):
        """Répondre 'non' à une question."""
        player = game.player
        # Vérifier si on est en fin de jeu avec Jacob et qu'on a parlé avec lui
        if (getattr(player, "endgame_ready", False)
                and getattr(player, "endgame_awaiting_response", False)
                and player.current_room.name == "Beach"):
            print("\nJacob dit : 'Très bien, vous n'avez qu'à revenir me voir "
                  "quand vous voudrez partir.'\n")
            player.endgame_awaiting_response = False
            return True
        print("\nIl n'y a rien à refuser ici.\n")
        return False
