from components import *
import numpy as np

class AugMatrix:
    def __init__(self):
        self.b_A: list[list[float]] = []

    def modify(self, x, y, value: any):
        self.b_A[y][x] = value

    @property
    def get_m(self):
        return len(self.b_A)

    @property
    def get_n(self):
        return len(self.b_A[0])

    def print_coef_debug(self):
        for row in self.b_A:
            print(" ".join(f"{x:10.2f}" for x in row))

    def add_row(self):
        new_record = self.get_n()
        self.b_A.append([0] * new_record)

    def add_col(self):
        for record in self.b_A:
            record.append(0)

    def solve(self):
        b_A = np.array(self.b_A, dtype = np.float32)
        b = -b_A[:, 0]
        A = b_A[:, 1:]
        x = np.linalg.solve(A, b)
        print(x)                
        return x




class Solver:
    def __init__(self):
        self.solution: AugMatrix = AugMatrix()

        # x
        self.coef_field: dict = {}
        self.coef_field_index = 0 

        # y
        self.eq_field: dict = {}
        self.eq_row_index = 0 

    def reset(self):
        self.__init__()

    def debug(self):
        
        coef_translate: dict = {}
        for coef_name in self.coef_field:
            coef_index = self.coef_field[coef_name]
            coef_translate[coef_index] = coef_name

        record_translate: dict = {}
        for eq_name in self.eq_field:
            eq_index = self.eq_field[eq_name]
            record_translate[eq_index] = eq_name
            
        """
        for eq_name in self.eq_field:
            print(f"{eq_name}: ", end = "") 
            record = self.eq_field[eq_name]

            for i, coef in enumerate(record):
                if (coef == 0): pass
                name = translate[i] 
                print(coef, name, end = "")

                if (i < len(record)):
                    print("+", end = "")

            print(" = 0")
        """
        print(f"{" ":10}|", end='')

        print(f"{"sca":<10}|", end='')
        print("|".join( f"{coef_translate[i]:<10}" for i in range(1, self.solution.get_n)))

        for i, row in enumerate(self.solution.b_A):
            row_name = record_translate[i]
            print(f"{row_name:<10}|", end='')
            print("|".join(f"{x:10.2f}" for x in row))        

    def fetch_coef_index(self, name: str) -> int:
        if (name in self.coef_field):
            return self.coef_field[name]
        self.coef_field[name] = self.coef_field_index
        self.coef_field_index += 1
        return self.coef_field[name]

    def fetch_eq_index(self, name: str) -> int:
        if (name in self.eq_field):
            return self.eq_field[name]
        self.eq_field[name] = self.eq_row_index
        self.eq_row_index += 1
        return self.eq_field[name]

    def solve_truss(self, members: list[Member], supports: list[Support], forces: list[Force]):
        # check is solveable
        capacity = len(supports) * 2

        unknowns = len(members)
        for support in supports:
            if support.type == COMPONENT_TYPE.PIN:
                unknowns += 2
            elif support.type == COMPONENT_TYPE.ROLLER: 
                unknowns += 1

        if (unknowns != capacity):
            print(f"check again, too many unknowns ({unknowns} unknowns > {capacity} capability)")
            return
        print(f"unknowns: {unknowns} && capacity: {capacity}")

        for y in range(capacity):
            self.solution.b_A.append(
                [0] * (capacity + 1)
            )

        """
        NOTE: 
        solution is a flipped aug matrix [b | A] = 0
        we can change it into Ax = -b form later

        NOTE: 
        add in equations (contributing model)
            each member contributes in the "completeness" of the row of equations
            each support has x and y as their equations
                to access to each row, use eq_row_field, with 
                    <name> + "x" : access the Fx
                    <name> + "y" : access the Fy
        """

        self.coef_field_index += 1 # a scalar field at 0
        for force in forces:
            vector = force.vector 

            x = 0 # b scalar index field (for aug mat being b | A)
            # Fx
            y = self.fetch_eq_index(force.support.name + "x")
            self.solution.modify(x, y, vector[0])

            # Fy
            y = self.fetch_eq_index(force.support.name + "y")
            self.solution.modify(x, y, vector[1])

        for member in members:
            if member.type == COMPONENT_TYPE.TRUSS:
                self.truss_contribute(member)

            elif members.type == COMPONENT_TYPE.FRAME:
                print("not yet implemented...")
                assert(0)
            else:
                print("not yet implemented...")
                assert(0)

        self.debug()
        x = self.solution.solve()

        translate: dict = {}
        for coef_name in self.coef_field:
            coef_index = self.coef_field[coef_name]
            translate[coef_index] = coef_name

        i = 1
        for ans in x:
            print(f"{translate[i]}: {ans}")
            i += 1

    def solve_frame(self):
        print("er")

    def truss_contribute(self, truss: Truss):
        relative = vector2_sub(truss.p2.point, truss.p1.point)

        self.support_contribute(truss.p1)
        self.support_contribute(truss.p2)

        # point1
        basis = vector2_unit(relative)

        x = self.fetch_coef_index(truss.name)
        y = self.fetch_eq_index(truss.p1.name + "x")
        self.solution.modify(x, y, basis[0])
        y = self.fetch_eq_index(truss.p1.name + "y")
        self.solution.modify(x, y, basis[1])

        # point2
        basis = vector2_scale(basis, -1)
        x = self.fetch_coef_index(truss.name)
        y = self.fetch_eq_index(truss.p2.name + "x")
        self.solution.modify(x, y, basis[0])
        y = self.fetch_eq_index(truss.p2.name + "y")
        self.solution.modify(x, y, basis[1])

    def support_contribute(self, support: Support):
        if (support.type == COMPONENT_TYPE.PIN):
            # Fx
            x = self.fetch_coef_index(support.name + "rX") # ArX
            y = self.fetch_eq_index(support.name + "x") # A_Fx
            self.solution.modify(x, y, 1)

            # Fy
            x = self.fetch_coef_index(support.name + "rY")
            y = self.fetch_eq_index(support.name + "y")
            self.solution.modify(x, y, 1)

        elif (support.type == COMPONENT_TYPE.ROLLER):
            # Fy
            x = self.fetch_coef_index(support.name + "rY")
            y = self.fetch_eq_index(support.name + "y")
            self.solution.modify(x, y, 1)

        else:
            pass



        
        


