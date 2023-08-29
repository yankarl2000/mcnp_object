import sys
import pathlib
import sys
from os.path import isfile

def print_help():
    print("usage: mcnp_parser [-h | --help]")
    print("These are common MCNP parser commands used in various situations:")
    print("See 'mcnp_parser help <command>' to read about a specific")
    exit()

if __name__ == '__main__':
    path_file = str(pathlib.Path().resolve())+ '\\'  # --------- ПУТЬ К ФАЙЛУ ------------
    print(path_file)
    if len(sys.argv) < 2:
        print_help()
    cmd = sys.argv[1]           # --------- ИМЯ ФАЙЛА ---------------
    if cmd == "--help" or cmd == "-h":
        print_help()
    elif cmd == "check_lost":
        print("the command is check_lost")
    elif cmd == "del_sim_surf":
        print("the command is del_sim_surf")
    elif cmd == "change_hist":
        print("the command is change_hist")
    else:
        print("unknown command")