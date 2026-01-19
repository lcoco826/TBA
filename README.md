# TBA

Ce repo contient une version avancée du jeu d’aventure TBA.

Le jeu comporte **8 lieux**, des **objets** (items), des **PNJ** et des **quêtes**. Une interface graphique (GUI) a également été ajoutée pour améliorer l'expérience utilisateur, bien que le mode console reste disponible.

## Fonctionnalités

**Exploration** : 8 lieux à découvrir (Plage, Crique, Forêt, Lagune, Falaise, Volcan, Grotte, Cascade).
**Inventaire** : Gestion d'objets avec un système de poids limite.
**PNJ** : Interaction avec des personnages (Jacob le perroquet, le Crocodile, les Singes).
**Quêtes** : Système d'objectifs à accomplir pour gagner des récompenses.
**Interface** : Fenêtre graphique avec boutons de déplacement, images des lieux et zone de texte.

## Structuration

Le projet est composé des modules suivants :

- `game.py` / `Game` : Moteur du jeu, configuration du monde et interface graphique (Tkinter).
- `room.py` / `Room` : Gestion des lieux et de leurs connexions.
- `player.py` / `Player` : Gestion du joueur, de son inventaire et de l'historique.
- `command.py` / `Command` : Structure des commandes.
- `actions.py` / `Actions` : Implémentation des actions du joueur (go, take, talk, etc.).
- `character.py` / `Character` : Gestion des personnages non-joueurs (PNJ).
- `item.py` / `Item` : Gestion des objets (poids, description).
- `quest.py` / `Quest` & `QuestManager` : Gestion des quêtes et objectifs.

## Lancement

- **Mode graphique** (recommandé) : `python game.py`
- **Mode console** : `python game.py --cli`
- **Mode debug** : `python game.py --debug`
