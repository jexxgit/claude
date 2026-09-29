# Lullaby - lobby memory (for the other AIs)

Everything below lives in the Roblox Studio place (edited via the mcp-test tools), not in git.

## Scripts
| Script | Type | Role |
|---|---|---|
| `ServerScriptService.LobbyServer` | Script | Seating (everyone auto-seated on `Workspace.LobbySeats.Seat1..4`, characters never auto-load) + multi-party system. Removes the spawn ForceField (SpawnLocation.Duration = 0 + destroys any ForceField). |
| `StarterPlayer.StarterPlayerScripts.LobbyUI` | LocalScript | Menu logic. Left: title + CREATE / LEAVE planks. Right: `Browser` (list of open parties with JOIN) when not in a party, `PartyPanel` (member list) when in one. Create dialog = friends only + max players (1-4). |
| `StarterPlayer.StarterPlayerScripts.LobbyStage` | LocalScript | Decides PER VIEWER who is drawn on which chair (see below). |
| `StarterPlayer.StarterPlayerScripts.LobbyPatients` | LocalScript | Ambient patients walking behind the benches + rolling shutter. Client-side now (was server-side physics, stuttered with several players). Assets moved to `ReplicatedStorage.PatientAssets`. |
| `StarterPlayer.StarterPlayerScripts.LobbyCamera` | LocalScript | Menu camera. `AimOffset` raised to (0, 3.6, 0) so the feet are no longer visible. |

## Remotes (`ReplicatedStorage.LobbyRemotes`)
- `LobbyAction` (RemoteFunction): `"Create", {friendsOnly, max}` | `"Join", {id}` | `"Leave"` | `"State"` -> `ok, err` / state
- `LobbyState` (RemoteEvent): `{max, seats = {{userId,name,slot}}, parties = {{id, host, hostName, friendsOnly, max, members = {{userId,name,slot}}}}}`
- Several parties can exist at once (one per host). Server checks: full, friends only (`host:IsFriendsWith`), already in a party. Host leaves -> oldest member becomes host; empty party is deleted.

## Stage rules (LobbyStage)
- Real characters (server-seated) are hidden for everybody (LocalTransparencyModifier); local copies ("puppets", built from HumanoidDescription, sit anim `rbxassetid://2506281703`, root offset 2.09 studs above the seat) are drawn instead.
- Front row (next to the camera): ONLY your party. Host = Seat1 (middle); other members = Seat2..4. No party = you alone in the middle, nobody beside you.
- Everyone else in the server sits on the back-row benches (z = -43.82, facing -Z, 9 seats, stable random slot per player).

## Known limits / not tested
- Tested with a single player in Studio only. Multi-player (2-4 players, friends only with a real friend, JOIN clicks) still to be verified in a live server.
- Non-party players are still visible on the back benches when you are in a party (only the front row is party-only).
- Real characters still exist on the server seats (hidden client-side), so future gameplay code can keep using them.
