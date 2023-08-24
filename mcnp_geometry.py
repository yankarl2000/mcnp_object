import re
EPS = 1e-7
MNEMONICS = ["P", "PX", "PY", "PZ", "SO", "S", "SX", "SY", "SZ",
            "C/X", "C/Y", "C/Z", "CX", "CY", "CZ",
            "K/X", "K/Y", "K/Z", "KX", "KY", "KZ",
            "SQ", "GQ", "TX", "TY", "TZ",
            "BOX", "RPP", "SPH", "RCC", "RHP",
            "HEX", "REC", "TRC", "ELL", "WED", "ARB"]

class Cell:
    def __init__(self, text):
        self.text = text
        description_block = True
        comment_block = False
        description_text = ''
        comment_text = ''
        parameter_text = ''
        for c in text:
            if c == '$': comment_block = True
            if comment_block and c == '\n': comment_block = False
            if c.isalpha() and not comment_block: 
                description_block = False
            if comment_block: comment_text += c
            elif description_block: description_text += c
            else: parameter_text += c
        self.description_text = description_text.rstrip()
        self.comment_text = comment_text.rstrip()
        self.parameter_text =  parameter_text.upper().rstrip()
        description_text_split = description_text.split()
        self.number = int(description_text_split[0])
        self.material_num = int(description_text_split[1])
        if self.material_num != 0:
            self.density = -float(description_text_split[2])
            surfaces_text = ' '.join(description_text_split[3:])
        else:
            self.density = None
            surfaces_text = ' '.join(description_text_split[2:])
        if "The outer cell" in comment_text: self.outer_cell = True
        else: self.outer_cell = False
        surfaces_num = surfaces_text.replace('(',' ').replace(')',
            ' ').replace(':',' ').replace('#',' ').split()
        self.surfaces_num = [int(num) for num in surfaces_num]
        self.parameters = self.get_parameters()
    def get_parameters(self):
        parameters = dict.fromkeys(["IMP:N=", "IMP:P=", "IMP:E=",
            "FILL=", "U=", "TMP=", "VOL="])
        text_split = [self.parameter_text]
        for key in parameters.keys():
            for i in range(len(text_split)):
                part = text_split[i].partition(key)
                if part[1]:
                    text_split.pop(i)
                    if part[0]:
                        text_split.insert(i, part[0].strip())
                        text_split.insert(i+1, part[1].strip())
                        text_split.insert(i+2, part[2].strip())
                    else:
                        text_split.insert(i, part[1].strip())
                        text_split.insert(i+1, part[2].strip())
        for i in range(len(text_split)):
            if text_split[i] in parameters.keys():
                parameters[text_split[i]] = text_split[i+1]
        return parameters
    def __str__(self):
        c_list = self.description_text.split()
        cell_text = c_list[0]
        for c in c_list[1:]:
            if len(cell_text.split('\n')[-1])+len(c)+2<80:
                cell_text += ' ' + c
            else:
                line = '\n         ' + c
                while len(line)>79:
                    part = line[:79].rpartition(':')
                    cell_text += part[0]
                    line = '\n         ' + part[1] + part[2] + line[79:]
                cell_text += line
        cell_text += '\n         '
        for p in self.parameters:
            if self.parameters[p]:
                if len(cell_text.split('\n')[-1])+len(p+self.parameters[p])+2<80:
                    cell_text += ' ' + p+self.parameters[p]
                else:
                    cell_text += '\n         ' + p+self.parameters[p]
        return cell_text
    def replace(self, old_surf, new_surf):
        description_list = ['']
        number = True
        for c in self.description_text:
            if c.isdigit() and number:
                description_list[-1] += c
            elif c.isdigit():
                number = True
                description_list.append(c)
            elif number:
                number = False
                description_list.append(c)
            else:
                description_list[-1] += c
        if self.material_num: skip = 3
        else: skip = 2
        for i in range(skip*2,len(description_list)):
            if (description_list[i].isdigit() and
                (int(description_list[i]) == old_surf.number)):
                description_list[i] = str(new_surf.number)
        self.description_text = "".join(description_list)

'''
FIRST PART

class Surface
Surface.text - how it in .i file
Surface.move(dx, dy, dz) - moves surface
function load_surfaces return list of Surface objects

SECOND PART
mcnp equations of serfaces
constructor gets object surface with params
[number, type, param1, param2...]
method move change params to moved
method str return surface without number
'''
'''-------FIRST PART--------'''

