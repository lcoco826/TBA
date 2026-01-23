"""
Module Character - Gère les personnages non-joueurs (PNJ).
"""

import random

class Character:
    """
    Représente un personnage non-joueur (PNJ) dans le jeu.
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name, description, current_room, msgs=None, can_move=True):
        """
        Initialise un personnage.
        
        Args:
            name (str): Le nom du personnage
            description (str): La description du personnage
            current_room (Room): La pièce où se trouve le personnage
            msgs (list): Liste des messages que le personnage peut dire
            can_move (bool): Si le personnage peut se déplacer (défaut: True)
        """
        self.name = name
        self.description = description
        self.current_room = current_room
        self.msgs = msgs if msgs is not None else []
        self.can_move = can_move

    def __str__(self):
        """
        Retourne une représentation textuelle du personnage.
        
        Returns:
            str: Format "Nom : description"
        """
        description = self.description
        if isinstance(description, dict):
            description = description.get(self.current_room.name,
                                          description.get('default', '...'))

        return f"{self.name} : {description}"

    def get_msg(self):
        """
        Retourne le message du personnage.
        Affiche cycliquement les messages.
        
        Returns:
            str: Le message du personnage
        """
        msgs_list = self.msgs

        # Si msgs est un dictionnaire, récupérer la liste pour la salle actuelle
        if isinstance(msgs_list, dict):
            msgs_list = msgs_list.get(self.current_room.name, [])

        # Si plus de messages, le personnage n'a rien à dire
        if not msgs_list:
            return f"{self.name} n'a rien d'autre à dire."

        # Retirer le premier message et le remettre à la fin (rotation)
        msg = msgs_list.pop(0)
        msgs_list.append(msg)
        return f"{self.name} dit : '{msg}'"

    def move(self, player=None):
        """
        Déplace le personnage de manière aléatoire.
        Le personnage a une chance sur deux de se déplacer.
        S'il se déplace, il va dans une pièce adjacente au hasard.
        
        Returns:
            bool: True si le personnage s'est déplacé, False sinon
        """
        # Vérifier si le personnage a le droit de bouger
        if not self.can_move:
            return False

        # Si le joueur est dans la même pièce, le personnage ne bouge pas
        # (pour permettre l'interaction)
        if player and player.current_room == self.current_room:
            return False

        import game # pylint: disable=import-outside-toplevel
        # Une chance sur deux de se déplacer
        if random.choice([True, False]):
            # Construire le message DEBUG et le stocker
            msg = f"DEBUG: {self.name} décide de rester sur place."
            try:
                game.DEBUG_LOG.append(msg)
            except Exception: # pylint: disable=broad-exception-caught
                pass
            # Afficher immédiatement si le mode DEBUG est activé
            if getattr(game, "DEBUG", False):
                print(msg)
            return False

        # Récupérer les sorties disponibles (non-None)
        available_exits = [r for r in self.current_room.exits.values() if r is not None]

        # Si aucune sortie disponible, rester sur place
        if not available_exits:
            msg = f"DEBUG: {self.name} ne peut pas bouger (aucune sortie)."
            try:
                game.DEBUG_LOG.append(msg)
            except Exception: # pylint: disable=broad-exception-caught
                pass
            if getattr(game, "DEBUG", False):
                print(msg)
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

        msg = f"DEBUG: {self.name} se déplace de '{old_room.name}' vers '{new_room.name}'."
        try:
            game.DEBUG_LOG.append(msg)
        except Exception: # pylint: disable=broad-exception-caught
            pass
        if getattr(game, "DEBUG", False):
            print(msg)

        return True
