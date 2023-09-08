'''
todo list:

причесать вывод find_sim_surf

добавить change_hist post pre processing
сделать скрипт замены всех совпадающих поверхностей и удаления лишних с сохранением в файл
с комментариями $ и C и без

попробовать внедрить скрипт объёмов
'''

'''
Usage: mcnp_parser [OPTIONS]

Options:
  --help  Show this message and exit.
'''
import sys
import pathlib
import sys
from os.path import isfile
from check_lost import check_lost
import mcnp_file as mf

def print_help():
    print('''usage: 'mcnp_parser [-h | --help]' to show this text''')
    print()
    print('''       'mcnp_parser check_lost file_name.o' to write text_for_SC.txt
        with script for ANSYS SpaceClaim, which making lost particle points
        use 'mcnp_parser check_lost dir_name' to get lost particles from multiply nodes
        dir_name contains dir_name_p1.o, dir_name_p2.o and others''')
    print()
    print('''       'mcnp_parser find_sim_surf file_name.i' searches for similar 
        surfaces and prints them''')
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
        if len(sys.argv)<3:
            print("empty filename")
            exit()
        check_lost(sys.argv[2])
    elif cmd == "find_sim_surf":
        if len(sys.argv)<3:
            print("empty filename")
            exit()
        i_file = mf.Ifile(sys.argv[2])
        i_file.find_similar_surfaces()
    elif cmd == "move_surf":
        if len(sys.argv)<3:
            print("empty filename")
            exit()
        i_file = mf.Ifile(sys.argv[2])
        i_file.surfaces[0].move(1,1,1)
    elif cmd == "del_sim_surf":
        print("the command is del_sim_surf")
    elif cmd == "change_hist":
        print("the command is change_hist")
    else:
        print("unknown command")