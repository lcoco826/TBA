# Description: Character class
# Description: Character class

import random
import game

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
    
    def get_msg(self):
        """
        Retourne et supprime le premier message du personnage.
        Affiche cycliquement les messages (les supprime au fur et à mesure).
        
        Returns:
            str: Le message du personnage
        """
        # Si plus de messages, le personnage n'a rien à dire
        if not self.msgs:
            return f"{self.name} n'a rien d'autre à dire."
        
        # Retirer et retourner le premier message
        msg = self.msgs.pop(0)
        return f"{self.name} dit : '{msg}'"
    
    def move(self):
        """
        Déplace le personnage de manière aléatoire.
        Le personnage a une chance sur deux de se déplacer.
        S'il se déplace, il va dans une pièce adjacente au hasard.
        
        Returns:
            bool: True si le personnage s'est déplacé, False sinon
        """
        # Une chance sur deux de se déplacer
        if random.choice([True, False]):
            if getattr(game, "DEBUG", False):
                print(f"DEBUG: {self.name} décide de rester sur place.")
            return False
        
        # Récupérer les sorties disponibles (non-None)
        available_exits = [room for room in self.current_room.exits.values() if room is not None]
        
        # Si aucune sortie disponible, rester sur place
        if not available_exits:
            if getattr(game, "DEBUG", False):
                print(f"DEBUG: {self.name} ne peut pas bouger (aucune sortie).")
            return False
        
        # Choisir une pièce au hasard
        old_room = self.current_room
        new_room = random.choice(available_exits)
        
        # Retirer le personnage de l'ancienne pièce
        if self.name in old_room.characters:
            del old_room.characters[self.name]
        
        # Déplacer le personnage
        self.current_room = new_room
        new_room.characters[self.name] = self
        
        if getattr(game, "DEBUG", False):
            print(f"DEBUG: {self.name} se déplace de '{old_room.name}' vers '{new_room.name}'.")
        
        return True