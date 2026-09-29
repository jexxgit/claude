---
name: LULLABY loading screen + intro T2W
description: écran de chargement seringue (ReplicatedFirst), intro Tween2Worlds, flux de téléportation START ; à réutiliser dans les autres places
type: project
---
**Loading screen** (source : `loading_sprite/LoadingScreen.client.luau`, à mettre dans **ReplicatedFirst de CHAQUE place** du jeu)
- Fond noir + seringue animée en bas à droite (spritesheet 4x4 de 256 px, `rbxassetid://108745882918693`, blanc/gris/noir, seules les frames 0-11 sont jouées, 0,06 s/frame, 160 px). Généré par `loading_sprite/make_syringe_sprite.py` (raw RGBA → EditableImage → CreateAssetAsync).
- Première charge : visible dès l'arrivée, min 2,5 s, puis attribut joueur `LoadingDone = true` + fondu. `WAIT_FOR_LOBBY = true` seulement dans le lobby (attend LobbyRemotes + LobbyCamAnchor) ; dans les autres places le mettre à false et attendre ce dont CETTE place a besoin.
- À la demande (départ de partie, grosse zone comme la Forest) : `player:SetAttribute("ShowLoading", true)` (fondu noir + seringue), puis `false` quand le lourd est fini.
- Lobby : quand l'hôte fait START, `LobbyStarted {teleporting = true}` déclenche `ShowLoading` tout seul (tant que `START_PLACE_ID` est nil : pas de téléportation, donc pas d'écran).
- `LobbyIntro` attend `LoadingDone` (si `ReplicatedFirst.LoadingScreen` existe) ; il ne cache jamais `LoadingScreenGui`.
- Limite : l'image appartient au compte de Jexx ; une autre expérience ne peut l'utiliser que si le compte/groupe propriétaire est le même (sinon ré-uploader la planche dans le bon compte).

**Données de partie envoyées à la place de jeu** (LobbyServer, quand `START_PLACE_ID` sera défini) : `TeleportOptions:SetTeleportData({from = "LULLABY lobby", host = userId, partyId = id, members = {userIds}})` → dans la place de jeu, côté serveur : `player:GetJoinData().TeleportData`.
- La placeId du jeu n'est pas encore définie (Jexx la donnera plus tard) → `START_PLACE_ID` dans LobbyServer.

**Intro Tween2Worlds** (LobbyIntro, LocalScript) : plan d'ouverture 1,8 s sur `Workspace.Creators` (caméra devant eux, léger arc/avance), puis glissement de 1,1 s (pas de coupure) vers la scène sombre : lettres 3D T2W qui s'assemblent (1,5x plus vite), passage dans le « 2 », lumière qui revient, drift final vers le joueur. Tremblement quasi supprimé (Jexx trouvait ça bizarre). Sous-titre TWEEN2WORLDS en Michroma. Son : `SoundService.LobbyUI.IntroAmbience` = rbxassetid://135482122368656 (Suno, 8,4 s). Musique du menu (`SoundService.Menu`) démarre seulement quand le menu apparaît (LobbyUI, fondu 1,5 s).
