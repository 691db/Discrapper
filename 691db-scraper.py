import os
import sys
import glob
import asyncio
import discord
import requests
from pystyle import Colors, Colorate, Center, Write

# Configuration des couleurs PyStyle
COLOR_GRADIENT = Colors.blue_to_white
COLOR_ALT = Colors.cyan_to_blue

# Chemin absolu du dossier où se trouve ce script Python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class DiscordMultiTool(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        
        # Vérification et création conditionnelle du dossier downloads
        self.output_dir = os.path.join(SCRIPT_DIR, "downloads")
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                print(Colorate.Horizontal(Colors.red_to_white, f"[!] Impossible de créer le dossier downloads : {e}"))

    async def on_ready(self):
        asyncio.create_task(self.main_menu())

    def print_header(self):
        clear_terminal()
        print_banner()
        print(Colorate.Horizontal(Colors.green_to_white, f"[+] Bot connecté avec succès : {self.user}\n"))

    def download_file(self, url, prefix, identifier):
        if not url:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Aucun élément graphique ({prefix}) trouvé pour cette cible."))
            return

        base_url = str(url).split("?")[0]
        full_url = f"{base_url}?size=1024"

        ext = ".gif" if "a_" in base_url.split("/")[-1] else ".png"
        filename = f"{prefix}_{identifier}{ext}"
        filepath = os.path.join(self.output_dir, filename)

        try:
            res = requests.get(full_url)
            if res.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(res.content)
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Fichier sauvegardé : {filepath}"))
            else:
                print(Colorate.Horizontal(Colors.red_to_white, f"[-] Échec du téléchargement (HTTP {res.status_code})."))
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Erreur lors du téléchargement : {e}"))

    async def prompt_input(self, text):
        return (await asyncio.to_thread(Write.Input, text, COLOR_ALT, 0.005)).strip()

    async def show_credits(self):
        clear_terminal()
        print_banner()
        credits_page = """
┌─── [ CRÉDITS DU TOOL ]
│
│ Made by 691db
│ Discord     : .4cm.
│ Guns.lol    : https://guns.lol/691db
│ GitHub      : https://github.com/ pas de github pr l'instant
│ Join our Discord Server : https://discord.gg/KTsayDpTK
│ Merci d'utiliser Discord Asset Scraper Multi-Tool !
└───
"""
        print(Colorate.Horizontal(COLOR_GRADIENT, credits_page))
        await self.prompt_input("Appuyez sur Entrée pour revenir au menu...")

    async def main_menu(self):
        while True:
            self.print_header()

            menu_text = """
┌─── [ OPTIONS UTILISATEURS ]
│ [1] Scrap l'Avatar Global (PDP)
│ [2] Scrap la Bannière
│ [3] Scrap PDP + Bannière (Pack)
│ [4] Scrap l'Avatar Spécifique d'un Serveur
│
├─── [ OPTIONS SERVEURS ] ** Bot doit être sur le server **
│ [5] Scrap l'Icône du Serveur
│ [6] Scrap la Bannière du Serveur
│ [7] Scrap l'Arrière-plan d'invitation (Splash)
│
└─── [ AUTRES ]
  [C] Crédits
  [0] Quitter le Tool

  """
            print(Colorate.Horizontal(COLOR_GRADIENT, menu_text))

            choice = await self.prompt_input("Select Option ➜ ")

            if choice.upper() == "C":
                await self.show_credits()
                continue

            elif choice == "0":
                print(Colorate.Horizontal(Colors.yellow_to_red, "\n[!] Fermeture du tool..."))
                await self.close()
                sys.exit()

            # --- MODULES UTILISATEURS ---
            elif choice in ["1", "2", "3", "4"]:
                user_id = await self.prompt_input("ID Utilisateur ➜ ")
                if not user_id.isdigit():
                    print(Colorate.Horizontal(Colors.red_to_white, "[!] ID invalide."))
                    await asyncio.sleep(2)
                    continue

                try:
                    user = await self.fetch_user(int(user_id))
                except discord.NotFound:
                    print(Colorate.Horizontal(Colors.red_to_white, "[!] Utilisateur introuvable."))
                    await asyncio.sleep(2)
                    continue
                except Exception as e:
                    print(Colorate.Horizontal(Colors.red_to_white, f"[!] Erreur : {e}"))
                    await asyncio.sleep(2)
                    continue

                if choice == "1":
                    self.download_file(user.avatar, "user_avatar", user.id)

                elif choice == "2":
                    self.download_file(user.banner, "user_banner", user.id)

                elif choice == "3":
                    self.download_file(user.avatar, "user_avatar", user.id)
                    self.download_file(user.banner, "user_banner", user.id)

                elif choice == "4":
                    guild_id = await self.prompt_input("ID du Serveur ➜ ")
                    if not guild_id.isdigit():
                        print(Colorate.Horizontal(Colors.red_to_white, "[!] ID de serveur invalide."))
                        await asyncio.sleep(2)
                        continue
                    try:
                        guild = self.get_guild(int(guild_id)) or await self.fetch_guild(int(guild_id))
                        member = await guild.fetch_member(user.id)
                        self.download_file(member.guild_avatar, f"server_avatar_{guild.id}", user.id)
                    except Exception as e:
                        print(Colorate.Horizontal(Colors.red_to_white, f"[!] Membre introuvable sur ce serveur : {e}"))

                await asyncio.sleep(2)

            # --- MODULES SERVEURS ---
            elif choice in ["5", "6", "7"]:
                guild_id = await self.prompt_input("ID du Serveur ➜ ")
                if not guild_id.isdigit():
                    print(Colorate.Horizontal(Colors.red_to_white, "[!] ID invalide."))
                    await asyncio.sleep(2)
                    continue

                try:
                    guild = self.get_guild(int(guild_id)) or await self.fetch_guild(int(guild_id))
                except discord.NotFound:
                    print(Colorate.Horizontal(Colors.red_to_white, "[!] Serveur introuvable ou le bot n'y est pas présent."))
                    await asyncio.sleep(2)
                    continue
                except Exception as e:
                    print(Colorate.Horizontal(Colors.red_to_white, f"[!] Erreur : {e}"))
                    await asyncio.sleep(2)
                    continue

                if choice == "5":
                    self.download_file(guild.icon, "guild_icon", guild.id)
                elif choice == "6":
                    self.download_file(guild.banner, "guild_banner", guild.id)
                elif choice == "7":
                    self.download_file(guild.splash, "guild_splash", guild.id)

                await asyncio.sleep(2)

            else:
                print(Colorate.Horizontal(Colors.red_to_white, "[!] Choix non valide."))
                await asyncio.sleep(1.5)


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = """
▓█████▄  ██▓  ██████  ▄████▄   ██▀███   ▄▄▄       ██▓███  ▓█████  ██▀███  
▒██▀ ██▌▓██▒▒██    ▒ ▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
░██   █▌▒██▒░ ▓██▄   ▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
░▓█▄   ▌░██░  ▒   ██▒▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
░▒████▓ ░██░▒██████▒▒▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒
 ▒▒▓  ▒ ░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
 ░ ▒  ▒  ▒ ░░ ░▒  ░ ░  ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
 ░ ░  ░  ▒ ░░  ░  ░  ░          ░░   ░   ░   ▒   ░░          ░     ░░   ░ 
   ░     ░        ░  ░ ░         ░           ░  ░            ░  ░   ░     
 ░                   ░                                                    
"""
    print(Colorate.Horizontal(COLOR_GRADIENT, banner))


