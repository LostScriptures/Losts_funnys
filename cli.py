from inspect import signature
from types import MethodType
from pathlib import Path
import importlib
import traceback
import modules
import pkgutil
import cmd
import sys
import gc

PROJECT_ROOT = Path(__file__).parent

class losts_funnys(cmd.Cmd):
    intro = 'Losts funnys CLI. Type ? or help <topic> for help\n'
    prompt = '>> '

    _module_map = {}

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

    def load_file(self, module_name, filename, mode = "r", encoding = None):
        full_path = PROJECT_ROOT / f"{module_name}/{filename}"
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with full_path.open(mode, encoding=encoding) as file:
            return file.read()
    
    def save_file(self, module_name, filename, data, mode = "w", encoding = None):
        full_path = PROJECT_ROOT / f"{module_name}/{filename}"
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with full_path.open(mode, encoding=encoding) as file:
            file.write(data)

def load_modules(cli, modules):
    """Loads the other modules"""
    print("--- Loading ---")
    # record original do_ commands on the class so we don't remove them on unload
    if not hasattr(cli, "_original_do_commands"):
        setattr(cli, "_original_do_commands", {n for n in dir(cli) if n.startswith("do_")})

    if hasattr(cli, "_module_map"):
        module_map = cli._module_map
    
    else:
        module_map = {}
        setattr(cli, "_module_map", module_map)

    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        functions = []
        loaded = False
        print(module_name, end="...")
        fullname = f'{modules.__name__}.{module_name}'

        try:
            if fullname in sys.modules:
                module = importlib.reload(sys.modules[fullname])
            else:
                module = importlib.import_module(fullname)

            # attach any do_ functions from the module to the CLI class
            for attr in dir(module):
                if attr.startswith("do_") or attr.startswith("help_"):
                    func = getattr(module, attr)
                    if not callable(func):
                        continue

                    parameters = signature(func).parameters

                    if len(parameters) > 0 and next(iter(parameters)) == "self":
                        func = MethodType(func, cli)

                    setattr(cli, attr, func)
                    functions.append(func)
                    loaded = True

            if loaded:
                print("OK")
            else:
                print("Nothing to load")
        except Exception as e:
            # print the error and the traceback so we can debug loading issues
            print(f"Failed to load {fullname}: {e}")
            traceback.print_exc()

        if functions != []:
            module_map.update({module_name: [f"{func.__name__}" for func in functions]})

def unload_modules(cli, modules):
    """Unloads the other modules"""
    print("--- Unloading ---")
    original = getattr(cli, "_original_do_commands", {n for n in dir(cli) if n.startswith("do_")})

    if not hasattr(cli, "_module_map"):
        raise AttributeError(f"No modules where loaded into {cli.__name__}")
    
    else:
        module_map = getattr(cli, "_module_map")

    unloaded_any = False
    # remove any do_ attributes that were not present originally
    for attr_name in list(dir(cli)):
        if attr_name.startswith('do_') or attr_name.startswith('help_') and attr_name not in original:
            try:
                delattr(cli, attr_name)
                unloaded_any = True
            except AttributeError:
                pass

    # also clear imported module cache for package modules so reload will pick up changes
    for name in list(sys.modules.keys()):
        if name.startswith(f'{modules.__name__}.'):
            del sys.modules[name]
            module_map.pop(f"{name}")

    if unloaded_any:
        print("Done")
    else:
        print("Nothing to unload")

    gc.collect()
            
if __name__ == '__main__':
    load_modules(losts_funnys, modules)

    try:
        losts_funnys().cmdloop()

    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)