class Surface:
    def __init__(self, text, log=False):
        self.text = text
        comment_block = False
        description_text = ''
        comment_text = ''
        for c in text:
            if c == '$': comment_block = True
            if comment_block and c == '\n': comment_block = False
            if comment_block: comment_text += c
            else: description_text += c
        description_text = description_text.replace('&', '')
        self.params = description_text.split()
        self.comment_text = comment_text
        if len(self.params) < 3: print("bad description")
        if self.params[0].startswith('*'):
            #print('find * at beginning')
            self.number = int(self.params[0][1:])
        else:
            self.number = int(self.params[0])
        self.mnemonic = self.params[1]
        if self.mnemonic == "P": self.equation = P(self, log)
        elif self.mnemonic == "PX": self.equation = PX(self, log)
        elif self.mnemonic == "PY": self.equation = PY(self, log)
        elif self.mnemonic == "PZ": self.equation = PZ(self, log)
        elif self.mnemonic == "SO": self.equation = SO(self, log)
        elif self.mnemonic == "S": self.equation = S(self, log)
        elif self.mnemonic == "SX": self.equation = SX(self, log)
        elif self.mnemonic == "SY": self.equation = SY(self, log)
        elif self.mnemonic == "SZ": self.equation = SZ(self, log)
        elif self.mnemonic == "C/X": self.equation = CpX(self, log)
        elif self.mnemonic == "C/Y": self.equation = CpY(self, log)
        elif self.mnemonic == "C/Z": self.equation = CpZ(self, log)
        elif self.mnemonic == "CX": self.equation = CX(self, log)
        elif self.mnemonic == "CY": self.equation = CY(self, log)
        elif self.mnemonic == "CZ": self.equation = CZ(self, log)
        elif self.mnemonic == "K/X": self.equation = KpX(self, log)
        elif self.mnemonic == "K/Y": self.equation = KpY(self, log)
        elif self.mnemonic == "K/Z": self.equation = KpZ(self, log)
        elif self.mnemonic == "KX": self.equation = KX(self, log)
        elif self.mnemonic == "KY": self.equation = KY(self, log)
        elif self.mnemonic == "KZ": self.equation = KZ(self, log)
        elif self.mnemonic == "SQ": self.equation = SQ(self, log)
        elif self.mnemonic == "GQ": self.equation = GQ(self, log)
        elif self.mnemonic == "TX": self.equation = TX(self, log)
        elif self.mnemonic == "TY": self.equation = TY(self, log)
        elif self.mnemonic == "TZ": self.equation = TZ(self, log)
        elif self.mnemonic == "BOX": self.equation = BOX(self, log)
        elif self.mnemonic == "RPP": self.equation = RPP(self, log)
        elif self.mnemonic == "SPH": self.equation = SPH(self, log)
        elif self.mnemonic == "RCC": self.equation = RCC(self, log)
        elif self.mnemonic == "RHP": self.equation = RHP(self, log)
        elif self.mnemonic == "HEX": self.equation = RHP(self, log)
        elif self.mnemonic == "REC": self.equation = REC(self, log)
        elif self.mnemonic == "TRC": self.equation = TRC(self, log)
        elif self.mnemonic == "ELL": self.equation = ELL(self, log)
        elif self.mnemonic == "WED": self.equation = WED(self, log)
        elif self.mnemonic == "ARB": self.equation = ARB(self, log)
        else: print("not found such surface mnemonic")
    def move(self, dx, dy, dz):
        self.equation.move(dx, dy, dz)
    def similar_with(self, surface):
        if self.mnemonic == surface.mnemonic:
            return self.equation.similar_with(surface.equation)
        else:
            return False
    def __str__(self):
        s_list = [str(self.number), self.mnemonic] + self.equation.str_params()
        s_string = s_list[0]
        for s in s_list[1:]:
            if len(s_string.split('\n')[-1])+len(s)+2<80:
                s_string += ' ' + s
            else:
                s_string += '\n         ' + s
        return s_string

'''------SECOND PART--------'''

def similar_vector(x1, y1, z1, x2, y2, z2):
    norm_x1 = x1/(x1**2 + y1**2 + z1**2)**0.5
    norm_y1 = y1/(x1**2 + y1**2 + z1**2)**0.5
    norm_z1 = z1/(x1**2 + y1**2 + z1**2)**0.5
    norm_x2 = x2/(x2**2 + y2**2 + z2**2)**0.5
    norm_y2 = y2/(x2**2 + y2**2 + z2**2)**0.5
    norm_z2 = z2/(x2**2 + y2**2 + z2**2)**0.5
    return (abs(norm_x1-norm_x2) < EPS and
            abs(norm_y1-norm_y2) < EPS and
            abs(norm_z1-norm_z2) < EPS)

# General plane
# Ax + By + Cz - D = 0
# № P A B C D
class P:
    def __init__(self, surface, log = False):
        if log: print("№ {} - General plane".format(surface.params[0]))
        (self.A, self.B, self.C,
            self.D) = tuple([float(p) for p in surface.params[2:6]])
    def move(self, dx, dy, dz):
        self.D += self.A*dx + self.B*dy + self.C*dz
    def str_params(self):
        return [str(p) for p in [self.A, self.B,
            self.C, self.D]]
    def similar_with(self, equation):
        return (abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS and
            abs(self.D-equation.D) < EPS)

# Normal to X-axis plane
# x - D = 0
# № P D
class PX:
    def __init__(self, surface, log = False):
        if log: print("№ {} - Normal to X-axis plane".format(surface.params[0]))
        self.D = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.D += dx
    def str_params(self):
        return [str(self.D)]
    def similar_with(self, equation):
        return abs(self.D-equation.D) < EPS

# Normal to Y-axis plane
# y - D = 0
# № P D
class PY:
    def __init__(self, surface, log = False):
        if log: print("№ {} - Normal to Y-axis plane".format(surface.params[0]))
        self.D = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.D += dy
    def str_params(self):
        return [str(self.D)]
    def similar_with(self, equation):
        return abs(self.D-equation.D) < EPS

