# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions
from quest import Quest, QuestManager
import os
import sys
try:
    import tkinter as tk
    from tkinter import ttk
    from pathlib import Path
except Exception:
    tk = None
    ttk = None
    from pathlib import Path

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
        beach = Room("Beach", "une plage de sable blanc. Capitaine, votre équipage a survécu cependant des singes ont volé toutes vos ressources, c'est à vous de découvrir cette île, retrouver vos ressources et trouver un moyen de partir !.")
        self.rooms.append(beach)
        cove = Room("Cove", "une crique isolée, un squelette murmure : .")
        self.rooms.append(cove)
        forest = Room("Forêt", "une forêt tropicale, dense et humide.")
        self.rooms.append(forest)
        lagoon = Room("Lagoon", "une lagune s'étire paisiblement, ses eaux turquoises reflétant le ciel.")
        self.rooms.append(lagoon)
        cliff = Room("Cliff", "une falaise, elle se détache sur l'horizon, comme un mur de pierre.")
        self.rooms.append(cliff)
        volcano = Room("Volcano", "un volcan, majestueux domine l'île, ses flancs noirs et rugueux témoignent des anciennes coulées de lave.")
        self.rooms.append(volcano)
        cave = Room("Cave", "une grotte mystérieuse et sombre se cache derrière la cascade.")
        self.rooms.append(cave)
        waterfall = Room("Waterfall", "une cascade qui dévale la falaise avec fracas, projetant des éclats d'eau créant un nuage de brume.")
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

        #quêtes 
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

        # Quête pour récupérer les barils (exemple) et activation automatique en entrant sur la falaise
        q_barils = Quest(
            "Récupérer les barils",
            "Récupérez les barils perdus sur la falaise.",
            ["prendre barils"],
            reward="Barils de vin"
        )
        self.quest_manager.add_quest(q_barils)

        # Quête pour explorer la grotte
        q_cave = Quest(
            "Explorer la grotte",
            "Découvrez les mystères cachés dans la grotte.",
            [f"Visiter {cave.name}"],
            reward="Lampe torche"
        )
        self.quest_manager.add_quest(q_cave)

        # Quête pour le volcan
        q_volcano = Quest(
            "Survivre au volcan",
            "Approchez et survivez aux dangers du volcan.",
            [f"Visiter {volcano.name}"],
            reward="Cendre rare"
        )
        self.quest_manager.add_quest(q_volcano)

        # NOTE: suppression de l'activation automatique des quêtes.
        # Les quêtes sont ajoutées au gestionnaire mais ne sont pas activées
        # automatiquement. L'utilisateur peut découvrir et activer les
        # quêtes via les commandes `quests` / `quest` / `rewards`.

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
        # Commande pour afficher les récompenses obtenues
        rewards_cmd = Command("rewards", " : afficher les récompenses obtenues", Actions.show_rewards, 0)
        self.commands["rewards"] = rewards_cmd

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
                    # Activation automatique : vérifier la map et activer la quête correspondante
                    try:
                        if hasattr(self, 'auto_activate_map'):
                            quest_to_activate = self.auto_activate_map.get(self.player.current_room.name)
                            if quest_to_activate:
                                activated = self.quest_manager.activate_quest(quest_to_activate)
                                # Afficher un message clair quand l'activation est automatique
                                if activated:
                                    print(f"\n(Automatique) Quête activée : {quest_to_activate}\n")
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
    # If '--cli' is passed, start the classic console version. Otherwise launch the Tkinter GUI.
    args = sys.argv[1:]
    if '--cli' in args:
        Game().play()
        return
    # Try to launch GUI, fallback to CLI if unavailable
    try:
        if tk is None:
            raise ImportError("Tkinter not available")
        # Create game and GUI
        game = Game()
        game.setup()
        app = None
        class GameGUI(tk.Tk):
            IMAGE_WIDTH = 400
            IMAGE_HEIGHT = 250

            def __init__(self, game_instance):
                super().__init__()
                self.game = game_instance
                self.title("TBA - Jeu d'aventure")
                self.protocol("WM_DELETE_WINDOW", self._on_close)
                # Layout
                self._build_layout()
                # Print welcome in text output
                self._print_welcome()

            def _build_layout(self):
                # Configure root grid
                self.grid_rowconfigure(0, weight=0)
                self.grid_rowconfigure(1, weight=1)
                self.grid_rowconfigure(2, weight=0)
                self.grid_columnconfigure(0, weight=1)

                # Top frame: image and buttons
                top_frame = ttk.Frame(self)
                top_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6,3))
                top_frame.grid_columnconfigure(0, weight=0)
                top_frame.grid_columnconfigure(1, weight=1)

                # Image area
                image_frame = ttk.Frame(top_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
                image_frame.grid(row=0, column=0, sticky="nw", padx=(0,6))
                image_frame.grid_propagate(False)
                self.canvas = tk.Canvas(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT, bg="#222")
                self.canvas.pack(fill="both", expand=True)

                # Buttons area
                buttons_frame = ttk.Frame(top_frame)
                buttons_frame.grid(row=0, column=1, sticky="ne")

                # Movement buttons
                move_frame = ttk.LabelFrame(buttons_frame, text="Déplacements")
                move_frame.grid(row=0, column=0, sticky="ew", pady=4)
                tk.Button(move_frame, text="N", command=lambda: self._send_command("go N")).grid(row=0, column=0, columnspan=2)
                tk.Button(move_frame, text="O", command=lambda: self._send_command("go O")).grid(row=1, column=0)
                tk.Button(move_frame, text="E", command=lambda: self._send_command("go E")).grid(row=1, column=1)
                tk.Button(move_frame, text="S", command=lambda: self._send_command("go S")).grid(row=2, column=0, columnspan=2)

                # Command buttons (extra)
                cmds_frame = ttk.LabelFrame(buttons_frame, text="Actions rapides")
                cmds_frame.grid(row=1, column=0, sticky="ew", pady=(6,0))
                row = 0
                quick_cmds = [
                    ("help", "Aide"), ("look", "Regarder"), ("take ", "Prendre"), ("drop ", "Déposer"),
                    ("check", "Inventaire"), ("back", "Retour"), ("talk ", "Parler"), ("quests", "Quêtes"), ("rewards", "Récompenses"),
                    ("charge", "Charger beamer"), ("fire", "Utiliser beamer"), ("debug", "DEBUG")
                ]
                for cmd, label in quick_cmds:
                    # For commands that require a parameter, open the input entry after sending the base command
                    def make_cmd(c):
                        return lambda: self._send_command(c.strip())
                    tk.Button(cmds_frame, text=label, command=make_cmd(cmd)).grid(row=row, column=0, sticky="ew", pady=2)
                    row += 1

                # Terminal output area
                output_frame = ttk.Frame(self)
                output_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=3)
                output_frame.grid_rowconfigure(0, weight=1)
                output_frame.grid_columnconfigure(0, weight=1)
                scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
                self.text_output = tk.Text(output_frame, wrap="word", yscrollcommand=scrollbar.set, state="disabled", bg="#111", fg="#eee")
                scrollbar.config(command=self.text_output.yview)
                self.text_output.grid(row=0, column=0, sticky="nsew")
                scrollbar.grid(row=0, column=1, sticky="ns")

                # Entry area
                entry_frame = ttk.Frame(self)
                entry_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(3,6))
                entry_frame.grid_columnconfigure(0, weight=1)
                self.entry_var = tk.StringVar()
                self.entry = ttk.Entry(entry_frame, textvariable=self.entry_var)
                self.entry.grid(row=0, column=0, sticky="ew")
                self.entry.bind("<Return>", self._on_enter)
                self.entry.focus_set()

            def _print_welcome(self):
                self._write_output(f"\nBienvenue {self.game.player.name} dans ce jeu d'aventure !\n")
                self._write_output("Entrez 'help' si vous avez besoin d'aide.\n")
                self._write_output(self.game.player.current_room.get_long_description())
                self._update_room_image()

            def _write_output(self, text):
                self.text_output.configure(state="normal")
                self.text_output.insert("end", text + "\n")
                self.text_output.see("end")
                self.text_output.configure(state="disabled")

            def _on_enter(self, _event=None):
                value = self.entry_var.get().strip()
                if value:
                    self._send_command(value)
                    self.entry_var.set("")

            def _send_command(self, command):
                if self.game.finished:
                    return
                # Echo the command in output area
                self._write_output(f"> {command}")
                # Process command
                self.game.process_command(command)
                # Update room image and output
                self._update_room_image()
                if self.game.finished:
                    self.entry.configure(state="disabled")
                    self.after(600, self._on_close)

            def _update_room_image(self):
                # Update the canvas based on current room. If room.image exists and file exists, try to load it.
                room = self.game.player.current_room
                assets_dir = Path(__file__).parent / 'assets'
                self.canvas.delete("all")
                image_path = None
                if getattr(room, 'image', None):
                    p = assets_dir / room.image
                    if p.exists():
                        image_path = str(p)
                if image_path:
                    try:
                        img = tk.PhotoImage(file=image_path)
                        # Keep reference
                        self._image_ref = img
                        self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, image=self._image_ref)
                        return
                    except Exception:
                        # fallthrough to drawn representation
                        pass
                # Draw a simple representation
                self.canvas.create_rectangle(0, 0, self.IMAGE_WIDTH, self.IMAGE_HEIGHT, fill="#334")
                self.canvas.create_text(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, text=room.name, fill="white", font=("Helvetica", 20))

            def _on_close(self):
                try:
                    self.destroy()
                except Exception:
                    pass

        app = GameGUI(game)
        app.mainloop()
    except Exception as e:
        print(f"GUI indisponible ({e}). Passage en mode console.")
        Game().play()
    

if __name__ == "__main__":
    main()
