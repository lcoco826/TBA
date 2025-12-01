# Define the Player class.
class Player:

    def __init__(self, name):
        self.name = name
        self.current_room = None
        self.history = []  # Historique des salles visitées
        self.inventory = {}
        self.max_weight = 10

    def move(self, direction):
        # La direction est déjà normalisée, pas besoin de la re-normaliser
    
        # Vérifier si la sortie existe
        next_room = self.current_room.exits.get(direction)
        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            print(self.current_room.get_long_description())
            return False

        # Ajouter la salle actuelle à l'historique
        self.history.append(self.current_room)

        # Déplacer le joueur
        self.current_room = next_room
        print(self.current_room.get_long_description())
        print(self.get_history())
        return True

    def back(self):
        """Revenir à la salle précédente si possible."""
        if not self.history:
            print("\nImpossible de revenir en arrière !\n")
            return False

        # Revenir à la dernière salle visitée
        self.current_room = self.history.pop()
        print(self.current_room.get_long_description())
        print(self.get_history())
        return True

    def get_history(self):
        """Retourne une chaîne représentant l'historique des salles visitées."""
        if not self.history:
            return ""
        lines = ["Vous avez déjà visité les pièces suivantes:"]
        for room in self.history:
            lines.append(f"    - {room.description}")
        return "\n".join(lines)

    # Get the inventory
    def get_inventory(self):
        # Si l'inventaire est vide
        if not self.inventory:
            return "Il n'y a rien ici."
    
        # Sinon, construire la chaîne avec tous les items
        msg = "Vous disposez des items suivants :\n"
        for item in self.inventory.values():
             msg += f"    - {item}\n"
        return msg
        # Get the inventory
