'''This script creates a basic directory structure for Hermius.'''

from pathlib import Path

# Base directory
base_dir = Path("")

# All the files and folders required
structure = [
    "app/__init__.py",
    "app/routes/__init__.py",
    "app/routes/main_routes.py",
    "app/routes/auth_routes.py",
    "app/routes/utility_routes.py",
    "app/sockets/__init__.py",
    "app/sockets/handlers.py",
    "app/database/__init__.py",
    "app/database/db.py",
    "app/utils/__init__.py",
    "app/utils/helpers.py",
    "app/templates/",
    "app/config.py",
    "main.py",
    "requirements.txt",
    ".env",
    "README.md",
    ".gitignore",
    "app/extensions.py"
]

#Create files and directories
for path_str in structure:
    path = base_dir / path_str
    if path.suffix:  # it's a file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    else:  #it's a directory
        path.mkdir(parents=True, exist_ok=True)

print("Project structure created successfully!")
