# deezer-discord-rpc

> Shows the track you're playing on Deezer as Discord Rich Presence (via Last.fm now-playing + album art).

## How it works
Deezer has no public "now playing" API, so the script reads it from **Last.fm** (scrobbled by Web Scrobbler),
fetches the album art and pushes it to **Discord Rich Presence** with `pypresence`. It detects when Discord is closed and reconnects.

## Run
```bash
pip install requests psutil pypresence
set DISCORD_CLIENT_ID=...
set LASTFM_API_KEY=...
set LASTFM_USERNAME=...
python DeezerRPC.py
```

---
Made by [Tom Galvan](https://tomglv.dev) · Bachelor in AI, ECE Paris
