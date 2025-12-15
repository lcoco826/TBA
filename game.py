# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions
from quest import Quest, QuestManager
import os
import sys

# DEBUG can be enabled in three ways (priority order):
# 1) Command-line flag `--debug`
# 2) Environment variable `GAME_DEBUG=1` or `GAME_DEBUG=true`
# 3) Default value False
def _detect_debug():
    if any(arg == "--debug" for arg in sys.argv[1:]):
        return True
    env = os.getenv("GAME_DEBUG", "0").lower()
    if env in ("1", "true", "yes", "on"):
        return True
    return False

DEBUG = _detect_debug()
# Buffer pour stocker les messages DEBUG afin de les afficher ultérieurement
DEBUG_LOG = []

class Game:

    # Constructor
    def __init__(self):
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.valid_directions = set()
    # Setup the game
    def setup(self):

        # Setup commands

        help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = help
        quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = quit
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O,U,D)", Actions.go, 1)
        self.commands["go"] = go
        look = Command("look", " : regarder autour de soi", Actions.look, 0)
        self.commands["look"] = look
        back = Command("back", " : revenir à la salle précédente", Actions.back, 0)
        self.commands["back"] = back

        # Setup rooms
        beach = Room("Beach", "une plage de sable blanc. Vous entendez l'écume grésiller doucement lorsque la vague se brise et se retire sur les galets.")
        self.rooms.append(beach)
        cove = Room("Cove", "une crique isolée, perdue entre mer et falaises.")
        self.rooms.append(cove)
        forest = Room("Forêt", "une forêt tropicale, dense et humide.")
        self.rooms.append(forest)
        lagoon = Room("Lagoon", "la lagune s'étire paisiblement, ses eaux turquoises reflétant le ciel.")
        self.rooms.append(lagoon)
        cliff = Room("Cliff", "la falaise, elle se détache sur l'horizon, comme un mur de pierre.")
        self.rooms.append(cliff)
        volcano = Room("Volcano", "un volcan, majestueux domine l'île, ses flancs noirs et rugueux témoignent des anciennes coulées de lave.")
        self.rooms.append(volcano)
        cave = Room("Cave", "une grotte mystérieuse et sombre se cache derrière la cascade.")
        self.rooms.append(cave)
        waterfall = Room("Waterfall", "la cascade qui dévale la falaise avec fracas, projetant des éclats d'eau créant un nuage de brume.")
        self.rooms.append(waterfall)

        # Create exits for rooms

        beach.exits = {"N" : forest, "E" : None, "S" : None, "O" : cove, "U" : None, "D": None}
        cove.exits = {"N" : lagoon, "E" : beach, "S" : None, "O" : None, "U" : None, "D": None}
        forest.exits = {"N" : None, "E" : None, "S" : beach, "O" : lagoon, "U" : None, "D": None}
        lagoon.exits = {"N" : cave, "E" : forest, "S" : cove, "O" : None, "U" : None, "D": None}
        cave.exits = {"N": None, "E" : volcano, "S" : lagoon, "O" : None, "U" : cliff, "D": None}
        cliff.exits = {"N": None, "E" : None, "S": None, "O" : None, "U" : None, "D" : cave}
        volcano.exits = {"N": None, "E" : None, "S": None, "O" : cave, "U" : waterfall, "D" : forest}
        waterfall.exits = {"N" : None, "E" : None, "S" : None, "O" : None, "U": None, "D": volcano}

        for room in self.rooms :
            self.valid_directions.update([d for d in room.exits.keys() if room.exits[d] is not None])

        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = beach

        # Initialise le gestionnaire de quêtes pour ce joueur
        self.quest_manager = QuestManager(self.player)

        # Exemple de quêtes adaptées au monde actuel
        q_explore = Quest(
            "Explorer l'île",
            "Visitez plusieurs lieux importants de l'île.",
            [f"Visiter {r.name}" for r in (beach, forest, lagoon)],
            reward="Carte de l'île"
        )
        self.quest_manager.add_quest(q_explore)

        q_treasure = Quest(
            "Trouver le trésor",
            "Retrouvez le trésor caché dans la lagune ou la cascade.",
            ["prendre tresor", "prendre parchemin"],
            reward="Trésor"
        )
        self.quest_manager.add_quest(q_treasure)

        # Dans setup(), après les autres commandes :
        look = Command("look", " : regarder autour de soi", Actions.look, 0)
        self.commands["look"] = look

        # Après la section "Create exits for rooms", ajoutez :

        # Import Item at the top of the file
        from item import Item

        # Add items to rooms (dans la méthode setup())
        parchemin = Item("parchemin", "Vous apercevez un morceau de parchemin à côté d'un squelette. Vous pouvez y lire \"Celui qui veut survivre devra faire l\'inverse de ce que dit le crocodile.\"", 0)
        beach.inventory["parchemin"] = parchemin

        bananes = Item("bananes", "Vous trouvez des bananes accrochées aux arbres.", 5)
        forest.inventory["bananes"] = bananes

        barils = Item("barils", "Vous avez retrouvé les barils de vin.", 10)
        cliff.inventory["barils"] = barils

        tresor = Item("tresor", "Vous avez retouvé le trésor.", 10)
        waterfall.inventory["tresor"] = tresor

        take = Command("take", " <item> : prendre un objet", Actions.take, 1)
        self.commands["take"] = take

        drop = Command("drop", " <item> : déposer un objet", Actions.drop, 1)
        self.commands["drop"] = drop

        check = Command("check", " : vérifier l'inventaire", Actions.check, 0)
        self.commands["check"] = check

        charge = Command("charge", " : charger le beamer", Actions.charge, 0)
        self.commands["charge"] = charge
        fire = Command("fire", " : utiliser le beamer", Actions.fire, 0)
        self.commands["fire"] = fire

        # Créer et ajouter le beamer dans une pièce
        beamer = Item("beamer", "un appareil de téléportation mystérieux", 0.5)
        beamer.is_beamer = True  # Marquer cet objet comme un beamer
        lagoon.inventory["beamer"] = beamer
        

        # Après la section "Create exits for rooms"
        for room in self.rooms:
            self.valid_directions.update([d for d in room.exits.keys() if room.exits[d] is not None])

        from character import Character

        # Créer des personnages
        perroquet = Character(
            "Jacob",
            "un perroquet coloré perché sur une branche",
            beach,
            ["Arrr! Bienvenue sur mon île ! Je suis Jacob !", "Cherchez le trésor sous la cascade !", "Méfiez-vous des singes !"]
        )

        crocodile = Character(
            "Crocodile",
            "il y a un bruit étrange dans la lagune...",
            lagoon,
            ["Bonjour pirates...", "La nature recèle bien des secrets.", "Il faut absolument que vous vous dirigiez vers la forêt tropicale"]
        )

        singe = Character(
            "Singes",
            "un groupe de singes malicieux",
            cliff,
            ["Cette falaise est magnifique, n'est-ce pas ?", "Elle serait encore plus belle si vous en tombiez !", "MOUHAHAHA !"]
        )  

        # Ajouter les personnages aux pièces
        beach.characters["Jacob"] = perroquet
        lagoon.characters["Crocodile"] = crocodile
        cliff.characters["Singes"] = singe

        # Dans setup(), avec les autres commandes
        talk = Command("talk", " <nom> : parler avec un personnage", Actions.talk, 1)
        self.commands["talk"] = talk
        # Commande debug pour basculer le mode debug à l'exécution
        debug_cmd = Command("debug", " : basculer le mode debug (affiche les messages DEBUG)", Actions.debug, 0)
        self.commands["debug"] = debug_cmd
        # Commandes liées aux quêtes
        quests_cmd = Command("quests", " : lister les quêtes disponibles", Actions.show_quests, 0)
        self.commands["quests"] = quests_cmd
        quest_cmd = Command("quest", " <titre> : afficher les détails d'une quête", Actions.show_quest, 1)
        self.commands["quest"] = quest_cmd

    #playthegamego
    def play(self):
        self.setup()
        self.print_welcome()
    
        # Collecter tous les personnages du jeu
        all_characters = []
        for room in self.rooms:
            all_characters.extend(room.characters.values())
    
        # Loop until the game is finished
        while not self.finished:
            # Get the command from the player
            self.process_command(input("> "))
        
            ## Déplacer tous les personnages après chaque commande
            #for character in all_characters:
            #    character.move()
    
        return None

    # Process the command entered by the player
    def process_command(self, command_string) -> None:

        # Supprimer les espaces
        command_string = command_string.strip()

        # Si la commande est vide, ne rien faire
        if command_string == "":
            return
        
        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

        command_word = list_of_words[0]

        # If the command is not recognized, print an error message
        if command_word not in self.commands.keys():
            print(f"\nCommande '{command_word}' non reconnue. Entrez 'help' pour voir la liste des commandes disponibles.\n")

        # If the command is recognized, execute it
        elif command_word == "go":
            if len(list_of_words) < 2:
                print("\nVous devez préciser une direction !\n")
                return
        
            direction = list_of_words[1]
        
            # Normaliser la direction
            direction_map = {
                "N": "N", "NORD": "N", "nord": "N", "n": "N",
                "S": "S", "SUD": "S", "sud": "S", "s": "S",
                "E": "E", "EST": "E", "est": "E", "e": "E",
                "O": "O", "OUEST": "O", "ouest": "O", "o": "O",
                "U": "U", "UP": "U", "up": "U", "u": "U",
                "D": "D", "DOWN": "D", "down": "D", "d": "D"
            }
        
            normalized_direction = direction_map.get(direction)
        
            # Vérifier si la direction est valide dans le jeu
            if normalized_direction not in self.valid_directions:
                print(f"\nLa direction '{direction}' n'existe pas dans ce jeu !")
                print(f"Directions valides : {', '.join(sorted(self.valid_directions))}\n")
                return
        
            # Effectuer le déplacement
            moved = self.player.move(normalized_direction)
            # Vérifier les objectifs liés aux salles
            try:
                if moved and hasattr(self, 'quest_manager'):
                    self.quest_manager.check_room_objectives(self.player.current_room.name)
                    # Activation automatique: lancer la quête "Trouver le trésor" en entrant à Lagoon
                    if self.player.current_room.name == "Lagoon":
                        # Tenter d'activer la quête si elle existe et n'est pas encore active
                        try:
                            self.quest_manager.activate_quest("Trouver le trésor")
                        except Exception:
                            pass
            except Exception:
                pass
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)
    # Print the welcome message
    def print_welcome(self):
        print(f"\nBienvenue {self.player.name} dans ce jeu d'aventure !")
        print("Entrez 'help' si vous avez besoin d'aide.")
        #
        print(self.player.current_room.get_long_description())   

def main():
    # Create a game object and play the game
    Game().play()
    

if __name__ == "__main__":
    main()