# Normal to Z-axis plane
# z - D = 0
# № P D
class PZ:
    def __init__(self, surface, log = False):
        if log: print("№ {} - Normal to Z-axis plane".format(surface.params[0]))
        self.D = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.D += dz
    def str_params(self):
        return [str(self.D)]
    def similar_with(self, equation):
        return abs(self.D-equation.D) < EPS

# Centered at Origin sphere
# x^2 + y^2 + z^2 - R^2 = 0
# № SO R
class SO:
    def __init__(self, surface, log = False):
        self.surface = surface
        if log: print("№ {} - Centred at Origin sphere".format(surface.params[0]))
        self.R = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 = dy
        self.z0 = dz
        if self.x0 >= EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.R]
            self.surface.equation = SX(self.surface)
        elif self.x0 < EPS and self.y0 >= EPS and self.z0 < EPS:
            self.surface.mnemonic = "SY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.R]
            self.surface.equation = SY(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 >= EPS:
            self.surface.mnemonic = "SZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.z0, self.R]
            self.surface.equation = SZ(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 < EPS:
            pass
        else:
            self.surface.mnemonic = "S"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.R]
            self.surface.equation = S(self.surface)
    def str_params(self):
        return [str(self.R)]
    def similar_with(self, equation):
        return abs(self.R-equation.R) < EPS

# General sphere
# (x-x0)^2 + (y-y0)^2 + (z-z0)^2 - R^2 = 0
# № S x0 y0 z0 R
class S:
    def __init__(self, surface, log = False):
        if log: print("№ {} - General sphere".format(surface.params[0]))
        (self.x0, self.y0, self.z0,
            self.R) = tuple([float(p) for p in surface.params[2:6]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
        if self.x0 >= EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.R]
            self.surface.equation = SX(self.surface)
        elif self.x0 < EPS and self.y0 >= EPS and self.z0 < EPS:
            self.surface.mnemonic = "SY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.R]
            self.surface.equation = SY(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 >= EPS:
            self.surface.mnemonic = "SZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.z0, self.R]
            self.surface.equation = SZ(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SO"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = SO(self.surface)
    def str_params(self):
        return [str(p) for p in [self.x0, self.y0, 
            self.z0, self.R]]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.R-equation.R) < EPS)
            
# Centered on X-axis sphere
# (x-x0)^2 + y^2 + z^2 - R^2 = 0
# № SX x0 R
class SX:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Centered on X-axis sphere".format(surface.params[0]))
        self.x0 = float(surface.params[2])
        self.R = float(surface.params[3])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 = dy
        self.z0 = dz
        if self.x0 >= EPS and self.y0 < EPS and self.z0 < EPS:
            pass
        elif self.x0 < EPS and self.y0 >= EPS and self.z0 < EPS:
            self.surface.mnemonic = "SY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.R]
            self.surface.equation = SY(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 >= EPS:
            self.surface.mnemonic = "SZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.z0, self.R]
            self.surface.equation = SZ(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SO"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = SO(self.surface)
        else:
            self.surface.mnemonic = "S"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.R]
            self.surface.equation = S(self.surface)
    def str_params(self):
        return [str(self.x0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.R-equation.R) < EPS)

# Centered on Y-axis sphere
# x^2 + (y-y0)^2 + z^2 - R^2 = 0
# № SY y0 R
class SY:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Centered on Y-axis sphere".format(surface.params[0]))
        self.y0 = float(surface.params[2])
        self.R = float(surface.params[3])
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 += dy
        self.z0 = dz
        if self.x0 >= EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.R]
            self.surface.equation = SX(self.surface)
        elif self.x0 < EPS and self.y0 >= EPS and self.z0 < EPS:
            pass
        elif self.x0 < EPS and self.y0 < EPS and self.z0 >= EPS:
            self.surface.mnemonic = "SZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.z0, self.R]
            self.surface.equation = SZ(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SO"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = SO(self.surface)
        else:
            self.surface.mnemonic = "S"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.R]
            self.surface.equation = S(self.surface)
    def str_params(self):
        return [str(self.y0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.y0-equation.y0) < EPS and
            abs(self.R-equation.R) < EPS)

# Centered on Z-axis sphere
# x^2 + y^2 + (z-z0)^2 - R^2 = 0
# № SZ z0 R
class SZ:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Centered on Z-axis sphere".format(surface.params[0]))
        self.z0 = float(surface.params[2])
        self.R = float(surface.params[3])
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 = dy
        self.z0 += dz
        if self.x0 >= EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.R]
            self.surface.equation = SX(self.surface)
        elif self.x0 < EPS and self.y0 >= EPS and self.z0 < EPS:
            self.surface.mnemonic = "SY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.R]
            self.surface.equation = SY(self.surface)
        elif self.x0 < EPS and self.y0 < EPS and self.z0 >= EPS:
            pass
        elif self.x0 < EPS and self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "SO"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = SO(self.surface)
        else:
            self.surface.mnemonic = "S"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.R]
            self.surface.equation = S(self.surface)
    def str_params(self):
        return [str(self.z0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.z0-equation.z0) < EPS and
            abs(self.R-equation.R) < EPS)

