# Basic color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'  # This resets the color back to default

def do_NO(self, args):
    """Annoying command that keeps printing DON'T PISS ME OFF"""
    while True:
        print(f"{RED}DON'T PISS ME OFF{RESET} ", end="")