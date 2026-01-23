"""
Module Item - Gère les objets du jeu.
"""

class Item:
    """Représente un objet dans le jeu."""
    # pylint: disable=too-few-public-methods
    def __init__(self, name, description, weight):
        """
        Constructeur de la classe Item.
        
        Args:
            name (str): Le nom de l'objet
            description (str): La description de l'objet
            weight (int): Le poids de l'objet en kg
        """
        self.name = name
        self.description = description
        self.weight = weight
        self.is_beamer = False
        self.charged_room = None


    def __str__(self):
        """
        Retourne une représentation textuelle de l'objet.
        
        Returns: Une chaîne formatée avec le nom, la description et le poids
        """
        return f"{self.name} : {self.description} ({self.weight} kg)"
