"""Hook UserPromptSubmit : affiche les nouveaux messages de l'autre dev (memory/messages.md).

Lancé automatiquement par Claude Code avant chaque message (voir .claude/settings.json).
- git fetch, puis lit memory/messages.md sur toutes les branches distantes + la copie locale.
- Affiche uniquement les lignes jamais vues sur ce clone ; sinon n'affiche rien.
- Les lignes déjà vues sont notées dans .git/claude-seen-messages (propre à chaque clone, jamais commité).
- Ne modifie aucun fichier du repo et ne bloque jamais : toute erreur = silence.
"""
import os
import subprocess
import sys

MSG_PATH = "memory/messages.md"


def git(*args, timeout=8):
    r = subprocess.run(["git", *args], capture_output=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return r.stdout if r.returncode == 0 else ""


def message_lines(text):
    return [l.strip() for l in text.splitlines() if l.strip().startswith("- ")]


def main():
    root = os.environ.get("HORROR_DIR") or "/home/user/horror"   # clone du repo de Seb (sebattfg/Horror) ; absent = silence
    if not os.path.isdir(os.path.join(root, ".git")):
        return
    os.chdir(root)
    git_dir = git("rev-parse", "--git-dir").strip()
    if not git_dir:
        return
    seen_file = os.path.join(git_dir, "claude-seen-messages")

    try:
        git("fetch", "--quiet", "origin", timeout=6)
    except Exception:
        pass  # hors ligne : on regarde quand même ce qu'on a déjà

    # Mes propres lignes (copie locale) ne sont jamais "nouvelles" pour moi.
    local = ""
    if os.path.exists(MSG_PATH):
        with open(MSG_PATH, encoding="utf-8", errors="replace") as f:
            local = f.read()
    local_lines = set(message_lines(local))

    remote_lines = []
    for ref in git("for-each-ref", "--format=%(refname)", "refs/remotes/origin").split():
        if ref.endswith("/HEAD"):
            continue
        for l in message_lines(git("show", f"{ref}:{MSG_PATH}")):
            if l not in remote_lines:
                remote_lines.append(l)

    first_run = not os.path.exists(seen_file)
    seen = set()
    if not first_run:
        with open(seen_file, encoding="utf-8", errors="replace") as f:
            seen = set(l.rstrip("\n") for l in f)

    new = [l for l in remote_lines if l not in seen and l not in local_lines]

    with open(seen_file, "a", encoding="utf-8") as f:
        for l in sorted((set(remote_lines) | local_lines) - seen):
            f.write(l + "\n")

    if new:
        sys.stdout.reconfigure(encoding="utf-8")  # console Windows = cp1252 → l'emoji planterait
        print("📬 Nouveau(x) message(s) de l'autre dev dans memory/messages.md (arrivé(s) sur GitHub, pas encore pull) :")
        for l in new:
            print(l)
        print("→ Signale-le à l'utilisateur. Fais un git pull quand c'est sans risque.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
