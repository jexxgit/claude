---
name: lullaby-todo
description: "LULLABY : décisions de Jexx, non vérifié, restes à faire (2026-09-29)"
metadata:
  author: Claude Jexx
  node_type: memory
  type: project
  date: 2026-09-29
---

## Décisions de Jexx
- Nom du jeu : LULLABY (2026-09-29) (sous-titre "don't run…" supprimé le 2026-09-29 sur demande)
- Vrais assets Roblox pour l'habillage (pas de parts fabriquées) ; textures de menu = mes PNG générés OK, mais JAMAIS de sang/gore.
- Texte de hover jaune, pas de contour ; bannière "PARTY CREATED / YOU JOINED THE PARTY / YOU LEFT THE PARTY" en bas ; avatar à côté de chaque pseudo dans la liste party ; boutons qui ne changent pas de place.
- Jexx accepte que Claude poste/édite sans redemander (mode auto), mais je ne peux pas cliquer "autoriser" moi-même.

## Non vérifié / à regarder dans le Studio de Jexx
- Rendu de la chemise de patient et des coiffures (assets d'autres créateurs) ; animation de marche ; virage à gauche des patients (sens : miroir Z autour de -52.5 pour inverser) ; 2 patients en même temps sous le rideau ; son du rideau (aucun).
- Placement de Seat3/Seat4 avec de vrais 2e/3e/4e joueurs (jamais testé à plusieurs).
- Si les textures ne s'affichent pas : modération en attente ; LobbyUI n'a pas de repli pour VinesLeft/VinesTop (juste Ink/planches ont un repli couleur).

## Idées restantes
- Sons de l'UI à fournir par Jexx (SoundGroup LobbyUI). Pantalon de patient (pas trouvé). Miniature/icône du jeu (sans image uploadée sans accord). Sous-titre/nom de l'expérience à changer dans Creator Hub (pas faisable par outil). Rendre le jaune aussi pour les autres rouges si Jexx le veut. Créer la branche main du dépôt si on veut une PR ; supprimer `menu_textures/raw/` (~9 Mo) une fois tout importé.

## Mise à jour 2026-09-29 (fin de session)
- **Rien n'est sauvegardé par Claude** : Jexx doit Ctrl+S la place (LobbyIntro, LobbyStage, LoadingScreen, LobbyServer, LobbyUI, sons IntroAmbience/Menu).
- START_PLACE_ID (LobbyServer) : placeId du jeu pas encore défini → Jexx la donnera ; le loading + TeleportData sont prêts.
- La place de jeu doit recevoir LoadingScreen.client.luau (ReplicatedFirst) : demandé à Claude Seb par message ; l'image seringue appartient au compte de Jexx.
- Scripts du lobby à ré-exporter dans sebattfg/Horror (lobby/) : LobbyStage (vie procédurale), LobbyIntro, LobbyUI (musique menu), LobbyServer (TeleportData), LoadingScreen — PR pas encore ouverte (Jexx n'a pas dit « oui »).
- Non vérifié : suivi d'un patient par le regard (aucun cas vu en test), 2e joueur, vrai téléportage, sourcils sur d'autres avatars, chapeau sur avatars sans RigidConstraint (fallback AccessoryWeld codé mais jamais vu).
- Sons : IntroWhoosh / IntroHit encore vides.
