# -*- coding: utf-8 -*-
import os
import time
import requests
import psutil
from pypresence import Presence
from pypresence.exceptions import InvalidID, DiscordNotFound

# --- CONFIGURATION DISCORD & LAST.FM ---
CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID', '') 
LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY', '') 
LASTFM_USERNAME = os.environ.get('LASTFM_USERNAME', '') 
DISCORD_PROCESS_NAME = "Discord.exe" 

# --- FONCTION DE RECUPERATION LAST.FM ---
def get_lastfm_track():
    """Recupere la chanson en cours de lecture depuis l'API Last.fm."""
    url = (
        f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
        f"&user={LASTFM_USERNAME}&api_key={LASTFM_API_KEY}&format=json&limit=1"
    )
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Verifie si le chemin d'acces aux donnees est valide
        if 'recenttracks' not in data or 'track' not in data['recenttracks'] or not data['recenttracks']['track']:
            return None

        track = data['recenttracks']['track'][0]
        
        # Le marqueur 'nowplaying': 'true' indique la lecture en cours (force par Web Scrobbler)
        if '@attr' in track and track['@attr']['nowplaying'] == 'true':
            
            # TENTATIVE DE RECUPERATION DE L'IMAGE DYNAMIQUE
            album_image_url = ''
            if 'image' in track and len(track['image']) >= 2:
                # Recupere l'URL de l'image de taille moyenne (index 2)
                album_image_url = track['image'][2]['#text']

            return {
                'track': track['name'],
                'artist': track['artist']['#text'],
                'album': track['album']['#text'],
                'image_url': album_image_url  
            }
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requete Last.fm: {e}")
    except Exception as e:
        # Peut echouer si le format de reponse de l'API est inattendu
        pass
    
    return None

# --- FONCTION DE SURVEILLANCE DES PROCESSUS ---
def is_discord_running():
    """Verifie si le processus Discord.exe est en cours d'execution."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == DISCORD_PROCESS_NAME:
            return True
    return False

# --- FONCTION PRINCIPALE DE GESTION RPC ---
def run_rich_presence():
    """Initialise et gere la Rich Presence tant que Discord est ouvert."""
    RPC = None
    try:
        RPC = Presence(CLIENT_ID) 
        RPC.connect()
        print("Connexion RPC etablie.")

        # Boucle de mise a jour
        while is_discord_running(): 
            current_track = get_lastfm_track()
            
            if current_track:
                artist = current_track['artist']
                track = current_track['track']
                image_url = current_track['image_url']

                RPC.update(
                    state=f"par {artist}",
                    details=track,
                    # Tente d'utiliser l'URL de l'image, sinon utilise l'asset generique 'deezer_logo'
                    large_image=image_url if image_url else 'deezer_logo', 
                    start=int(time.time()),
                    # Ajout optionnel du texte alternatif sur l'image
                    large_text=current_track['album'] 
                )

                print(f"Statut mis a jour: {track} par {artist}")
            else:
                RPC.clear()
                print("Aucune chanson detectee via Last.fm. Statut Discord efface.")

            # Rafraichissement toutes les 10 secondes pour une meilleure reactivite
            time.sleep(10) 

    except DiscordNotFound:
        print("Discord n'a pas pu etre trouve ou la connexion est perdue.")
    except InvalidID:
        print("Erreur: L'ID client Discord est invalide.")
    except Exception as e:
        print(f"Erreur inattendue pendant la RPC: {e}")
    finally:
        if RPC:
            RPC.close()
            print("Deconnexion de Discord RPC.")


# --- BOUCLE DE SURVEILLANCE GLOBALE ---
if __name__ == "__main__":
    print("Demarrage du service de surveillance Discord (Ctrl+C pour arreter)...")
    try:
        while True:
            if is_discord_running():
                print("Discord detecte. Lancement de la Rich Presence...")
                run_rich_presence() # Execute le service RPC jusqu'a ce que Discord se ferme
                print("Discord s'est ferme. Mise en pause du service.")
                
            else:
                # Attendre un peu avant de reverifier
                print("Discord non detecte. En attente...")
                time.sleep(30) 
    except KeyboardInterrupt:
        print("Service de surveillance arrete par l'utilisateur.")
    except Exception as e:
        print(f"Erreur critique du service de surveillance: {e}")