# Parallel to X-axis cylinder
# (y-y0)^2 + (z-z0)^2 - R^2 = 0
# № C/X y0 z0 R
class CpX:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to X-axis cylinder".format(surface.params[0]))
        (self.y0, self.z0,
            self.R) = tuple([float(p) for p in surface.params[2:5]])
    def move(self, dx, dy, dz):
        self.y0 += dy
        self.z0 += dz
        if self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "CX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = CX(self.surface)
    def str_params(self):
        return [str(self.y0), str(self.z0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.R-equation.R) < EPS)

# Parallel to Y-axis cylinder
# (x-x0)^2 + (z-z0)^2 - R^2 = 0
# № C/Y x0 z0 R
class CpY:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to Y-axis cylinder".format(surface.params[0]))
        (self.x0, self.z0,
            self.R) = tuple([float(p) for p in surface.params[2:5]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.z0 += dz
        if self.x0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "CY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = CY(self.surface)
    def str_params(self):
        return [str(self.x0), str(self.z0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.R-equation.R) < EPS)

# Parallel to Z-axis cylinder
# (x-x0)^2 + (y-y0)^2 - R^2 = 0
# № C/Z x0 y0 R
class CpZ:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to Z-axis cylinder".format(surface.params[0]))
        (self.x0, self.y0,
            self.R) = tuple([float(p) for p in surface.params[2:5]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        if self.x0 < EPS and self.y0 < EPS:
            self.surface.mnemonic = "CZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.R]
            self.surface.equation = CZ(self.surface)
    def str_params(self):
        return [str(self.x0), str(self.y0), str(self.R)]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.R-equation.R) < EPS)

# On X-axis cylinder
# y^2 + z^2 - R^2 = 0
# № CX R
class CX:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On X-axis cylinder".format(surface.params[0]))
        self.R = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.y0 = dy
        self.z0 = dz
        if self.y0 >= EPS or self.z0 >= EPS:
            self.surface.mnemonic = "CpX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.z0, self.R]
            self.surface.equation = CpX(self.surface)
    def str_params(self):
        return [str(self.R)]
    def similar_with(self, equation):
        return abs(self.R-equation.R) < EPS

# On Y-axis cylinder
# x^2 + z^2 - R^2 = 0
# № CY  R
class CY:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On Y-axis cylinder".format(surface.params[0]))
        self.R = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.z0 = dz
        if self.x0 >= EPS or self.z0 >= EPS:
            self.surface.mnemonic = "CpY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.z0, self.R]
            self.surface.equation = CpY(self.surface)
    def str_params(self):
        return [str(self.R)]
    def similar_with(self, equation):
        return abs(self.R-equation.R) < EPS

# On Z-axis cylinder
# x^2 + y^2 - R^2 = 0
# № CZ R
class CZ:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On Z-axis cylinder".format(surface.params[0]))
        self.R = float(surface.params[2])
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 = dy
        if self.x0 >= EPS or self.y0 >= EPS:
            self.surface.mnemonic = "CpZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.R]
            self.surface.equation = CpZ(self.surface)
    def str_params(self):
        return [str(self.R)]
    def similar_with(self, equation):
        return abs(self.R-equation.R) < EPS

# Parallel to X-axis cone
# sqrt((y-y0)^2 + (z-z0)^2) - t((x-x0))
# № K/X x0 y0 z0 t^2 p
# p = +1 - x>x0 => increase R
# p = -1 - x<x0 => increase R
class KpX:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to X-axis cone".format(surface.params[0]))
        (self.x0, self.y0, self.z0,
            self.t_2) = tuple([float(p) for p in surface.params[2:6]])
        if len(surface.params)>=7: self.p = float(surface.params[6])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
        if self.y0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "KX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KX(self.surface)
    def str_params(self):
        p_list = [self.x0, self.y0, 
                self.z0, self.t_2]
        if self.p: p_list.append(self.p)
        return [str(p) for p in p_list]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# Parallel to Y-axis cone
# sqrt((x-x0)^2 + (z-z0)^2) - t((y-y0))
# № K/Y x0 y0 z0 t^2 p
# p = +1 - y>y0 => increase R
# p = -1 - y<y0 => increase R
class KpY:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to Y-axis cone".format(surface.params[0]))
        (self.x0, self.y0, self.z0,
            self.t_2) = tuple([float(p) for p in surface.params[2:6]])
        if len(surface.params)>=7: self.p = float(surface.params[6])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
        if self.x0 < EPS and self.z0 < EPS:
            self.surface.mnemonic = "KY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.y0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KY(self.surface)
    def str_params(self):
        p_list = [self.x0, self.y0, 
                self.z0, self.t_2]
        if self.p: p_list.append(self.p)
        return [str(p) for p in p_list]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# Parallel to Z-axis cone
# sqrt((x-x0)^2 + (y-y0)^2) - t((z-z0))
# № K/Z x0 y0 z0 t^2 p
# p = +1 - z>z0 => increase R
# p = -1 - z<z0 => increase R
class KpZ:
    def __init__(self, surface, log=False):
        if log: print("№ {} - Parallel to Z-axis cone".format(surface.params[0]))
        (self.x0, self.y0, self.z0,
            self.t_2) = tuple([float(p) for p in surface.params[2:6]])
        if len(surface.params)>=7: self.p = float(surface.params[6])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
        if self.x0 < EPS and self.y0 < EPS:
            self.surface.mnemonic = "KZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.z0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KZ(self.surface)
    def str_params(self):
        p_list = [self.x0, self.y0, 
                self.z0, self.t_2]
        if self.p: p_list.append(self.p)
        return [str(p) for p in p_list]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# On X-axis cone
# sqrt(y^2 + z^2) - t((x-x0))
# № KX x0 t^2 p
# p = +1 - x>x0 => increase R
# p = -1 - x<x0 => increase R
class KX:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On X-axis cone".format(surface.params[0]))
        self.x0 = float(surface.params[2])
        self.t_2 = float(surface.params[3])
        if len(surface.params)>=5: self.p = float(surface.params[4])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 = dy
        self.z0 = dz
        if self.y0 >= EPS or self.z0 >= EPS:
            self.surface.mnemonic = "KpX"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KpX(self.surface)
    def str_params(self):
        str_list = [str(self.x0), str(self.t_2)]
        if self.p: str_list.append(str(self.p))
        return str_list
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# On Y-axis cone
# sqrt(x^2 + z^2) - t((y-y0))
# № KY y0 t^2 p
# p = +1 - y>y0 => increase R
# p = -1 - y<y0 => increase R
class KY:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On Y-axis cone".format(surface.params[0]))
        self.y0 = float(surface.params[2])
        self.t_2 = float(surface.params[3])
        if len(surface.params)>=5: self.p = float(surface.params[4])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 += dy
        self.z0 = dz
        if self.x0 >= EPS or self.z0 >= EPS:
            self.surface.mnemonic = "KpY"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KpY(self.surface)
    def str_params(self):
        str_list = [str(self.y0), str(self.t_2)]
        if self.p: str_list.append(str(self.p))
        return str_list
    def similar_with(self, equation):
        return (abs(self.y0-equation.y0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# On Z-axis cone
# sqrt(x^2 + y^2) - t((z-z0))
# № KZ z0 t^2 p
# p = +1 - z>z0 => increase R
# p = -1 - z<z0 => increase R
class KZ:
    def __init__(self, surface, log=False):
        if log: print("№ {} - On Z-axis cone".format(surface.params[0]))
        self.z0 = float(surface.params[2])
        self.t_2 = float(surface.params[3])
        if len(surface.params)>=5: self.p = float(surface.params[4])
        else: self.p = 0
    def move(self, dx, dy, dz):
        self.x0 = dx
        self.y0 = dy
        self.z0 += dz
        if self.x0 >= EPS or self.y0 >= EPS:
            self.surface.mnemonic = "KpZ"
            self.surface.params = [self.surface.number, 
                self.surface.mnemonic, self.x0, self.y0, self.z0, self.t_2]
            if self.p: self.surface.params.append(self.p)
            self.surface.equation = KpZ(self.surface)
    def str_params(self):
        str_list = [str(self.z0), str(self.t_2)]
        if self.p: str_list.append(str(self.p))
        return str_list
    def similar_with(self, equation):
        return (abs(self.z0-equation.z0) < EPS and
            abs(self.t_2-equation.t_2) < EPS and
            self.p == equation.p)

# Axis parallel to X-, Y-, or Z-axis ellipsoid, hyperboloid, parabaloid
# A(x-x0)^2 + B(y-y0)^2 + C(z-z0)^2 + 2D(x-x0) + 2E(y-y0) + 2F(z-z0) + G = 0
# № SQ A B C D E F G x0 y0 z0
class SQ:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Axis parallel to X-, Y-, or Z-axis ellipsoid, 
                    hyperboloid, parabaloid'''.format(surface.params[0]))
        (self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.x0,
            self.y0, self.z0) = tuple([float(p) for p in surface.params[2:12]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
    def str_params(self):
        return [str(p) for p in [self.A, self.B, self.C,
            self.D, self.E, self.F, self.G, 
            self.x0, self.y0, self.z0]]
    def similar_with(self, equation):
        return (abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS and
            abs(self.D-equation.D) < EPS and
            abs(self.E-equation.E) < EPS and
            abs(self.F-equation.F) < EPS and
            abs(self.G-equation.G) < EPS and
            abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS)

# Axes not parallel to X-, Y-, or Z-axis cylinder, cone, 
# ellipsoid, hyperboloid, parabaloid
# Ax^2 + By^2 + Cz^2 + Dxy + Eyz + Fzx + Gx + Hy + Jz + K = 0
# № GQ A B C D E F G H J K
class GQ:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Axes not parallel to X-, Y-, or Z-axis 
        cylinder, cone, ellipsoid, hyperboloid, parabaloid'''.format(surface.params[0]))
        (self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H,
            self.J, self.K) = tuple([float(p) for p in surface.params[2:12]])
    def move(self, dx, dy, dz):
        self.G -= 2*self.A*dx + self.D*dy + self.F*dz
        self.H -= 2*self.B*dy + self.D*dx + self.E*dz
        self.J -= 2*self.C*dz + self.E*dy + self.F*dx
        self.K += self.A*dx**2 + self.B*dy**2 + self.C*dz**2
        self.K += self.D*dx*dy + self.E*dy*dz + self.F*dz*dx
        self.K -= self.G*dx + self.H*dy + self.J*dz
    def str_params(self):
        return [str(p) for p in [self.A, self.B, self.C, 
            self.D, self.E, self.F, self.G, 
            self.H, self.J, self.K]]
    def similar_with(self, equation):
        return (abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS and
            abs(self.D-equation.D) < EPS and
            abs(self.E-equation.E) < EPS and
            abs(self.F-equation.F) < EPS and
            abs(self.G-equation.G) < EPS and
            abs(self.H-equation.H) < EPS and
            abs(self.J-equation.J) < EPS and
            abs(self.K-equation.K) < EPS)

# Axis is parallel to X-axis elliptical or circular torus
# (x-x0)^2/B^2 + (sqrt((y-y0)^2 + (z-z0)^2) - A)^2/C^2 - 1 = 0
# № TX x0 y0 z0 A B C
class TX:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Axis is parallel to X-axis elliptical
                        or circular torus'''.format(surface.params[0]))
        (self.x0, self.y0, self.z0, self.A, self.B,
            self.C) = tuple([float(p) for p in surface.params[2:8]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
    def str_params(self):
        return [str(p) for p in [self.x0, self.y0, self.z0, 
            self.A, self.B, self.C]]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS)

# Axis is parallel to Y-axis elliptical or circular torus
# (y-y0)^2/B^2 + (sqrt((x-x0)^2 + (z-z0)^2) - A)^2/C^2 - 1 = 0
# № TY x0 y0 z0 A B C
class TY:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Axis is parallel to Y-axis elliptical
                        or circular torus'''.format(surface.params[0]))
        (self.x0, self.y0, self.z0, self.A, self.B,
            self.C) = tuple([float(p) for p in surface.params[2:8]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
    def str_params(self):
        return [str(p) for p in [self.x0, self.y0, self.z0, 
            self.A, self.B, self.C]]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS)

# Axis is parallel to Z-axis elliptical or circular torus
# (z-z0)^2/B^2 + (sqrt((x-x0)^2 + (y-y0)^2) - A)^2/C^2 - 1 = 0
# № TZ x0 y0 z0 A B C
class TZ:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Axis is parallel to Z-axis elliptical
                        or circular torus'''.format(surface.params[0]))
        (self.x0, self.y0, self.z0, self.A, self.B,
            self.C) = tuple([float(p) for p in surface.params[2:8]])
    def move(self, dx, dy, dz):
        self.x0 += dx
        self.y0 += dy
        self.z0 += dz
    def str_params(self):
        return [str(p) for p in [self.x0, self.y0, self.z0, 
            self.A, self.B, self.C]]
    def similar_with(self, equation):
        return (abs(self.x0-equation.x0) < EPS and
            abs(self.y0-equation.y0) < EPS and
            abs(self.z0-equation.z0) < EPS and
            abs(self.A-equation.A) < EPS and
            abs(self.B-equation.B) < EPS and
            abs(self.C-equation.C) < EPS)

# Arbitrarily oriented ortogonal box
# № BOX Vx Vy Vz A1x A1y A1z A2x A2y A2z A3x A3y A3z
class BOX:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Arbitrarily oriented 
                        ortogonal box'''.format(surface.params[0]))
        self.Vx = float(surface.params[2])
        self.Vy = float(surface.params[3])
        self.Vz = float(surface.params[4])
        self.A1x = float(surface.params[5])
        self.A1y = float(surface.params[6])
        self.A1z = float(surface.params[7])
        self.A2x = float(surface.params[8])
        self.A2y = float(surface.params[9])
        self.A2z = float(surface.params[10])
        self.A3x = float(surface.params[11])
        self.A3y = float(surface.params[12])
        self.A3z = float(surface.params[13])
        (self.Vx, self.Vy, self.Vz, self.A1x, self.A1y, self.A1z,
            self.A2x, self.A2y, self.A2z, self.A3x, self.A3y,
            self.A3z) = tuple([float(p) for p in surface.params[2:14]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, self.Vz, 
            self.A1x, self.A1y, self.A1z, 
            self.A2x, self.A2y, self.A2z, 
            self.A3x, self.A3y, self.A3z]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            similar_vector(self.A1x, self.A1y, self.A1z,
                equation.A1x,equation.A1y,equation.A1z) and
            similar_vector(self.A2x, self.A2y, self.A2z,
                equation.A2x,equation.A2y,equation.A2z) and
            similar_vector(self.A3x, self.A3y, self.A3z,
                equation.A3x,equation.A3y,equation.A3z))

# Rectangular Parallelepiped
# № RPP Xmin Xmax Ymin Ymax Zmin Zmax
class RPP:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Rectangular 
                        Parallelepiped'''.format(surface.params[0]))
        (self.Xmin, self.Xmax, self.Ymin, self.Ymax, self.Zmin,
            self.Zmax) = tuple([float(p) for p in surface.params[2:8]])
    def move(self, dx, dy, dz):
        self.Xmin += dx
        self.Ymin += dy
        self.Zmin += dz
        self.Xmax += dx
        self.Ymax += dy
        self.Zmax += dz
    def str_params(self):
        return [str(p) for p in [self.Xmin, self.Xmax, 
            self.Ymin, self.Ymax, 
            self.Zmin, self.Zmax]]
    def similar_with(self, equation):
        return (abs(self.Xmin-equation.Xmin) < EPS and
            abs(self.Ymin-equation.Ymin) < EPS and
            abs(self.Zmin-equation.Zmin) < EPS and
            abs(self.Xmax-equation.Xmax) < EPS and
            abs(self.Ymax-equation.Ymax) < EPS and
            abs(self.Zmax-equation.Zmax) < EPS)

# Sphere
# № SPH Vx Vy Vz R
class SPH:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Sphere'''.format(surface.params[0]))
        self.Vx = float(surface.params[2])
        self.Vy = float(surface.params[3])
        self.Vz = float(surface.params[4])
        self.R = float(surface.params[5])
        (self.Vx, self.Vy, self.Vz,
            self.R) = tuple([float(p) for p in surface.params[2:6]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, 
            self.Vz, self.R]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            abs(self.R-equation.r) < EPS)

# Right Circular Cylinder
# № RCC Vx Vy Vz Hx Hy Hz R
class RCC:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Right Circular 
                        Cylinder'''.format(surface.params[0]))
        self.Vx = float(surface.params[2])
        self.Vy = float(surface.params[3])
        self.Vz = float(surface.params[4])
        self.Hx = float(surface.params[5])
        self.Hy = float(surface.params[6])
        self.Hz = float(surface.params[7])
        self.R = float(surface.params[8])
        (self.Vx, self.Vy, self.Vz, self.Hx, self.Hy, self.Hz,
            self.R) = tuple([float(p) for p in surface.params[2:9]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, self.Vz, 
            self.Hx, self.Hy, self.Hz, self.R]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            similar_vector(self.Hx, self.Hy, self.Hz,
                equation.Hx,equation.Hy,equation.Hz) and
            abs(self.R-equation.R) < EPS)

# Right Hexogonal Prism
# № RHP(HEX) v1 v2 v3 h1 h2 h3 r1 r2 r3 s1 s2 s3 t1 t2 t3
class RHP:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Right Hexogonal Prism'''.format(surface.params[0]))
        (self.v1, self.v2, self.v3, self.h1, self.h2, self.h3, self.r1,
            self.r2, self.r3, self.s1, self.s2, self.s3, self.t1, self.t2, 
            self.t3) = tuple([float(p) for p in surface.params[2:17]])
    def move(self, dx, dy, dz):
        self.v1 += dx
        self.v2 += dy
        self.v3 += dz
    def str_params(self):
        return [str(p) for p in [self.v1, self.v2, self.v3, 
            self.h1, self.h2, self.h3, 
            self.r1, self.r2, self.r3,
            self.s1, self.s2, self.s3,
            self.t1, self.t2, self.t3]]
    def similar_with(self, equation):
        return (abs(self.v1-equation.v1) < EPS and
            abs(self.v2-equation.v2) < EPS and
            abs(self.v3-equation.v3) < EPS and
            similar_vector(self.h1, self.h2, self.h3,
                equation.h1,equation.h2,equation.h3) and
            similar_vector(self.r1, self.r2, self.r3,
                equation.r1,equation.r2,equation.r3) and
            similar_vector(self.s1, self.s2, self.s3,
                equation.s1,equation.s2,equation.s3) and
            similar_vector(self.t1, self.t2, self.t3,
                equation.t1,equation.t2,equation.t3))

