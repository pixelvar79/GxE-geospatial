import subprocess

# Define the name of the virtual environment
env_name = "polycreator"

# Define the path to the requirements.txt file
requirements_file = "requirements.txt"

# Create the virtual environment
subprocess.run(["conda", "create", "-n", env_name, "python=3.9", "--yes"])

# Activate the virtual environment
subprocess.run(["conda", "run", "-n", env_name, "conda", "activate", env_name])

# Install any missing packages
subprocess.run(["conda", "run", "-n", env_name, "conda", "install", "--file", requirements_file, "--yes"])

# Deactivate the virtual environment
subprocess.run(["conda", "run", "-n", env_name, "conda", "deactivate"])



