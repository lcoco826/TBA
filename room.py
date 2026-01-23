# pylint: disable=cyclic-import
"""
Module Room - Gère les lieux du jeu.

Ce module contient la classe Room qui représente un lieu dans le jeu.
"""

class Room:
    """
    Représente un lieu (salle) dans le jeu.

    Attributs:
        name (str): Le nom du lieu.
        description (str): La description du lieu.
        image (str): Chemin vers l'image du lieu (optionnel).
        exits (dict): Les sorties vers d'autres lieux.
        inventory (dict): Les objets présents dans le lieu.
        characters (dict): Les personnages présents dans le lieu.
    """

    # Define the constructor.
    def __init__(self, name, description, image=None):
        self.name = name
        self.description = description
        # Optional path (relative) to an image representing the room
        self.image = image
        self.exits = {}
        self.inventory = {}
        self.characters = {}

    def get_exit(self, direction):
        """
        Retourne la pièce dans la direction donnée si elle existe.

        Args:
            direction (str): La direction vers laquelle aller.

        Returns:
            Room: La pièce correspondante ou None.
        """
        if direction in self.exits:
            return self.exits[direction]
        return None

    def get_exit_string(self):
        """Retourne une chaîne décrivant les sorties de la pièce."""
        exit_string = "Sorties : "
        for direction in self.exits:
            if self.exits.get(direction) is not None:
                exit_string += direction + ", "
        exit_string = exit_string.strip(", ")
        return exit_string

    def get_long_description(self):
        """
        Retourne une description de base de la pièce avec les sorties uniquement.
        N'affiche PAS les items ni les personnages (ils seront visibles avec 'look').
        """
        msg = f"\nVous êtes dans {self.description}\n"
        msg += self.get_exit_string() + "\n"

        # Afficher les personnages automatiquement
        if self.characters:
            msg += "\nVous voyez :\n"
            for character in self.characters.values():
                msg += f"    - {character}\n"

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
            except AttributeError:
                # Fallback si l'item est juste une chaîne
                msg += f"    - {item}\n"

        # Afficher les personnages
        for character in self.characters.values():
            msg += f"    - {character}\n"

        return msg
