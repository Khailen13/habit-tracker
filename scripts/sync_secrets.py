"""
Синхронизация GitHub Secrets с использованием python-dotenv.
Требует: python-dotenv, GitHub CLI (gh)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


def run(cmd):
    """Запускает команду и возвращает результат"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", f"Ошибка выполнения: {e}"


def main():
    print("=== GitHub Secrets Sync ===")

    # 1. Проверка GitHub CLI
    ok, _, _ = run("gh --version")
    if not ok:
        print("❌ Установите GitHub CLI: https://cli.github.com/")
        sys.exit(1)

    # 2. Проверка авторизации
    ok, _, _ = run("gh auth status")
    if not ok:
        print("🔐 Авторизуйтесь: gh auth login")
        sys.exit(1)

    # 3. Определение репозитория
    repo = os.getenv("GH_REPO")
    if not repo:
        ok, out, _ = run("git remote get-url origin")
        if ok and out:
            match = re.search(r"github\.com[/:]([^/]+/[^/.]+?)(\.git)?$", out)
            repo = match.group(1) if match else None

    if not repo:
        repo = input("Введите owner/repo: ").strip()
        if not repo:
            print("❌ Репозиторий не указан")
            sys.exit(1)

    print(f"📦 Репозиторий: {repo}")

    # 4. Поиск .env файла
    env_path = os.getenv("ENV_FILE", ".env")
    if not os.path.exists(env_path):
        parent_env = Path(__file__).parent.parent / ".env"
        if parent_env.exists():
            env_path = str(parent_env)
        else:
            print("❌ .env не найден. Искал:")
            print(f"   • {os.path.abspath('.env')}")
            print(f"   • {parent_env}")
            sys.exit(1)

    print(f"📄 Файл: {env_path}")

    # 5. Чтение переменных с python-dotenv (одна строка!)
    secrets = dotenv_values(env_path)

    # Убираем None значения и пустые строки
    secrets = {k: v for k, v in secrets.items() if v is not None and str(v).strip()}

    if not secrets:
        print("❌ В файле нет переменных")
        sys.exit(1)

    print(f"🔑 Найдено переменных: {len(secrets)}")

    # 6. Отправка через gh
    success, error = 0, 0
    for key, val in secrets.items():
        # Экранируем кавычки для shell
        val_escaped = str(val).replace('"', '\\"').replace("$", "\\$")
        cmd = f'gh secret set "{key}" --body "{val_escaped}" --repo "{repo}"'
        ok, _, err = run(cmd)

        if ok:
            print(f"  ✅ {key}")
            success += 1
        elif "already exists" in err:
            print(f"  ⚠️  {key} (уже существует)")
            success += 1
        else:
            print(f"  ❌ {key}: {err[:80]}")
            error += 1

    # 7. Итог
    print(f"\n📊 Итог: {success} успешно, {error} с ошибками")
    if error == 0:
        print("✅ Все секреты синхронизированы")
    print(f"🔗 https://github.com/{repo}/settings/secrets/actions")


if __name__ == "__main__":
    # Обработка аргументов
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Синхронизация .env с GitHub Secrets")
            print("Использование: python sync_secrets.py [owner/repo]")
            print("Примеры:")
            print("  python sync_secrets.py")
            print("  python sync_secrets.py user/repo")
            print("  ENV_FILE=.env.prod python sync_secrets.py")
            sys.exit(0)
        elif "/" in sys.argv[1]:
            os.environ["GH_REPO"] = sys.argv[1]

    main()