# Right Elliptical Cylinder
# № REC Vx Vy Vz Hx Hy Hz V1x V1y V1z V2x V2y V2z
class REC:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Right Elliptical
                        Cylinder'''.format(surface.params[0]))
        (self.Vx, self.Vy, self.Vz, self.Hx, self.Hy, self.Hz,
            self.V1x, self.V1y, self.V1z, self.V2x, self.V2y,
            self.V2z) = tuple([float(p) for p in surface.params[2:14]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, self.Vz, 
            self.Hx, self.Hy, self.Hz, 
            self.V1x, self.V1y, self.V1z, 
            self.V2x, self.V2y, self.V2z]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            similar_vector(self.Hx, self.Hy, self.Hz,
                equation.Hx,equation.Hy,equation.Hz) and
            similar_vector(self.V1x, self.V1y, self.V1z,
                equation.V1x,equation.V1y,equation.V1z) and
            similar_vector(self.V2x, self.V2y, self.V2z,
                equation.V2x,equation.V2y,equation.V2z))

# Truncated Right-angle Cone
# № TRC Vx Vy Vz Hx Hy Hz R1 R2
class TRC:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Truncated Right-angle
                        Cone'''.format(surface.params[0]))
        (self.Vx, self.Vy, self.Vz, self.Hx, self.Hy, self.Hz,
            self.R1, self.R2) = tuple([float(p) for p in surface.params[2:10]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, self.Vz, 
            self.Hx, self.Hy, self.Hz, self.R1, self.R2]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            similar_vector(self.Hx, self.Hy, self.Hz,
                equation.Hx,equation.Hy,equation.Hz) and
            abs(self.R1-equation.R1) < EPS and
            abs(self.R2-equation.R2) < EPS)

