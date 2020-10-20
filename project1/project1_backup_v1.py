# Question：
# Memory
#   32-bit address
#   8-bit cell
# Register
#   32 32-bit
# Program
#   Add the number in memory address 0 and 1 to address 3
#   Load r1, #0
#   Load r2, #1
#   Add r3, r1, r2
#   Store r3, #3
class Word:
    """字类"""

    def __init__(self, num=None, num_str=None, num_list=None):
        """初始化函数"""
        if num is not None:
            self.data = self.dex2binl(num)
        elif num_str is not None:
            self.data = self.str2binl(num_str)
        elif num_list is not None:
            self.data = num_list
        else:
            self.data = self.dex2binl(0)

    def __str__(self):
        return self.data

    def str2binl(self, num_str):
        data = []
        i = 0
        for _ in range(4):
            data.append(num_str[i:i + 8])
            i += 8
        return data

    def get_bin_str(self):
        return ''.join(self.data)

    def dex2binl(self, num):
        """
        将10进制数转为2进制字符串
        :param num: 10进制数字
        :return: 2进制字符串
        """
        bin_s = ''.join(['0' for _ in range(31)])
        bin_s += bin(num)[2:]
        bin_s = bin_s[-32:]
        return [bin_s[:8], bin_s[8:16], bin_s[16:24], bin_s[-8:]]


class MyMemory:
    def __init__(self):
        self.memory = []
        self.extend_memory(20)

    def extend_memory(self, extend_size):
        """扩展内存数组"""
        for i in range(extend_size):
            self.memory.append(Word(0).data[0])

    def check_extend(self, index):
        """检查是否要扩展内存空间"""
        if index * 4 >= len(self.memory):
            self.extend_memory((index + 1) * 4 - len(self.memory))

    def get_data(self, index):
        """获取指定index的数据"""
        index *= 4
        return Word(num_list=[self.memory[index + i] for i in range(4)])

    def write_data(self, index, data: Word):
        self.check_extend(index)
        index *= 4
        """向指定index写入数据"""
        for i in range(len(data.data)):
            self.memory[index + i] = data.data[i]


class Instruction:
    """指令类"""

    def __init__(self, instruction_name, func):
        self.instruction_name = instruction_name
        self.func = func

    def execute(self, operands):
        self.func(operands)


class Instructions:
    """
    指令集类
    """

    def __init__(self, memory: MyMemory, register: list):
        self.instructions = []
        self.memory = memory
        self.register = register
        self.init_instruction_Load()
        self.init_instruction_Add()
        self.init_instruction_Store()

    def init_instruction_Load(self):
        """初始化Load指令"""

        def execute_func(operand: list):
            if len(operand) != 2:
                raise Exception(r"Destination operand error!")
            des, src = operand[0], operand[1]
            if not des.startswith('r'):
                raise Exception(r"Destination operand error!")
            else:
                des = int(des[1:])
            if not src.startswith('#'):
                raise Exception(r"Source operand error!")
            else:
                src = int(src[1:])
            self.register[des] = self.memory.get_data(src).get_bin_str()

        self.instructions.append(Instruction(instruction_name="Load", func=execute_func))

    def init_instruction_Add(self):
        """初始化Add指令"""

        def execute_func(operand: list):
            if len(operand) != 3:
                raise Exception(r"Destination operand error!")
            des, src1, src2 = operand[0], operand[1], operand[2]

            if not des.startswith('r'):
                raise Exception(r"Destination operand error!")
            else:
                des = int(des[1:])
            if (not src1.startswith('r')) or (not src2.startswith('r')):
                raise Exception(r"Source operand error!")
            else:
                src1 = int(src1[1:])
                src2 = int(src2[1:])
            self.register[des] = binary_add(self.register[src1], self.register[src2])

        def binary_add(a: str, b: str):
            a = a[::-1]
            b = b[::-1]
            f = False
            res = ''
            for i in range(32):
                if a[i] == '1' and b[i] == '1':
                    if f:
                        res += '1'
                    else:
                        res += '0'
                    f = True
                elif a[i] == '0' and b[i] == '0':
                    if f:
                        res += '1'
                    else:
                        res += '0'
                    f = False
                else:
                    if f:
                        res += '0'
                        f = True
                    else:
                        res += '1'
                        f = False
            return res[::-1]

        self.instructions.append(Instruction(instruction_name="Add", func=execute_func))

    def init_instruction_Store(self):
        """初始化Store指令"""

        def execute_func(operand: list):
            if len(operand) != 2:
                raise Exception(r"Destination operand error!")
            des, src = operand[1], operand[0]
            if not des.startswith('#'):
                raise Exception(r"Destination operand error!")
            else:
                des = int(des[1:])
            if not src.startswith('r'):
                raise Exception(r"Source operand error!")
            else:
                src = int(src[1:])
            self.memory.write_data(des, Word(num_str=self.register[src]))

        self.instructions.append(Instruction(instruction_name="Store", func=execute_func))


class CPU:
    """CPU类"""

    def __init__(self):
        self.register = None
        self.memory = MyMemory()
        self.memory_init()
        self.register_init()
        self.instructions = Instructions(self.memory, self.register)

    def register_init(self):
        register_cell = ''.join(Word(0).data)
        self.register = [register_cell for _ in range(32)]

    def memory_init(self):
        self.memory.write_data(0, Word(10))
        self.memory.write_data(1, Word(15))

    def run_code(self, code: str):
        print(code)
        code_a = code.split(',')
        instruction_name, p1 = tuple(code_a[0].strip().split(' '))
        p = [p1]
        for s in code_a[1:]:
            p.append(s.strip())
        for instruction in self.instructions.instructions:
            if instruction.instruction_name == instruction_name:
                instruction.execute(p)
                break

    def show_memory(self):
        for m in self.memory.memory:
            print(m)


cpu = CPU()
with open('codes.txt', 'r') as f:
    lines = f.readlines()

for code in lines:
    cpu.run_code(code)

cpu.show_memory()

# print(Word(10).data)
