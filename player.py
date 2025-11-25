# Define the Player class.
class Player:

    def __init__(self, name):
        self.name = name
        self.current_room = None
        self.history = []  # Historique des salles visitées

    def move(self, direction):
        # Dictionnaire de normalisation des directions
        direction_map = {
            "N": "N", "NORD": "N", "Nord": "N", "nord": "N", "n": "N",
            "S": "S", "SUD": "S", "Sud": "S", "sud": "S", "s": "S",
            "E": "E", "EST": "E", "Est": "E", "est": "E", "e": "E"
            "O": "O", "OUEST": "O", "Ouest": "O", "ouest": "O", "o": "O"
            "U": "U", "UP": "U", "Up": "U", "up": "U", "u": "U"
            "D": "D", "DOWN": "D", "Down": "D", "down": "D", "d": "D"
        }

        # Normalisation de la direction
        normalized_direction = direction_map.get(direction)
        print(direction, normalized_direction)
        if normalized_direction is None:
            print(f"\nDirection '{direction}' non reconnue.\n")
            print(self.current_room.get_long_description())
            #print(f"\nDirection '{direction}' invalide ! Veuillez entrer une direction valide.\n")
            return False

        # Vérifier si la sortie existe
        next_room = self.current_room.exits.get(normalized_direction)
        if next_room is None:
            print("\nAucune porte dans cette direction !\n")
            print(self.current_room.get_long_description())
            return False

        # Ajouter la salle actuelle à l’historique
        self.history.append(self.current_room)

        # Déplacer le joueur
        self.current_room = next_room
        print(self.current_room.get_long_description())
        print(self.get_history())
        return True

    def undo(self):
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
