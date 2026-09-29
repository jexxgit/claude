--[[ LULLABY loading screen (client, put it in ReplicatedFirst of EVERY place of the game): black screen + animated syringe bottom-right.
   Sprite sheet: 4 x 4 frames of 256 px (rbxassetid://108745882918693, made by make_syringe_sprite.py); only frames 0-11 are played.
   It shows by itself while the place loads (at least MIN_TIME), sets the player attribute LoadingDone when it is over (LobbyIntro waits for it)
   and fades out. It can also be shown again at any time (start of a game, big area like the Forest, ...):
       player:SetAttribute("ShowLoading", true)    -- black + syringe fade in
       player:SetAttribute("ShowLoading", false)   -- fade out when the heavy work is done
   In the lobby it also shows on its own when the host's START launches a teleport (RemoteEvent LobbyRemotes.LobbyStarted, {teleporting = true}).
   Everything to tweak is in CFG. ]]
local Players = game:GetService("Players")
local ReplicatedFirst = game:GetService("ReplicatedFirst")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local ContentProvider = game:GetService("ContentProvider")

local CFG = {
	SPRITE = "rbxassetid://108745882918693",
	FRAME = 256,            -- px of one frame in the sheet
	COLS = 4, ROWS = 4,
	FRAMES = 12,            -- only the filling frames (0-11): no droplet / drip frames
	FRAME_TIME = 0.06,      -- seconds per frame
	SIZE = 160,             -- px on screen
	MARGIN = 20,            -- px from the bottom-right corner
	WAIT_FOR_LOBBY = true,  -- true in the lobby place, false in the game places
	MIN_TIME = 2.5,         -- the first load is never shorter than this
	MAX_TIME = 25,          -- failsafe for the first load
	FADE_IN = 0.5,
	FADE_OUT = 0.7,
	TELEPORT_MAX = 40,      -- if the teleport has not taken us away after this long, the screen hides again (failed teleport)
}

pcall(function() ReplicatedFirst:RemoveDefaultLoadingScreen() end)
local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

local gui = Instance.new("ScreenGui")
gui.Name, gui.DisplayOrder, gui.IgnoreGuiInset, gui.ResetOnSpawn = "LoadingScreenGui", 1000, true, false
gui.Parent = playerGui
local black = Instance.new("Frame")
black.Size, black.BackgroundColor3, black.BorderSizePixel = UDim2.fromScale(1, 1), Color3.new(0, 0, 0), 0
black.Active = true   -- swallows clicks while it is up
black.Parent = gui
local img = Instance.new("ImageLabel")
img.AnchorPoint, img.Position, img.Size = Vector2.new(1, 1), UDim2.new(1, -CFG.MARGIN, 1, -CFG.MARGIN), UDim2.fromOffset(CFG.SIZE, CFG.SIZE)
img.BackgroundTransparency, img.Image, img.ImageRectSize = 1, CFG.SPRITE, Vector2.new(CFG.FRAME, CFG.FRAME)
img.ZIndex = 2
img.Parent = gui
task.spawn(function() pcall(function() ContentProvider:PreloadAsync({img}) end) end)

-- show / hide (fade), the syringe animation only runs while the screen is up
local shown, token = false, 0
local function show(fade)
	token += 1
	local my = token
	if shown then
		TweenService:Create(black, TweenInfo.new(0.2), {BackgroundTransparency = 0}):Play()
		TweenService:Create(img, TweenInfo.new(0.2), {ImageTransparency = 0}):Play()
		return
	end
	shown = true
	gui.Enabled = true
	if fade > 0 then
		black.BackgroundTransparency, img.ImageTransparency = 1, 1
		local info = TweenInfo.new(fade, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
		TweenService:Create(black, info, {BackgroundTransparency = 0}):Play()
		TweenService:Create(img, info, {ImageTransparency = 0}):Play()
	else
		black.BackgroundTransparency, img.ImageTransparency = 0, 0
	end
	task.spawn(function()
		local i = 0
		while shown and token == my and gui.Parent do
			local f = i % CFG.FRAMES
			img.ImageRectOffset = Vector2.new((f % CFG.COLS) * CFG.FRAME, (f // CFG.COLS % CFG.ROWS) * CFG.FRAME)
			i += 1
			task.wait(CFG.FRAME_TIME)
		end
	end)
end
local function hide(fade)
	if not shown then return end
	token += 1
	local my = token
	local info = TweenInfo.new(fade, Enum.EasingStyle.Sine, Enum.EasingDirection.Out)
	TweenService:Create(black, info, {BackgroundTransparency = 1}):Play()
	TweenService:Create(img, info, {ImageTransparency = 1}):Play()
	task.delay(fade + 0.05, function()
		if token == my then shown = false; gui.Enabled = false end
	end)
end

-- 1) first load of the place
show(0)
task.delay(CFG.MAX_TIME, function()   -- failsafe: never trap the player behind the black screen
	player:SetAttribute("LoadingDone", true)
	if not player:GetAttribute("ShowLoading") then hide(CFG.FADE_OUT) end
end)
task.spawn(function()
	local t0 = os.clock()
	if not game:IsLoaded() then game.Loaded:Wait() end
	if CFG.WAIT_FOR_LOBBY then   -- lobby place: also wait for the lobby scene / remotes (other places: set to false, or add what THEY need, e.g. the Forest)
		pcall(function()
			ReplicatedStorage:WaitForChild("LobbyRemotes", 15)
			workspace:WaitForChild("LobbyCamAnchor", 15)
		end)
	end
	local left = CFG.MIN_TIME - (os.clock() - t0)
	if left > 0 then task.wait(left) end
	player:SetAttribute("LoadingDone", true)   -- the intro / the game starts right under the fading black
	if not player:GetAttribute("ShowLoading") then hide(CFG.FADE_OUT) end
end)

-- 2) on demand (game start, big area...): player:SetAttribute("ShowLoading", true / false)
player:GetAttributeChangedSignal("ShowLoading"):Connect(function()
	if player:GetAttribute("ShowLoading") then show(CFG.FADE_IN) else hide(CFG.FADE_OUT) end
end)

-- 3) lobby: START launched a teleport -> the loading screen covers the wait until the other place takes over
task.spawn(function()
	local remotes = ReplicatedStorage:WaitForChild("LobbyRemotes", 60)
	local started = remotes and remotes:WaitForChild("LobbyStarted", 10)
	if not started then return end
	started.OnClientEvent:Connect(function(info)
		if info and info.teleporting then
			player:SetAttribute("ShowLoading", true)
			task.delay(CFG.TELEPORT_MAX, function() player:SetAttribute("ShowLoading", false) end)
		end
	end)
end)
