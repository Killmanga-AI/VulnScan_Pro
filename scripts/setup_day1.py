import os
import subprocess
import sys
from pathlib import Path

def run_command(command,description):
    """Run a shell command and print status"""
    print(description)
    try:
        result = subprocess.run(command, shell=True, capture_output=True,text=True)
        if result.returncode == 0:
            print(f"{description} - Success")
            return True
        else:
            print(f"{description} - Failed")
            return False
    except Exception as e:
        print(f"{description} - Error: {e}")
        return False

def main():
    print("Starting Day 1 Setup: Basic Configuration")
    print("-"*50)


    if not Path("requirements.txt").exits():
        print("Run this script from the project root")
        sys.exit(1)

    if not Path("venv").exits():
        success = run_command("python -m venv venv","Creating virtual environment")
        if not success:
            sys.exit(1)

    else:
        print("Virtual environment already created")


    if os.name == "nt": #Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv/Scripts/pip"
        python_cmd = "venv/bin/python"

    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"

    success = run_command(f"{pip_cmd}","install -r requirements.txt","installing dependencies")
    if not success:
        sys.exit(1)

    directories = ["data/database","data/logs","data/reports","app"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Creating directory {directory}")



    if not Path(".env").exists():
        if Path(".env.example").exists():
            with open(".env.example","r") as example:
                with open(Path(".env.example"),"w") as env:
                    env.write(example.read())
            print("Created .env file from .env.example")
        else:
            print("No .env file found")
    else:
        print(".env file already exists")

    print("\n Testiing configuration")
    try:

        sys.path.insert(0,str(Path.cwd()))
        from app.config import settings


        print("Configuration loaded successfully")
        print(f"   - Database URL: {settings.DATABASE_URL}")
        print(f"   - Debug mode: {settings.DEBUG}")
        print(f"   - Stripe configured: {bool(settings.STRIPE_SECRET_KEY)}")

    except ImportError as e:
        print(f" Configuration test failed: {e}")
        print("   This might be normal if other app files aren't created yet")

print("\n Day 1 Setup Complete!")
print("\n Next steps:")
print("1. Update .env file with your Stripe test keys")
print("2. Run: source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
print("3. Next time: Create database models and API structure")

if __name__ == "__main__":
    main()


