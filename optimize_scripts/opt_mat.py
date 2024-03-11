'''
opt_mat file.i save only materials need to build cells of file.i
начало описание материала M...
конец описания материала строка начинающаяся не с пробела, не с C, не с $, не с M
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

def need_mat(line, nums, previous):
    if line.startswith(('m', 'M')):
        print(line.split()[0][1:])
        print(int(line.split()[0][1:]) in nums)
        return int(line.split()[0][1:]) in nums
    else: return previous

def opt_mat(file_name):
    name = os.path.splitext(os.path.basename(file_name))[0]
    path = os.path.dirname(file_name)
    opt_name = os.path.join(path, f'opt_'+name+'.i')
    with open(file_name, 'r') as file, open(opt_name, 'w') as new_file:
        nums = set()
        all_nums = []
        cells = True
        mat = False
        previous = True
        c = 0 # total number of materials
        for line in file:
            if line == '\n':
                if cells: cells = False
                else: mat = True;
            if cells:
                if line[0].isdigit():
                    nums.add(int(line.split()[1]))
                new_file.write(line)
            elif mat:
                if not (line[0] in ' Cc$mM\n'):
                    mat = False
                    if not previous: new_file.write(line)
                if line.startswith(('m', 'M')):
                    all_nums.append(line.split()[0])
                    c+=1
                current = need_mat(line, nums, previous)
                if current:
                    new_file.write(line)
                previous = current
            else:
                new_file.write(line)
    print(nums)
    print(all_nums)
    return f'{len(nums)} of the {c} materials were saved'

if __name__ == "__main__":
    if len(sys.argv)<2:
        filename = input("enter filename: ")
    else:
        filename = sys.argv[1]
    message = opt_mat(filename)
    print(message)