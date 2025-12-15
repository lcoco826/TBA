# Description: The actions module.

# The actions module contains the functions that are called when a command is executed.
# Each function takes 3 parameters:
# - game: the game object
# - list_of_words: the list of words in the command
# - number_of_parameters: the number of parameters expected by the command
# The functions return True if the command was executed successfully, False otherwise.
# The functions print an error message if the number of parameters is incorrect.
# The error message is different depending on the number of parameters expected by the command.


# The error message is stored in the MSG0 and MSG1 variables and formatted with the command_word variable, the first word in the command.
# The MSG0 variable is used when the command does not take any parameter.
MSG0 = "\nLa commande '{command_word}' ne prend pas de paramètre.\n"
# The MSG1 variable is used when the command takes 1 parameter.
MSG1 = "\nLa commande '{command_word}' prend 1 seul paramètre.\n"

class Actions:
    def go(game, list_of_words, number_of_parameters):
        """
        Move the player in the direction specified by the parameter.
        The parameter must be a cardinal direction (N, E, S, O).

        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:
        
        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> go(game, ["go", "N"], 1)
        True
        >>> go(game, ["go", "N", "E"], 1)
        False
        >>> go(game, ["go"], 1)
        False

        """
        
        player = game.player
        l = len(list_of_words)
        # If the number of parameters is incorrect, print an error message and return False.
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG1.format(command_word=command_word))
            return False

        # Get the direction from the list of words.
        direction = list_of_words[1]
        # Move the player in the direction specified by the parameter.
        player.move(direction)
        return True

    def quit(game, list_of_words, number_of_parameters):
        """
        Quit the game.

        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:

        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> quit(game, ["quit"], 0)
        True
        >>> quit(game, ["quit", "N"], 0)
        False
        >>> quit(game, ["quit", "N", "E"], 0)
        False

        """
        l = len(list_of_words)
        # If the number of parameters is incorrect, print an error message and return False.
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        
        # Set the finished attribute of the game object to True.
        player = game.player
        msg = f"\nMerci {player.name} d'avoir joué. Au revoir.\n"
        print(msg)
        game.finished = True
        return True

    def help(game, list_of_words, number_of_parameters):
        """
        Print the list of available commands.
        
        Args:
            game (Game): The game object.
            list_of_words (list): The list of words in the command.
            number_of_parameters (int): The number of parameters expected by the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.

        Examples:

        >>> from game import Game
        >>> game = Game()
        >>> game.setup()
        >>> help(game, ["help"], 0)
        True
        >>> help(game, ["help", "N"], 0)
        False
        >>> help(game, ["help", "N", "E"], 0)
        False

        """

        # If the number of parameters is incorrect, print an error message and return False.
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False
        
        # Print the list of available commands.
        print("\nVoici les commandes disponibles:")
        for command in game.commands.values():
            print("\t- " + str(command))
        print()
        return True # Look around the current room


    def look(game, list_of_words, number_of_parameters):
        # Afficher la description longue de la pièce
        print(game.player.current_room.get_long_description())
    
        # Afficher les items présents dans la pièce
        if not game.player.current_room.inventory:
            print("\nIl n'y a aucun objet dans ce lieu.")
        else:
            print("\nVous voyez les objets suivants :")
        for item in game.player.current_room.inventory.values():
            print(f"    - {item}")

    
    # Take an item from the current room
    # Take an item from the current room
    def take(game, list_of_words, number_of_parameters):
        # Vérifier qu'un nom d'item a été spécifié
        if len(list_of_words) < 2:
            print("\nPrendre quoi ?")
            return
    
        # Récupérer le nom de l'item
        item_name = list_of_words[1]
    
        # Vérifier si l'item existe dans la pièce
        if item_name not in game.player.current_room.inventory:
            print(f"\nIl n'y a pas de '{item_name}' ici.")
            return
    
        # Récupérer l'objet Item
        item = game.player.current_room.inventory[item_name]
    
        # Vérifier si le joueur peut porter l'objet (poids)
        current_weight = sum(i.weight for i in game.player.inventory.values())
        if current_weight + item.weight > game.player.max_weight:
            print(f"\nVous ne pouvez pas porter '{item_name}'. Votre inventaire est trop lourd ! (Poids actuel: {current_weight} kg, Max: {game.player.max_weight} kg)")
            return
    
        # Ajouter l'item à l'inventaire du joueur
        game.player.inventory[item_name] = item
    
        # Retirer l'item de la pièce
        del game.player.current_room.inventory[item_name]
    
        # Message de confirmation
        print(f"\nVous avez pris l'objet '{item_name}'.")
        # Vérifier les objectifs de quête liés à l'action 'prendre'
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("prendre", item_name)
        except Exception:
            pass


    # Drop an item in the current room
    def drop(game, list_of_words, number_of_parameters):
        # Vérifier qu'un nom d'item a été spécifié
        if len(list_of_words) < 2:
            print("\nDéposer quoi ?")
            return
    
        # Récupérer le nom de l'item
        item_name = list_of_words[1]
    
        # Vérifier si l'item existe dans l'inventaire du joueur
        if item_name not in game.player.inventory:
            print(f"\nVous n'avez pas de '{item_name}' dans votre inventaire.")
            return
    
        # Récupérer l'objet Item
        item = game.player.inventory[item_name]
    
        # Ajouter l'item à la pièce
        game.player.current_room.inventory[item_name] = item
    
        # Retirer l'item de l'inventaire du joueur
        del game.player.inventory[item_name]
    
        # Message de confirmation
        print(f"\nVous avez déposé l'objet '{item_name}'.")

    # Check player's inventory
    def check(game, list_of_words, number_of_parameters):
        print(game.player.get_inventory())

    # Charge the beamer

    def charge(game, params, n_params):
        """Charger le beamer si le joueur en possède un."""
        player = game.player

        # Vérifier si le joueur possède un beamer
        if "beamer" not in player.inventory:
            print("\nVous n'avez pas de beamer !\n")
            return

        beamer = player.inventory["beamer"]

        # Enregistrer la salle actuelle
        beamer.saved_room = player.current_room
        print("\nLe beamer est chargé !\n")
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("charger", "beamer")
        except Exception:
            pass

    def fire(game, params, n_params):
        """Utiliser le beamer pour se téléporter."""
        player = game.player

        if "beamer" not in player.inventory:
            print("\nVous n'avez pas de beamer !\n")
            return

        beamer = player.inventory["beamer"]

        # Le beamer n'a jamais été chargé
        if not hasattr(beamer, "saved_room"):
            print("\nLe beamer n'est pas chargé !\n")
            return

        # Téléportation
        player.current_room = beamer.saved_room
        print("\nVous êtes téléporté !\n")
        print(player.current_room.get_long_description())
        try:
            if hasattr(game, 'quest_manager'):
                game.quest_manager.check_action_objectives("utiliser", "beamer")
        except Exception:
            pass

    # Dans actions.py


    def talk(game, list_of_words, number_of_parameters):
        """
        Parler avec un personnage non-joueur.
    
        Args:
            game: L'instance du jeu
            list_of_words: Liste des mots de la commande
            number_of_parameters: Nombre de paramètres attendus
        """
        # Vérifier qu'un nom de personnage a été fourni
        if len(list_of_words) < 2:
            print("\nParler avec qui ? Utilisez : talk <nom>\n")
            return
    
        character_name = list_of_words[1]
    
        # Vérifier si le personnage est dans la pièce actuelle
        if character_name not in game.player.current_room.characters:
            print(f"\n{character_name} n'est pas ici.\n")
            return
    
        # Récupérer le personnage et afficher son message
        character = game.player.current_room.characters[character_name]
        print(f"\n{character.get_msg()}\n")
        # Vérifier les objectifs liés à la conversation
        try:
            if hasattr(game, 'quest_manager'):
                # utiliser le verbe français 'parler'
                game.quest_manager.check_action_objectives("parler", character_name)
        except Exception:
            pass

    def debug(game, list_of_words, number_of_parameters):
        """Basculer le mode DEBUG du jeu (affiche/masque les messages DEBUG)."""
        # Ne prend pas de paramètre
        l = len(list_of_words)
        if l != number_of_parameters + 1:
            command_word = list_of_words[0]
            print(MSG0.format(command_word=command_word))
            return False

        # Toggle global DEBUG in the game module
        try:
            # game module stores DEBUG at top-level
            current = getattr(game, 'DEBUG', None)
            import game as game_mod
            if current is None:
                current = getattr(game_mod, 'DEBUG', False)

            new = not current
            # Set both the instance attribute (if present) and module-level flag
            try:
                setattr(game, 'DEBUG', new)
            except Exception:
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
                except Exception:
                    pass

            return True
        except Exception as e:
            print(f"\nImpossible de basculer DEBUG : {e}\n")
            return False
    
    def back(game, list_of_words, number_of_parameters):
        """
        Permet au joueur de revenir à la salle précédente.
        Args:
            game : l'objet Game
            list_of_words : les mots de la commande
            number_of_parameters : nombre de paramètres attendus
        """
        game.player.back()