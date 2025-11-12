import cmd
import importlib
import pkgutil
import modules

class losts_funnys(cmd.Cmd):
    intro = 'Losts funnys CLI. Type ? or help <topic> for help\n'
    prompt = '> '

    # Command to exit the CLI
    def do_exit(self, args):
        """Exit the CLI."""
        print("Exiting...")
        return True
    
    def do_clear(self, args):
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_reload(self, args):
        """Reloads all modules"""
        unload_modules(self; modules) #TODO: Implement unload_modules
        load_modules(self, modules)

def load_modules(cli, modules):
    """Loads the other modules"""
    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        print(module_name, end="...")
        module = importlib.import_module(f'{modules.__name__}.{module_name}')
        
        loaded = False
        for attr_name in dir(module):
            if attr_name.startswith('do_'):
                setattr(cli, attr_name, getattr(module, attr_name))
                loaded = True
            
        if loaded:
            print("Done")
        else:
            print("Nothing to load")
            

if __name__ == '__main__':
    load_modules(losts_funnys, modules)
    try:
        losts_funnys().cmdloop()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)