def get_token():
    os.chdir(SCRIPT_DIR)

    txt_files = [f for f in glob.glob(os.path.join(SCRIPT_DIR, "*.txt")) if os.path.isfile(f)]

    for file_path in txt_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                if content:
                    file_name = os.path.basename(file_path)
                    print(Colorate.Horizontal(Colors.green_to_white, f"[+] Token détecté et chargé depuis : {file_name}"))
                    return content
        except Exception:
            continue

    print(Colorate.Horizontal(Colors.yellow_to_red, "[!] Aucun fichier .txt contenant un token n'a été trouvé à la racine."))
    token = Write.Input("Entrez le Token du Bot Discord ➜ ", COLOR_ALT, interval=0.005).strip()

    if token:
        save_path = os.path.join(SCRIPT_DIR, "token.txt")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(token)
            print(Colorate.Horizontal(Colors.green_to_white, "[+] Token sauvegardé dans token.txt pour les futurs lancements."))
        except Exception:
            pass

    return token


def main():
    clear_terminal()
    print_banner()

    token = get_token()

    if not token:
        print(Colorate.Horizontal(Colors.red_to_white, "[!] Aucun token fourni. Lancement annulé."))
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit()

    print(Colorate.Horizontal(Colors.cyan_to_blue, "\n[*] Connexion au bot Discord en cours..."))

    client = DiscordMultiTool()
    try:
        client.run(token)
    except discord.LoginFailure:
        print(Colorate.Horizontal(Colors.red_to_white, "[!] Token invalide dans le fichier texte."))
        input("\nAppuyez sur Entrée pour quitter...")
    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_white, f"[!] Erreur lors de la connexion : {e}"))
        input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()