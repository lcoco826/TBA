# Define the Room class.

class Room:

    # Define the constructor. 
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.inventory = {}
        self.characters = {}

    # Define the get_exit method.
    def get_exit(self, direction):

        # Return the room in the given direction if it exists.
        if direction in self.exits.keys():
            return self.exits[direction]
        else:
            return None
    
    # Return a string describing the room's exits.
    def get_exit_string(self):
        exit_string = "Sorties: " 
        for exit in self.exits.keys():
            if self.exits.get(exit) is not None:
                exit_string += exit + ", "
        exit_string = exit_string.strip(", ")
        return exit_string

    # Return a long description of this room including exits.
    def get_long_description(self):
        """Retourne une description complète de la pièce incluant les sorties,
        l'inventaire et les personnages présents.
        """
        msg = f"\nVous êtes dans {self.description}\n"

        exit_string = self.get_exit_string()
        if exit_string:
            msg += exit_string + "\n"

        # `get_characters` retourne aussi les items présents dans la pièce
        characters_and_items = self.get_characters()
        if characters_and_items:
            msg += characters_and_items

        return msg

    def get_characters(self):
        """Retourne une chaîne décrivant les items et les personnages présents dans la pièce."""
        # Si ni items ni personnages, rien à afficher
        if not self.inventory and not self.characters:
            return ""

        msg = "\nOn voit:\n"

        # Afficher les items
        for item in self.inventory.values():
            # Certains items peuvent être représentés par un objet Item
            # avec attributs `name`, `description`, `weight`.
            try:
                msg += f"    - {item.name} : {item.description} ({item.weight} kg)\n"
            except Exception:
                # Fallback si l'item est juste une chaîne
                msg += f"    - {item}\n"

        # Afficher les personnages
        for character in self.characters.values():
            msg += f"    - {character}\n"

        return msg

    