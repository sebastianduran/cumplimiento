"""Script para instalar los navegadores de Playwright."""
import subprocess
import sys


def main():
    print("Instalando navegador Chromium para Playwright...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    print("Navegador instalado correctamente.")


if __name__ == "__main__":
    main()
