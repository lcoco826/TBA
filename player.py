"""
Module Player - Gère l'état du joueur et ses interactions avec le monde du jeu.

Ce module contient la classe Player qui représente le joueur dans le jeu.
Elle gère:
- La position actuelle du joueur
- L'historique des salles visitées
- L'inventaire et la limite de poids
- Les récompenses obtenues
- Le mouvement dans le monde
"""


class Player:
    """
    Représente le joueur dans le jeu.
    
    Attributs:
        name (str): Le nom du joueur
        current_room (Room): La salle actuelle du joueur
        history (list): Historique des salles visitées
        inventory (dict): Dictionnaire des items possédés
        max_weight (float): Poids maximum transportable (10 kg)
        rewards (list): Liste des récompenses obtenues
        
    Exemples:
        >>> player = Player("Capitaine")
        >>> player.name
        'Capitaine'
    """

    def __init__(self, name):
        """
        Initialiser un nouveau joueur.
        
        Args:
            name (str): Le nom du joueur
            
        Raises:
            ValueError: Si le nom est vide ou None
        """
        if not name or not isinstance(name, str):
            raise ValueError("Le nom du joueur doit être une chaîne non vide")
        
        self.name = name.strip()
        self.current_room = None
        self.history = []  # Historique des salles visitées
        self.inventory = {}
        self.max_weight = 5
        self.rewards = []  # Récompenses obtenues
        self.endgame_ready = False

    def move(self, direction):
        """
        Se déplacer dans la direction spécifiée.
        
        La direction doit être une direction cardinale valide: N, S, E, O, U, D
        (ou leurs variantes: NORD, SUD, EST, OUEST, UP, DOWN)
        
        Args:
            direction (str): Direction de déplacement
            
        Returns:
            bool: True si le déplacement a réussi, False sinon
            
        Affiche des messages d'erreur détaillés si le déplacement échoue.
        
        Exemples:
            >>> player.move("N")  # Se déplacer au nord
            >>> player.move("NORD")  # Fonctionne aussi
        """
        if not self.current_room:
            print("\n❌ Erreur: Vous n'êtes dans aucune salle.\n")
            return False
    
        # Vérifier si la sortie existe
        next_room = self.current_room.exits.get(direction)
        if next_room is None:
            print(f"\n❌ Aucune porte dans la direction '{direction.upper()}' !")
            print(f"   Sorties disponibles : {', '.join([d for d in self.current_room.exits.keys() if self.current_room.exits[d] is not None])}\n")
            print(self.current_room.get_long_description())
            return False

        # Ajouter la salle actuelle à l'historique
        self.history.append(self.current_room)

        # Déplacer le joueur
        self.current_room = next_room

        # Si on entre dans la forêt (mort immédiate), on n'affiche pas les infos de la salle ni l'historique
        if self.current_room.name == "Forêt":
            return True

        print(self.current_room.get_long_description())
        history_msg = self.get_history()
        if history_msg:
            print(history_msg)
        return True

    def back(self):
        """
        Revenir à la salle précédente si possible.
        
        Vérifie que:
        1. L'historique n'est pas vide
        2. Il existe un chemin de retour (pas de passage unidirectionnel)
        
        Returns:
            bool: True si le retour a réussi, False sinon
            
        Exemples:
            >>> player.back()  # Retourner à la salle précédente
        """
        if not self.history:
            print("\n❌ Vous n'avez aucune salle antérieure. Vous êtes au point de départ.\n")
            return False

        # Récupérer la salle précédente
        previous_room = self.history[-1]
    
        # Vérifier s'il existe un chemin de retour vers la salle précédente
        can_go_back = False
        for direction, room in self.current_room.exits.items():
            if room == previous_room:
                can_go_back = True
                break
    
        # Si aucun chemin de retour n'existe (sens unique)
        if not can_go_back:
            print("\n❌ Impossible de faire demi-tour ! Ce passage est unidirectionnel.\n")
            return False

        # Revenir à la dernière salle visitée
        self.current_room = self.history.pop()
        print(self.current_room.get_long_description())
        history_msg = self.get_history()
        if history_msg:
            print(history_msg)
        return True

    def get_history(self):
        """
        Obtenir une représentation textuelle de l'historique des salles.
        
        Returns:
            str: Chaîne listant les salles visitées (vide si aucune visite)
            
        Exemples:
            >>> player.get_history()
            'Vous avez déjà visité les pièces suivantes:\\n    - une plage...'
        """
        if not self.history:
            return ""
        lines = ["📍 Vous avez déjà visité les pièces suivantes:"]
        for room in self.history:
            lines.append(f"    - {room.description}")
        return "\n".join(lines)

    def get_inventory(self):
        """
        Obtenir une représentation textuelle de l'inventaire.
        
        Affiche:
        - La liste des items
        - Le poids total
        - La capacité restante
        
        Returns:
            str: Chaîne formatée de l'inventaire
            
        Exemples:
            >>> player.get_inventory()
            'Votre inventaire est vide.'
        """
        if not self.inventory:
            return "📭 Votre inventaire est vide."
        
        current_weight = sum(i.weight for i in self.inventory.values())
        remaining = self.max_weight - current_weight
        
        msg = "📦 Vous disposez des items suivants :\n"
        for item in self.inventory.values():
            msg += f"    - {item}\n"
        msg += f"\n💪 Poids : {current_weight:.1f} kg / {self.max_weight} kg (Reste : {remaining:.1f} kg)"
        return msg

    def add_reward(self, reward):
        """
        Ajouter une récompense au joueur.
        
        Args:
            reward (str): Description de la récompense
            
        Affiche un message de confirmation.
        
        Exemples:
            >>> player.add_reward("Carte de l'île")
            '\\nVous avez reçu : Carte de l'île\\n'
        """
        if not hasattr(self, 'rewards'):
            self.rewards = []
        
        if not reward or not isinstance(reward, str):
            print("\n❌ Erreur: La récompense doit être une chaîne non vide.\n")
            return
        
        self.rewards.append(reward)
        print(f"\n🎁 Vous avez reçu : {reward}\n")
        
        if "Sac à dos moyen" in reward:
            self.max_weight += 5
            print(f"💪 Votre capacité d'inventaire augmente de 5kg ! (Total: {self.max_weight}kg)")
        elif "Grand sac à dos" in reward:
            self.max_weight += 10
            print(f"💪 Votre capacité d'inventaire augmente de 10kg ! (Total: {self.max_weight}kg)")
        
        if "Beamer" in reward:
            from item import Item
            beamer = Item("beamer", "un appareil de téléportation mystérieux.", 0)
            beamer.is_beamer = True
            if hasattr(self, 'starting_room'):
                beamer.saved_room = self.starting_room
                beamer.fixed_destination = True
            self.inventory["beamer"] = beamer
            print("✨ Vous obtenez le Beamer ! Il vous ramènera toujours au point de départ.")

    def get_rewards(self):
        """
        Obtenir une représentation textuelle des récompenses obtenues.
        
        Returns:
            str: Chaîne listant les récompenses (ou message si aucune)
            
        Exemples:
            >>> player.get_rewards()
            '\\nRécompenses obtenues :\\n  - Carte de l\\'île\\n'
        """
        if not getattr(self, 'rewards', None):
            return "\n🏆 Vous n'avez obtenu aucune récompense pour le moment.\n"
        
        lines = ["\n🏆 Récompenses obtenues :"]
        for i, reward in enumerate(self.rewards, 1):
            lines.append(f"  {i}. {reward}")
        return "\n".join(lines) + "\n"
