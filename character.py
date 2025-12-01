# Description: Character class

class Character:
    """
    Représente un personnage non-joueur (PNJ) dans le jeu.
    """
    
    def __init__(self, name, description, current_room, msgs=None):
        """
        Initialise un personnage.
        
        Args:
            name (str): Le nom du personnage
            description (str): La description du personnage
            current_room (Room): La pièce où se trouve le personnage
            msgs (list): Liste des messages que le personnage peut dire
        """
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs if msgs is not None else []
    
    def __str__(self):
        """
        Retourne une représentation textuelle du personnage.
        
        Returns:
            str: Format "Nom : description"
        """
        return f"{self.name} : {self.description}"
    
    def get_msg(self, index=0):
        """
        Retourne un message du personnage.
        
        Args:
            index (int): L'index du message à retourner (par défaut 0)
            
        Returns:
            str: Le message ou un message par défaut si l'index est invalide
        """
        if not self.msgs:
            return f"{self.name} n'a rien à dire."
        
        if 0 <= index < len(self.msgs):
            return f"{self.name} dit : '{self.msgs[index]}'"
        
        return f"{self.name} n'a rien d'autre à dire."
    
    def move(self, new_room):
        """
        Déplace le personnage vers une nouvelle pièce.
        
        Args:
            new_room (Room): La nouvelle pièce de destination
        """
        self.current_room = new_room