# ELLipsoids
# № ELL V1x V1y V1z V2x V2y V2z Rm
class ELL:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - ELLipsoids'''.format(surface.params[0]))
        (self.V1x, self.V1y, self.V1z, self.V2x, self.V2y, self.V2z,
            self.Rm) = tuple([float(p) for p in surface.params[2:9]])
    def move(self, dx, dy, dz):
        self.V1x += dx
        self.V1y += dy
        self.V1z += dz
        self.V2x += dx
        self.V2y += dy
        self.V2z += dz
    def str_params(self):
        return [str(p) for p in [self.V1x, self.V1y, self.V1z, 
            self.V2x, self.V2y, self.V2z, self.Rm]]
    def similar_with(self, equation):
        return (abs(self.V1x-equation.V1x) < EPS and
            abs(self.V1y-equation.V1y) < EPS and
            abs(self.V1z-equation.V1z) < EPS and
            abs(self.V2x-equation.V2x) < EPS and
            abs(self.V2y-equation.V2y) < EPS and
            abs(self.V2z-equation.V2z) < EPS and
            abs(self.Rm-equation.Rm) < EPS)

# Wedge
# № WED Vx Vy Vz V1x V1y V1z V2x V2y V2z V3x V3y V3z
class WED:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - Wedge'''.format(surface.params[0]))
        (self.Vx, self.Vy, self.Vz, self.V1x, self.V1y, self.V1z,
            self.V2x, self.V2y, self.V2z, self.V3x, self.V3y,
            self.V3z) = tuple([float(p) for p in surface.params[2:14]])
    def move(self, dx, dy, dz):
        self.Vx += dx
        self.Vy += dy
        self.Vz += dz
    def str_params(self):
        return [str(p) for p in [self.Vx, self.Vy, self.Vz, 
            self.V1x, self.V1y, self.V1z,
            self.V2x, self.V2y, self.V2z,
            self.V3x, self.V3y, self.V3z]]
    def similar_with(self, equation):
        return (abs(self.Vx-equation.Vx) < EPS and
            abs(self.Vy-equation.Vy) < EPS and
            abs(self.Vz-equation.Vz) < EPS and
            similar_vector(self.V1x, self.V1y, self.V1z,
                equation.V1x,equation.V1y,equation.V1z) and
            similar_vector(self.V2x, self.V2y, self.V2z,
                equation.V2x,equation.V2y,equation.V2z) and
            similar_vector(self.V3x, self.V3y, self.V3z,
                equation.V3x,equation.V3y,equation.V3z))

