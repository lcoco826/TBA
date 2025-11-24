# Description: Game class

# Import modules

from room import Room
from player import Player
from command import Command
from actions import Actions

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

        beach.exits = {"N" : forest, "E" : None, "S" : None, "O" : cove}
        cove.exits = {"N" : lagoon, "E" : beach, "S" : None, "O" : None}
        forest.exits = {"N" : None, "E" : None, "S" : beach, "O" : lagoon}
        lagoon.exits = {"N" : cliff, "E" : forest, "S" : cove, "O" : None}
        cliff.exits = {"U" : cave, "E" : volcano, "D" : lagoon, "O" : None}
        volcano.exits = {"N" : waterfall, "E" : None, "S" : None, "O" : cliff}
        cave.exits = {"N" : None, "E" : waterfall, "S" : cliff, "O" : None}
        waterfall.exits = {"N" : None, "E" : None, "S" : volcano, "O" : cliff}

        for room in self.rooms :
            self.valid_directions.update([d for d in room.exits.keys() if room.exits[d] is not None])

        # Setup player and starting room

        self.player = Player(input("\nEntrez votre nom: "))
        self.player.current_room = beach

    # Play the gamego
    def play(self):
        self.setup()
        self.print_welcome()
        # Loop until the game is finished
        while not self.finished:
            # Get the command from the player
            self.process_command(input("> "))
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
        if command_word == "go":
            if len(list_of_words) < 2:
                print("Vous devez préciser une direction !")
                return
            direction = list_of_words[1]  # <- Le vrai paramètre
            self.player.move(direction)

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
