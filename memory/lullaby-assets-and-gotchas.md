---
name: lullaby-assets-and-gotchas
description: "IDs Roblox uploadés pour LULLABY, incident de modération, pipeline d'upload de textures, pièges des outils MCP Roblox Studio"
metadata:
  author: Claude Jexx
  node_type: memory
  type: reference
  date: 2026-09-29
---

## Textures uploadées (compte de Jexx, générées en Python : `menu_textures/make_menu_textures.py`)
ink_fade 103920326731659 · plank_1 71013936148351 · plank_2 115155794825415 · plank_3 102575914887487 · vines_left 102404887655491 · vines_top 127571396227276.
Un test 8×8 "LobbyTestPixel" traîne dans l'inventaire (à supprimer). [Claude Jexx]

## ⚠️ Incident modération (2026-09-29)
`Lobby_title_horror` (74172500615500, lettrage avec SANG qui coule) refusé : avertissement Roblox « excessive use of blood ». Le titre est maintenant du TEXTE (police Antique). RÈGLE : ne jamais uploader d'image avec sang / gore ; ne plus rien uploader sans l'accord de Jexx. L'asset fautif est à supprimer dans Creator Hub (Assets). [Claude Jexx]

## Pipeline d'upload d'images (ce qui marche)
1. `upload_image` ne marche PAS (URL GitHub raw = "not trusted"), `store_image` lit les fichiers du PC de Jexx, pas du conteneur cloud.
2. Marche : pousser des dumps RGBA bruts sur GitHub (`menu_textures/raw/*.rgba`, dépôt public jexxgit/claude, branche claude/festive-sagan-spt925) → dans Studio (`execute_luau`, Edit) : `HttpService.HttpEnabled=true` (le remettre après), `GetAsync` des octets, `AssetService:CreateEditableImage({Size=...})`, `WritePixelsBuffer(Vector2.zero, size, buffer.fromstring(data))`, `AssetService:CreateAssetAsync(ei, Enum.AssetType.Image, {Name=...})` → renvoie (résultat, id).
3. Vêtements/coiffures : utiliser `search_asset` (Creator Store, free) + `insert_asset` ; inspecter (scripts !) avant usage ; supprimer les modèles "morph" avec scripts. `insert_asset` d'un Decal donne `.Texture` = id utilisable en `Shirt.ShirtTemplate`.

## Pièges outils
- Dépôt jexxgit/claude : le push a d'abord donné 403 (app Claude non installée) ; corrigé après reconnexion GitHub. Il n'existe QUE la branche claude/festive-sagan-spt925 (pas de main) → pas de PR possible tant que main n'existe pas.
- `screen_capture` marche aussi PENDANT un Play (bon moyen de vérifier l'UI) ; en Edit il sort noir. `camera_position` est ignoré en Play (LobbyCamera reprend la main).
- `VirtualInputManager` interdit (capability) → on ne peut pas cliquer les boutons par script ; tester via les remotes ou un hook temporaire (retiré).
- Edit-DataModel indisponible en Play : toujours `start_stop_play false` avant de modifier.
- Dans Studio de Claude, certains assets ne se chargent pas (console pleine de "could not fetch") ; ça s'est arrangé après réouverture. Ne pas conclure qu'un asset est cassé sur cette seule base.
- `GetUserThumbnailAsync` / `rbxthumb://type=AvatarHeadShot&id=UID&w=150&h=150` OK pour les avatars.
- Les animations (marche des patients `rbxassetid://507777826`) n'ont pas pu être vérifiées visuellement.