# ARBitrary polyhedron
# № ARB ax ay az bx by bz cx cy cz ... hx by hz N1 N2 N3 N4 N5 N6
class ARB:
    def __init__(self, surface, log=False):
        if log: print('''№ {} - ARBitrary polyhedron'''.format(surface.params[0]))
        (self.ax, self.ay, self.az, self.bx, self.by, self.bz,
            self.cx, self.cy, self.cz, self.dx, self.dy, self.dz,
            self.ex, self.ey, self.ez, self.fx, self.fy, self.fz,
            self.gx, self.gy, self.gz, self.hx, self.hy, self.hz,
            self.N1, self.N2, self.N3, self.N4, self.N5,
            self.N6) = tuple([float(p) for p in surface.params[2:32]])
    def move(self, dx, dy, dz):
        self.ax+=dx; self.ay+=dy; self.az+=dz
        self.bx+=dx; self.by+=dy; self.dz+=dz
        self.cx+=dx; self.cy+=dy; self.cz+=dz
        self.dx+=dx; self.dy+=dy; self.dz+=dz
        self.ex+=dx; self.ey+=dy; self.ez+=dz
        self.fx+=dx; self.fy+=dy; self.fz+=dz
        self.gx+=dx; self.gy+=dy; self.gz+=dz
        self.hx+=dx; self.hy+=dy; self.hz+=dz
    def str_params(self):
        return [str(p) for p in [
            self.ax, self.ay, self.az, self.bx, self.by, self.bz,
            self.cx, self.cy, self.cz, self.dx, self.dy, self.dz,
            self.ex, self.ey, self.ez, self.fx, self.fy, self.fz,
            self.gx, self.gy, self.gz, self.hx, self.hy, self.hz,
            self.N1, self.N2, self.N3, self.N4, self.N5, self.N6]]
    def similar_with(self, equation):
        return (abs(self.ax-equation.ax) < EPS and
            abs(self.ay-equation.ay) < EPS and
            abs(self.az-equation.az) < EPS and
            abs(self.bx-equation.bx) < EPS and
            abs(self.by-equation.by) < EPS and
            abs(self.bz-equation.bz) < EPS and
            abs(self.cx-equation.cx) < EPS and
            abs(self.cy-equation.cy) < EPS and
            abs(self.cz-equation.cz) < EPS and
            abs(self.dx-equation.dx) < EPS and
            abs(self.dy-equation.dy) < EPS and
            abs(self.dz-equation.dz) < EPS and
            abs(self.ex-equation.ex) < EPS and
            abs(self.ey-equation.ey) < EPS and
            abs(self.ez-equation.ez) < EPS and
            abs(self.fx-equation.fx) < EPS and
            abs(self.fy-equation.fy) < EPS and
            abs(self.fz-equation.fz) < EPS and
            abs(self.gx-equation.gx) < EPS and
            abs(self.gy-equation.gy) < EPS and
            abs(self.gz-equation.gz) < EPS and
            abs(self.hx-equation.hx) < EPS and
            abs(self.hy-equation.hy) < EPS and
            abs(self.hz-equation.hz) < EPS and
            abs(self.N1-equation.N1) < EPS and
            abs(self.N2-equation.N2) < EPS and
            abs(self.N3-equation.N3) < EPS and
            abs(self.N4-equation.N4) < EPS and
            abs(self.N5-equation.N5) < EPS and
            abs(self.N6-equation.N6) < EPS)