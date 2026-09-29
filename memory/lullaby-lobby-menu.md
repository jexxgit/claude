---
name: lullaby-lobby-menu
description: "Architecture du menu/lobby LULLABY dans la place Claynns_Vicky (Studio, pas le repo Horror) : objets, scripts, contrats de noms, comportements"
metadata:
  author: Claude Jexx
  node_type: memory
  type: project
  date: 2026-09-29
---

Jeu = **LULLABY** (nom choisi par Jexx le 2026-09-29). Histoire (repo sebattfg/Horror, `memory/story-plan.md`) : hôpital abandonné, un homme infecté est devenu un monstre qui a tué tout le monde ; une créature imite une infirmière au téléphone ; « don't run, it hears everything » ; « I'll be waiting for you… in Room 6 ». Tout le texte en jeu = anglais. Réponses à Jexx en français. [Claude Jexx]

Place Studio : **Claynns_Vicky's Place: 09272026_1** (placeId 132558889592601). Le `studio_id` du MCP change à chaque réouverture : toujours refaire `list_roblox_studios`. Une 2e place existe : "Horror with jexx prime" (placeId 84834548474198) = le jeu de Seb. [Claude Jexx]

## Scène (Workspace)
- `LobbyCamAnchor` (position seule utilisée), `LobbySpawn`, musique `SoundService.Menu` (déjà là, loop, jouée toute seule, pas touchée).
- `LobbySeats` : Seat1 (= ancien LobbyMiddleSeat, milieu du banc, renommé) + Seat2 (+3.97 X) + Seat3 (-3.97) + Seat4 (+8.03, banc voisin). Les sièges regardent +Z (vers la caméra). Écran-droite = +X, écran-gauche = -X.
- Un rideau métallique `Workspace.Lobby.Shutter_card.FullGrid` bloque le couloir à x≈-16.7 (z -64..-49.7) : utilisé par les patients.

## Scripts
- `ServerScriptService.LobbyServer` : `Players.CharacterAutoLoads=false`. Chaque joueur est assis AUTOMATIQUEMENT au 1er siège libre (milieu d'abord), personnage chargé à la main sur le siège, immobile, re-assis s'il tombe, respawn sur le même siège. >4 joueurs = attend sans personnage. `ReplicationFocus = LobbyCamAnchor` (StreamingEnabled). La **party** est indépendante du siège : Create / Join / Leave ne changent que l'appartenance (1 party par serveur, max 4). Remotes créés dans `ReplicatedStorage.LobbyRemotes` : `LobbyAction` (RemoteFunction "Create"/"Join"/"Leave"/"State") et `LobbyState` (RemoteEvent, state = {host, max, members={userId,name,slot,party}}). Anti-spam 0.4 s.
- `StarterPlayerScripts.LobbyCamera` : caméra Scriptable posée sur l'ancre, regarde Seat1 (+`AimOffset` 0,2.1,0), FOV 55, balancement main/vent (bruit + rafales), souris = 15 % du demi-FOV + petit décalage, "punch" (zoom + tremblement) déclenché par l'attribut joueur `LobbyPunch`. Tous les réglages dans `CFG` en haut. Cache PlayerList/Backpack/Health/Emotes et le bouton reset.
- `StarterPlayerScripts.LobbyUI` : lie l'UI par NOM (recherche récursive dans `PlayerGui.LobbyMenu`). Clone lui-même `StarterGui.LobbyMenu` dans PlayerGui (car CharacterAutoLoads=false → Roblox ne copie StarterGui qu'au 1er spawn) et détruit le doublon. Animations : typewriter, planches qui apparaissent/disparaissent en fondu (`setBtn`), bannière `celebrate()`, panneau party (`setParty`), poussière, vacillement néon, glitch du titre, rideau d'intro, sons.
- `ServerScriptService.LobbyPatients` : patients ambiants (voir plus bas).

## UI `StarterGui.LobbyMenu` (ScreenGui, ResetOnSpawn=false)
Noms attendus par LobbyUI : `CreateButton`, `JoinButton`, `LeaveButton` (TextButton, dans `Panel.ButtonSlot` : les 3 planches se superposent au même endroit, jamais de saut), `Status`, `Slot1..Slot4` (TextLabel + `Avatar` ImageLabel frère dans chaque `RowN`), `PartyList` (dans `PartyPanel`, CanvasGroup à droite/milieu, visible seulement dans la party, membres de la party seulement, hôte en 1er), `Banner` (Text, Line ; en bas de l'écran, centré), `Curtain` (Visible=false en édition, le script le met visible au lancement), `Flicker`, `Vignette` (ZIndex -1000), `BarTop/BarBottom`, `Ink` (fondu d'encre), `VinesLeft`, `VinesTop`, `Panel` (Title texte "LULLABY", Subtitle "don't run. it hears everything.").
Tailles verrouillées avec `UIAspectRatioConstraint` en `ScaleWithParentSize` (PAS `FitWithinMaxSize` avec X=0 → taille 0). Survol : texte JAUNE (232,196,72), pas de contour. Les autres rouges (flash écran, trait bannière, glitch) sont restés rouges. [Claude Jexx]

## Sons : `SoundService.LobbyUI` (SoundGroup, 9 Sound VIDES à remplir par Jexx)
Hover, Click, Create, Join, Leave, Error, MemberJoined, MemberLeft, MenuIntro (attribut `Description` sur chacun). Vides = silencieux.

## Patients ambiants
Apparaissent derrière le rideau (x=-2, z=-52.5, hors caméra), le rideau `Shutter_card` se lève (les lames s'empilent sous la barre du haut, `SHUTTER_LIFT`=11.3 max), ils traversent vers la GAUCHE de l'écran, puis tournent à LEUR gauche (+Z, côté bancs) et disparaissent (-70,-26) ; le rideau se referme. Toutes les 9-22 s, 2 max. Habillage = VRAIS assets Roblox dans `ServerStorage.PatientAssets` (`Shirts` = Shirt avec templates 10335864342/79654995040551 ; `Hair` = Accessory : HairBlack, HairHalfUp, HairPlain, HairMessy), visage effacé, peau pâle. Réglages dans `CFG` de LobbyPatients (PATH, WALK_SPEED, SHUTTER_*, INTERVAL…). [Claude Jexx]
