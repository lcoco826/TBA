#!/usr/bin/env python3
"""
Module Game - Moteur principal du jeu d'aventure TBA.

Ce module gère:
- L'initialisation et la boucle de jeu
- Le chargement des salles et des commandes
- Le traitement des entrées utilisateur
- L'interface en ligne de commande ou graphique (Tkinter)

Utilisation:
    Mode CLI: python game.py --cli
    Mode GUI (défaut): python game.py
    Mode DEBUG: python game.py --debug

Variables globales:
    DEBUG: Booléen pour activer les messages de débogage
    DEBUG_LOG: Buffer pour stocker les messages de débogage
"""

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

# DEBUG peut être activé de trois façons (ordre de priorité):
# 1) Flag en ligne de commande `--debug`
# 2) Variable d'environnement `GAME_DEBUG=1` ou `GAME_DEBUG=true`
# 3) Valeur par défaut False
def _detect_debug():
    """
    Détecte si le mode DEBUG est activé.
    
    Ordre de priorité:
    1. Flag --debug en ligne de commande
    2. Variable d'environnement GAME_DEBUG
    3. Valeur par défaut (False)
    
    Returns:
        bool: True si le mode DEBUG est activé
    """
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
    """
    Classe principale du jeu d'aventure.
    
    Gère:
    - L'état du jeu (salles, joueur, commandes)
    - La boucle de jeu
    - Le traitement des commandes
    - L'interface utilisateur
    
    Attributs:
        finished (bool): Si le jeu est terminé
        rooms (list): Liste des salles du jeu
        commands (dict): Dictionnaire des commandes disponibles
        player (Player): L'instance du joueur
        player_name (str): Nom optionnel du joueur
        valid_directions (set): Ensemble des directions valides utilisées
        quest_manager (QuestManager): Gestionnaire des quêtes
    """

    def __init__(self, player_name=None):
        """
        Initialiser une nouvelle instance de jeu.
        
        Args:
            player_name (str, optional): Nom du joueur. Si None, sera demandé
                                        lors de setup() en mode CLI
        """
        self.finished = False
        self.rooms = []
        self.commands = {}
        self.player = None
        self.player_name = player_name  # Nom optionnel du joueur
        self.valid_directions = set()
        self.victory = False
        
    def setup(self):
        """
        Initialiser et configurer le jeu.
        
        Cette méthode:
        - Crée toutes les salles et leurs connexions
        - Ajoute les items et personnages
        - Enregistre les commandes disponibles
        - Crée le joueur
        - Initialise le gestionnaire de quêtes
        
        Note: Ne doit être appelée qu'une seule fois au démarrage du jeu
        """

        # Setup commands

        help = Command("help", " : afficher cette aide", Actions.help, 0)
        self.commands["help"] = help
        quit = Command("quit", " : quitter le jeu", Actions.quit, 0)
        self.commands["quit"] = quit
        # Alias/commande supplémentaire pour arrêter le jeu si souhaité
        if "stop" not in self.commands:
            stop = Command("stop", " : arrêter le jeu", Actions.quit, 0)
            self.commands["stop"] = stop
        go = Command("go", " <direction> : se déplacer dans une direction cardinale (N, E, S, O, U, D)", Actions.go, 1)
        self.commands["go"] = go
        look = Command("look", " : regarder autour de soi", Actions.look, 0)
        self.commands["look"] = look
        back = Command("back", " : revenir à la salle précédente", Actions.back, 0)
        self.commands["back"] = back

        # Setup rooms
        beach = Room("Beach", "une plage de sable blanc bordée de palmiers, avec des eaux cristallines.")
        self.rooms.append(beach)
        cove = Room("Cove", "une crique isolée, le calme y règne, cela paraît presque étrange...")
        self.rooms.append(cove)
        forest = Room("Forêt", "une forêt tropicale, dense et humide, attention aux plantes carnivores ! ")
        self.rooms.append(forest)
        lagoon = Room("Lagoon", "une lagune dont les eaux turquoises reflètent le ciel et les palmiers.")
        self.rooms.append(lagoon)
        cliff = Room("Cliff", "une falaise, elle se détache sur l'horizon comme un mur de pierre.")
        self.rooms.append(cliff)
        volcano = Room("Volcano", "un volcan majestueux qui domine l'île, ses flancs noirs et rugueux témoignent des anciennes coulées de lave.")
        self.rooms.append(volcano)
        cave = Room("Cave", "une grotte mystérieuse et sombre qui se cache sous une montagne.")
        self.rooms.append(cave)
        waterfall = Room("Waterfall", "une cascade qui dévale la falaise avec fracas, projetant des éclats d'eau créant un nuage de brume.")
        self.rooms.append(waterfall)

        # Create exits for rooms

        beach.exits = {"N" : None, "E" : None, "S" : None, "O" : cove, "U" : None, "D": None}
        cove.exits = {"N" : lagoon, "E" : beach, "S" : None, "O" : None, "U" : None, "D": None}
        forest.exits = {"N" : None, "E" : None, "S" : None, "O" : None, "U" : None, "D": None}
        lagoon.exits = {"N" : cave, "E" : forest, "S" : cove, "O" : None, "U" : None, "D": None}
        cave.exits = {"N": None, "E" : volcano, "S" : lagoon, "O" : None, "U" : cliff, "D": None}
        cliff.exits = {"N": None, "E" : None, "S": None, "O" : None, "U" : None, "D" : cave}
        volcano.exits = {"N": None, "E" : None, "S": None, "O" : cave, "U" : waterfall, "D" : None}
        waterfall.exits = {"N" : None, "E" : None, "S" : None, "O" : cliff, "U": None, "D": None}

        for room in self.rooms :
            self.valid_directions.update([d for d in room.exits.keys() if room.exits[d] is not None])

        # Setup player and starting room

        # Use provided name or ask interactively if not provided
        if self.player_name:
            player_name = self.player_name
        else:
            player_name = input("\nEntrez votre nom: ")
        
        self.player = Player(player_name)
        self.player.current_room = beach
        self.player.starting_room = beach

        # Initialise le gestionnaire de quêtes pour ce joueur
        self.quest_manager = QuestManager(self.player)

        #quêtes 
        q_explore = Quest(
            "Vivre un rêve",
            "Visitez les plus beaux lieux de l'île.",
            [f"Visiter {r.name}" for r in (beach, cove, waterfall, lagoon)],
            reward="Sac à dos moyen (+5kg)"
        )
        self.quest_manager.add_quest(q_explore)

        q_treasure = Quest(
            "Chasse aux trésors",
            "Retrouvez le trésor caché et les barils perdus.",
            ["prendre trésor", "prendre barils"],
            reward="Trésor, Vin et Beamer"
        )
        self.quest_manager.add_quest(q_treasure)

        # Quête pour explorer les lieux dangereux (Grotte et Volcan)
        q_danger = Quest(
            "Explorer les lieux dangereux",
            "Explorez la grotte mystérieuse et le volcan majestueux.",
            [f"Visiter {cave.name}", f"Visiter {volcano.name}"],
            reward="Équipement d'explorateur"
        )
        self.quest_manager.add_quest(q_danger)
        
        q_trade = Quest(
            "Marchander",
            "Discutez avec les singes, récupérez les bananes et donnez-leur.",
            ["parler avec Singes", "prendre bananes", "donner bananes"],
            reward="Grand sac à dos (+10kg)"
        )
        self.quest_manager.add_quest(q_trade)
        
        # Activation des quêtes principales
        self.quest_manager.activate_quest("Vivre un rêve")
        # self.quest_manager.activate_quest("Chasse aux trésors") # Sera activée par le parchemin
        
        # Configuration de l'activation automatique des quêtes secondaires
        self.auto_activate_map = {
            "Cave": "Explorer les lieux dangereux",
            "Volcano": "Marchander"
        }

        # Dans setup(), après les autres commandes :
        look = Command("look", " : regarder autour de soi", Actions.look, 0)
        self.commands["look"] = look

        # Après la section "Create exits for rooms", ajoutez :

        # Import Item at the top of the file
        from item import Item

        # Add items to rooms (dans la méthode setup())
        parchemin = Item("parchemin", "Vous apercevez un morceau de parchemin à côté d'un squelette. Vous pouvez y lire \"Le trésor se trouve à l'extrémité de l'île.\"", 0)
        beach.inventory["parchemin"] = parchemin

        bananes = Item("bananes", "Vous trouvez des bananes accrochées aux arbres.", 5)
        waterfall.inventory["bananes"] = bananes

        barils = Item("barils", "Vous avez retrouvé les barils de vin.", 10)
        waterfall.inventory["barils"] = barils

        tresor = Item("trésor", "Vous avez retrouvé le trésor.", 10)
        cliff.inventory["trésor"] = tresor

        # Wrapper pour la commande take afin d'activer la quête via le parchemin
        def take_wrapper(game, list_of_words, number_of_parameters):
            result = Actions.take(game, list_of_words, number_of_parameters)
            if result and len(list_of_words) > 1:
                item_name = list_of_words[1].strip().lower()
                if item_name in ["parchemin", "trésor", "barils"]:
                    if game.quest_manager.activate_quest("Chasse aux trésors"):
                        # Si la quête vient d'être activée, on valide l'objectif rétroactivement pour l'objet pris
                        for key in game.player.inventory:
                            if key.lower() == item_name:
                                game.quest_manager.check_action_objectives("prendre", key)
                                break
            return result

        take = Command("take", " <item> : prendre un objet", take_wrapper, 1)
        self.commands["take"] = take

        drop = Command("drop", " <item> : déposer un objet", Actions.drop, 1)
        self.commands["drop"] = drop

        check = Command("check", " : vérifier l'inventaire", Actions.check, 0)
        self.commands["check"] = check

        fire = Command("fire", " : utiliser le beamer", Actions.fire, 0)
        self.commands["fire"] = fire

        oui = Command("oui", " : répondre oui", Actions.yes, 0)
        self.commands["oui"] = oui
        non = Command("non", " : répondre non", Actions.no, 0)
        self.commands["non"] = non
        

        # Après la section "Create exits for rooms"
        for room in self.rooms:
            self.valid_directions.update([d for d in room.exits.keys() if room.exits[d] is not None])

        from character import Character

        # Créer des personnages
        perroquet = Character(
            "Jacob",
            "un perroquet coloré perché sur une branche près de vous.",
            beach,
            ["Arrr ! Bienvenue sur mon île ! Je suis Jacob ! Les singes vous ont volé mais ils ne représetent pas le réel danger de cette île, vous devez vous méfier du crocodile !!"]
        )

        crocodile = Character(
            "Crocodile",
            "un crocodile géant émerge de l'eau de la lagune.",
            lagoon,
            ["Bonjour pirates... La nature recèle bien des secrets, allez vers l'Est avant que je ne vous dévore MOUAHAHAH !"]
        )

        singe = Character(
            "Singes",
            "un groupe de singes malicieux qui semblent affamés.",
            volcano,
            ["Des bananes ! Des Bananes !"]
        )  

        # Ajouter les personnages aux pièces
        beach.characters["Jacob"] = perroquet
        lagoon.characters["Crocodile"] = crocodile
        volcano.characters["Singes"] = singe

        # Dans setup(), avec les autres commandes
        talk = Command("talk", " <nom> : parler avec un personnage", Actions.talk, 1)
        self.commands["talk"] = talk
        give = Command("give", " <item> : donner un objet à un personnage", Actions.give, 1)
        self.commands["give"] = give
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
        
        # Vérifier les objectifs de la salle de départ (pour valider "Visiter Beach" immédiatement)
        self.quest_manager.check_room_objectives(self.player.current_room.name)

    def play(self):
        """
        Lancer la boucle principale du jeu (mode CLI).
        
        Cette méthode:
        1. Initialise le jeu via setup()
        2. Affiche le message de bienvenue
        3. Entre dans la boucle de jeu
        4. Continue jusqu'à ce que le jeu soit terminé
        
        Returns:
            None: Le jeu se termine quand finished est True
        """
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
        
        return None

    def process_command(self, command_string) -> None:
        """
        Traiter une commande saisie par le joueur.
        
        Processus:
        1. Valide et nettoie la saisie
        2. Extrait la commande et les paramètres
        3. Cherche la commande dans le dictionnaire
        4. Exécute l'action correspondante
        5. Vérifie les conditions de défaite
        
        Args:
            command_string (str): La chaîne saisie par l'utilisateur
            
        Affiche des messages d'erreur si:
        - La commande n'existe pas
        - Les paramètres sont incorrects
        - L'action échoue
        """

        # Supprimer les espaces
        command_string = command_string.strip()

        # Si la commande est vide, ne rien faire
        if command_string == "":
            return
        
        # Split the command string into a list of words
        list_of_words = command_string.split(" ")

        command_word = list_of_words[0].lower()

        # If the command is not recognized, print an error message
        if command_word not in self.commands.keys():
            print(f"\n❌ Commande '{command_word}' non reconnue.")
            print(f"   Utilisez 'help' pour voir la liste des commandes disponibles.\n")

        # If the command is recognized, execute it
        elif command_word == "go":
            if len(list_of_words) < 2:
                print("\n❌ Erreur: Vous devez préciser une direction !")
                print("   Utilisation: go <direction>\n")
                return
        
            direction = list_of_words[1].upper()
        
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
                print(f"\n❌ Direction '{direction}' invalide dans ce jeu.")
                print(f"   Directions valides : {', '.join(sorted(self.valid_directions))}\n")
                return
        
            # Effectuer le déplacement
            moved = self.player.move(normalized_direction)
            # Vérifier condition de perte : entrer dans la forêt -> plantes carnivores
            try:
                if moved and getattr(self.player.current_room, 'name', '').strip() == "Forêt":
                    # Texte de défaite plus évocateur
                    print("\n☠️ Vous pénétrez plus profondément dans la Forêt.")
                    print("    Des lianes visqueuses surgissent, des fleurs s'ouvrent en un claquement de crocs...")
                    print("    Vous êtes violemment dévoré par les plantes carnivores.")
                    print("    FIN.\n")
                    self.finished = True
                    return
            except Exception:
                pass
            # Vérifier les objectifs liés aux salles
            try:
                if moved and hasattr(self, 'quest_manager'):
                    # 1. D'abord vérifier si une quête doit s'activer ici
                    try:
                        if hasattr(self, 'auto_activate_map'):
                            quest_to_activate = self.auto_activate_map.get(self.player.current_room.name)
                            if quest_to_activate:
                                self.quest_manager.activate_quest(quest_to_activate)
                    except Exception:
                        pass
                    # 2. Ensuite vérifier les objectifs (maintenant que la quête est active)
                    self.quest_manager.check_room_objectives(self.player.current_room.name)
            except Exception:
                pass
        else:
            command = self.commands[command_word]
            command.action(self, list_of_words, command.number_of_parameters)
    def print_welcome(self):
        """
        Afficher le message de bienvenue et la description initiale.
        
        Affiche:
        - Un message de bienvenue personnalisé
        - Un rappel pour utiliser 'help'
        - La description de la salle de départ
        """
        print(f"\n{'='*50}")
        print(f"🎮 Bienvenue {self.player.name} dans ce jeu d'aventure !")
        print(f"{'='*50}")
        print("💡 Entrez 'help' si vous avez besoin d'aide sur les commandes.")
        print(f"{'='*50}\n")
        print("Capitaine, votre bateau a fait naufrage, fort heureusement, votre équipage a survécu. Cependant, toutes vos ressources ont été volées par des singes. Il vous faura explorer cette île pour retrouver vos ressources et découvrir des trésors !")
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
        # Ask for player name before opening GUI
        player_name = input("Entrez votre nom : ").strip()
        if not player_name:
            player_name = "Aventurier"
        # Create game and GUI with player name
        game = Game(player_name=player_name)

        app = None
        class GameGUI(tk.Tk):
            IMAGE_WIDTH = 700
            IMAGE_HEIGHT = 450

            def __init__(self, game_instance):
                super().__init__()
                self.game = game_instance
                self.title("TBA - Jeu d'aventure")
                self.protocol("WM_DELETE_WINDOW", self._on_close)
                self._game_over_shown = False
                
                # Sauvegarde de la sortie standard actuelle (le terminal)
                self.old_stdout = sys.stdout
                
                # Configure style
                self.style = ttk.Style()
                self.style.theme_use('clam')
                # Layout
                self._build_layout()
                
                # Redirection de tous les print() vers l'interface graphique
                sys.stdout = self

                # Initialisation du jeu (après redirection pour éviter les erreurs d'encodage console)
                self.game.setup()

                # Print welcome in text output
                self._print_welcome()

            def write(self, text):
                """Méthode appelée par print() pour écrire du texte."""
                self.text_output.configure(state="normal")
                self.text_output.insert("end", text)
                self.text_output.see("end")
                self.text_output.configure(state="disabled")
                self.update_idletasks() # Met à jour l'affichage immédiatement

            def flush(self):
                """Méthode requise pour la compatibilité avec sys.stdout."""
                pass

            def _build_layout(self):
                # Configure root grid - 2 columns, 2 rows (plus entry row at bottom)
                self.grid_rowconfigure(0, weight=1)  # Image / Deplacements
                self.grid_rowconfigure(1, weight=1)  # Console / Commands
                self.grid_rowconfigure(2, weight=0)  # Entry bar
                self.grid_columnconfigure(0, weight=1)  # Left column (image + console)
                self.grid_columnconfigure(1, weight=0)  # Right column (buttons)

                # TOP LEFT: Image area
                image_frame = ttk.Frame(self)
                image_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
                image_frame.grid_propagate(False)
                image_frame.config(width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT)
                self.canvas = tk.Canvas(image_frame, width=self.IMAGE_WIDTH, height=self.IMAGE_HEIGHT, bg="#1a1a2e", highlightthickness=0)
                self.canvas.pack(fill="both", expand=True)

                # TOP RIGHT: Movement buttons
                move_frame = ttk.LabelFrame(self, text="Déplacements", padding=10)
                move_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
                move_frame.grid_columnconfigure(0, weight=1)
                move_frame.grid_columnconfigure(1, weight=1)
                move_frame.grid_rowconfigure(0, weight=1)
                move_frame.grid_rowconfigure(1, weight=1)
                move_frame.grid_rowconfigure(2, weight=1)
                move_frame.grid_rowconfigure(3, weight=1)
                
                btn_style = {'font': ('Arial', 10, 'bold'), 'height': 3, 'width': 4, 'bg': '#2196F3', 'fg': 'white', 'activebackground': '#0b7dda'}
                tk.Button(move_frame, text="N", command=lambda: self._send_command("go N"), **btn_style).grid(row=0, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
                tk.Button(move_frame, text="O", command=lambda: self._send_command("go O"), **btn_style).grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
                tk.Button(move_frame, text="E", command=lambda: self._send_command("go E"), **btn_style).grid(row=1, column=1, sticky="nsew", padx=1, pady=1)
                tk.Button(move_frame, text="S", command=lambda: self._send_command("go S"), **btn_style).grid(row=2, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
                tk.Button(move_frame, text="U", command=lambda: self._send_command("go U"), **btn_style).grid(row=3, column=0, sticky="nsew", padx=1, pady=1)
                tk.Button(move_frame, text="D", command=lambda: self._send_command("go D"), **btn_style).grid(row=3, column=1, sticky="nsew", padx=1, pady=1)

                # BOTTOM LEFT: Terminal output area
                output_frame = ttk.Frame(self)
                output_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
                output_frame.grid_rowconfigure(0, weight=1)
                output_frame.grid_columnconfigure(0, weight=1)
                scrollbar = ttk.Scrollbar(output_frame, orient="vertical")
                self.text_output = tk.Text(output_frame, wrap="word", yscrollcommand=scrollbar.set, state="disabled", bg="#111", fg="#eee", font=('Arial', 10))
                scrollbar.config(command=self.text_output.yview)
                self.text_output.grid(row=0, column=0, sticky="nsew")
                scrollbar.grid(row=0, column=1, sticky="ns")

                # BOTTOM RIGHT: Command buttons
                cmds_frame = ttk.LabelFrame(self, text="Actions rapides", padding=10)
                cmds_frame.grid(row=1, column=1, sticky="nsew", padx=6, pady=(0,6))
                cmds_frame.grid_columnconfigure(0, weight=1)
                cmds_frame.grid_rowconfigure(0, weight=1)
                
                # Create scrollable frame for commands with 2 columns
                canvas_cmds = tk.Canvas(cmds_frame, bg="#f0f0f0", highlightthickness=0)
                scrollable_frame = ttk.Frame(canvas_cmds)
                win_id = canvas_cmds.create_window((0, 0), window=scrollable_frame, anchor="nw")

                def _update_dims(event):
                    c_w = event.width if event.widget == canvas_cmds else canvas_cmds.winfo_width()
                    c_h = event.height if event.widget == canvas_cmds else canvas_cmds.winfo_height()
                    f_req_h = scrollable_frame.winfo_reqheight()
                    canvas_cmds.itemconfig(win_id, width=c_w, height=max(c_h, f_req_h))
                    canvas_cmds.configure(scrollregion=canvas_cmds.bbox("all"))

                scrollable_frame.bind("<Configure>", _update_dims)
                canvas_cmds.bind("<Configure>", _update_dims)
                
                quick_cmds = [
                    ("help", "Aide"), ("look", "Regarder"), ("take ", "Prendre"), ("drop ", "Déposer"),
                    ("check", "Inventaire"), ("back", "Retour"), ("talk ", "Parler"), ("quests", "Quêtes"), ("quest ", "Détails quête"), ("rewards", "Récompenses"),
                    ("fire", "Utiliser beamer"), ("debug", "DEBUG")
                ]
                
                action_btn_style = {'font': ('Arial', 9, 'bold'), 'height': 3, 'bg': '#4CAF50', 'fg': 'white', 'activebackground': '#45a049'}
                
                # Create grid for buttons (3 columns)
                scrollable_frame.grid_columnconfigure(0, weight=1)
                scrollable_frame.grid_columnconfigure(1, weight=1)
                scrollable_frame.grid_columnconfigure(2, weight=1)
                
                for idx, (cmd, label) in enumerate(quick_cmds):
                    def make_cmd(c):
                        if c.endswith(" "):
                            return lambda: self._fill_entry(c)
                        return lambda: self._send_command(c.strip())
                    row = idx // 3
                    col = idx % 3
                    scrollable_frame.grid_rowconfigure(row, weight=1)
                    tk.Button(scrollable_frame, text=label, command=make_cmd(cmd), **action_btn_style).grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                
                canvas_cmds.grid(row=0, column=0, sticky="nsew")

                # BOTTOM: Entry area (spans both columns)
                entry_frame = ttk.Frame(self)
                entry_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(3,6))
                entry_frame.grid_columnconfigure(0, weight=1)
                self.entry_var = tk.StringVar()
                self.entry = ttk.Entry(entry_frame, textvariable=self.entry_var)
                self.entry.grid(row=0, column=0, sticky="ew")
                self.entry.bind("<Return>", self._on_enter)
                self.entry.focus_set()

            def _print_welcome(self):
                self._write_output(f"\n🎮 Bienvenue {self.game.player.name} dans ce jeu d'aventure !\n")
                self._write_output("💡 Entrez 'help' si vous avez besoin d'aide.\n")
                self._write_output("Capitaine, votre bateau a fait naufrage, fort heureusement, votre équipage a survécu. Cependant, toutes vos ressources ont été volées par des singes.\nIl vous faura explorer cette île pour retrouver vos ressources et découvrir des trésors !")
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

            def _fill_entry(self, text):
                self.entry.delete(0, "end")
                self.entry.insert(0, text)
                self.entry.focus_set()
                self.entry.icursor("end")

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
                    # Show a final animation or image instead of immediate close
                    self.after(200, self._show_game_over)

            def _update_room_image(self):
                # Update the canvas based on current room. If room.image exists and file exists, try to load it.
                room = self.game.player.current_room
                assets_dir = Path(__file__).parent / 'assets'
                self.canvas.delete("all")
                image_path = None
                
                # 1. Vérifier si une image est explicitement définie
                if getattr(room, 'image', None):
                    p = assets_dir / room.image
                    if p.exists():
                        image_path = str(p)
                
                # 2. Sinon, chercher une image portant le nom de la salle (ex: Beach.png)
                if not image_path:
                    for ext in [".png", ".gif"]:
                        p = assets_dir / f"{room.name}{ext}"
                        if p.exists():
                            image_path = str(p)
                            break

                if image_path:
                    try:
                        img = tk.PhotoImage(file=image_path)
                        
                        # Redimensionner l'image si elle est trop grande (méthode native sans PIL)
                        w, h = img.width(), img.height()
                        factor = int(max(w / self.IMAGE_WIDTH, h / self.IMAGE_HEIGHT))
                        
                        if factor > 1:
                            img = img.subsample(factor)
                            
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

            def _show_game_over(self):
                """Display final image or simple animation when the game ends."""
                if getattr(self, '_game_over_shown', False):
                    return
                self._game_over_shown = True
                # Try to load an explicit gameover image from assets
                assets_dir = Path(__file__).parent / 'assets'
                # Accept PNG or PPM placeholders
                gameover_path_png = assets_dir / 'gameover.png'
                gameover_path_ppm = assets_dir / 'gameover.ppm'
                self.canvas.delete("all")
                chosen = None
                if gameover_path_png.exists():
                    chosen = gameover_path_png
                elif gameover_path_ppm.exists():
                    chosen = gameover_path_ppm
                if chosen is not None:
                    try:
                        img = tk.PhotoImage(file=str(chosen))
                        self._image_ref = img
                        self.canvas.create_image(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2, image=self._image_ref)
                        return
                    except Exception:
                        chosen = None
                if chosen is None:
                    # Simple flashing red animation with final text
                    steps = 6
                    def flash(step=0):
                        if getattr(self.game, 'victory', False):
                            color = "#2E7D32" if step % 2 == 0 else "#1B5E20" # Vert pour la victoire
                            text_main = "VOUS AVEZ GAGNÉ !"
                        else:
                            color = "#600" if step % 2 == 0 else "#300" # Rouge pour la défaite
                            text_main = "VOUS AVEZ ÉTÉ DÉVORÉ"

                        self.canvas.delete("all")
                        self.canvas.create_rectangle(0, 0, self.IMAGE_WIDTH, self.IMAGE_HEIGHT, fill=color)
                        self.canvas.create_text(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2 - 10, text=text_main, fill="white", font=("Helvetica", 16, "bold"))
                        self.canvas.create_text(self.IMAGE_WIDTH/2, self.IMAGE_HEIGHT/2 + 30, text="FIN", fill="white", font=("Helvetica", 14))
                        if step < steps:
                            self.after(300, lambda: flash(step+1))
                        else:
                            # keep final frame and write to output console
                            self._write_output(f"\n--- {text_main}. PARTIE TERMINÉE ---\n")
                    flash()

            def _on_close(self):
                sys.stdout = self.old_stdout # Restaure la sortie vers le terminal
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
