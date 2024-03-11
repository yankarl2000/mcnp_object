'''
opt_surf file.i save only surfaces need to build cells of file.i
ЕСТЬ номера поверхностей в строках вида:
    ^номер ячейки номер материала плотность ....
    'пробелы'+ двоеточие/минус/скобка ....
НЕТ номеров поверхностей в строках вида:
    'пробелы'+ буква....
    'пробелы'+ $....
не забываем отсекать комментарии в конце строки $
'''
import os, sys, re

def get_nums(line):
    if line[0].isdigit():
        line = line.partition('$')[0]
    elif line.strip().startswith(tuple('():-0123456789')):
        line = line.partition('$')[0]
    elif line.strip().startswith('$') or line.strip()[0].isalpha():
        return set()
    else:
        print(f'strange line:\n{line}')
        return set()
    n = list()
    l = re.split(r'[():\s]+', line)
    if line[0].isdigit():
        for i in l[3:-1]:
            if i:
                n.append(abs(int(i)))
    else:
        for i in l:
            if i: n.append(abs(int(i)))
    return set(n)

def need_surf(line, nums, previous):
    if line[0].isdigit():
        return int(line.split()[0]) in nums
    else: return previous

def opt_surf(file_name):
    name = os.path.splitext(os.path.basename(file_name))[0]
    path = os.path.dirname(file_name)
    opt_name = os.path.join(path, f'opt_'+name+'.i')
    with open(file_name, 'r') as file, open(opt_name, 'w') as new_file:
        nums = set()
        cells = True
        surf = False
        previous = True
        c = 0 # total number of surfaces
        for line in file:
            if line == '\n':
                if cells: cells, surf = False, True
                else: surf = False
            if cells:
                nums = nums.union(get_nums(line))
                new_file.write(line)
            elif surf:
                if line[0].isdigit(): c+=1
                current = need_surf(line, nums, previous)
                if current:
                    new_file.write(line)
                previous = current
            else:
                new_file.write(line)
    return f'{len(nums)} of the {c} surfaces were saved'

if __name__ == "__main__":
    if len(sys.argv)<2:
        filename = input("enter filename: ")
    else:
        filename = sys.argv[1]
    message = opt_surf(filename)
    print(message)