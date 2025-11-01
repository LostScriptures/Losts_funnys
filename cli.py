import cmd
import importlib
import pkgutil
import modules

class my_cli(cmd.Cmd):
    intro = 'Losttools CLI. Type ? or help <topic> for help\n'
    prompt = '> '

    # Command with argument
    def do_add(self, args):
        """Add two numbers. Usage: add <num1> <num2>"""
        try:
            num1, num2 = map(float, args.split())
            print(f"The sum is: {num1 + num2}")
        except ValueError:
            print("Please provide two numbers.")

    # Command to exit the CLI
    def do_exit(self, args):
        """Exit the CLI."""
        print("Exiting...")
        return True
    
    def do_clear(self, args):
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

def load_modules(cli, modules):
    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        module = importlib.import_module(f'{modules.__name__}.{module_name}')
        
        for attr_name in dir(module):
            if attr_name.startswith('do_'):
                setattr(cli, attr_name, getattr(module, attr_name))

if __name__ == '__main__':
    load_modules(my_cli, modules)

    my_cli().cmdloop()