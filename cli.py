import cmd
import importlib
import pkgutil
import sys
import traceback
import modules
class losts_funnys(cmd.Cmd):
    intro = 'Losts funnys CLI. Type ? or help <topic> for help\n'
    prompt = '> '

    # Command to exit the CLI
    def do_exit(self, _args):
        """Exit the CLI."""
        _ = _args
        print("Exiting...")
        return True
    
    def do_clear(self, _args):
        """Clear the screen."""
        _ = _args
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_reload(self, _args):
        """Reloads all modules"""
        _ = _args
        # operate on the class so commands are added/removed at the class level
        unload_modules(self.__class__, modules)
        load_modules(self.__class__, modules)

def load_modules(cli, modules):
    """Loads the other modules"""
    print("--- Loading ---")
    # record original do_ commands on the class so we don't remove them on unload
    if not hasattr(cli, "_original_do_commands"):
        setattr(cli, "_original_do_commands", {n for n in dir(cli) if n.startswith("do_")})
    if not hasattr(cli, "_loaded_module_names"):
        setattr(cli, "_loaded_module_names", set())

    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        print(module_name, end="...")
        fullname = f'{modules.__name__}.{module_name}'
        try:
            if fullname in sys.modules:
                module = importlib.reload(sys.modules[fullname])
            else:
                module = importlib.import_module(fullname)

            # attach any do_ functions from the module to the CLI class
            for attr in dir(module):
                if attr.startswith("do_"):
                    func = getattr(module, attr)
                    if callable(func):
                        setattr(cli, attr, func)

            # remember we loaded this module
            getattr(cli, "_loaded_module_names").add(module_name)
            print("OK")
        except Exception as e:
            # print the error and the traceback so we can debug loading issues
            print(f"Failed to load {fullname}: {e}")
            traceback.print_exc()

def unload_modules(cli, modules):
    """Unloads the other modules"""
    print("--- Unloading ---")
    original = getattr(cli, "_original_do_commands", {n for n in dir(cli) if n.startswith("do_")})

    unloaded_any = False
    # remove any do_ attributes that were not present originally
    for attr_name in list(dir(cli)):
        if attr_name.startswith('do_') and attr_name not in original:
            try:
                delattr(cli, attr_name)
                unloaded_any = True
            except AttributeError:
                pass

    # also clear imported module cache for package modules so reload will pick up changes
    for name in list(sys.modules.keys()):
        if name.startswith(f'{modules.__name__}.'):
            del sys.modules[name]

    # clear tracked loaded modules
    if hasattr(cli, "_loaded_module_names"):
        getattr(cli, "_loaded_module_names").clear()

    if unloaded_any:
        print("Done")
    else:
        print("Nothing to unload")
            
if __name__ == '__main__':
    load_modules(losts_funnys, modules)

    try:
        losts_funnys().cmdloop()

    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)