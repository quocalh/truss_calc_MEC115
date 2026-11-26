from components import *
import numpy as np

class AugMatrix:
    def __init__(self):
        self.b_A: list[list[float]] = []

    def modify(self, x, y, value: any):
        self.b_A[y][x] = value

    def add(self, x, y, value: any):
        self.b_A[y][x] += value

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

        if (np.linalg.det(A) == 0):
            print("can't be solved (singularity).")
            return False
    
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
        self.solution = AugMatrix()

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

        """
        for support in supports:
            self.truss_support_contribute(support)
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
            self.solution.modify(x, y, -vector[1])

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

    def truss_contribute(self, truss: Truss):
        relative = vector2_sub(truss.p2.point, truss.p1.point)

        self.truss_support_contribute(truss.p1)
        self.truss_support_contribute(truss.p2)

        # point1
        basis = vector2_unit(relative)

        x = self.fetch_coef_index(truss.name)
        y = self.fetch_eq_index(truss.p1.name + "x")
        self.solution.modify(x, y, basis[0])
        y = self.fetch_eq_index(truss.p1.name + "y")
        self.solution.modify(x, y, -basis[1])

        # point2
        basis = vector2_scale(basis, -1)
        x = self.fetch_coef_index(truss.name)
        y = self.fetch_eq_index(truss.p2.name + "x")
        self.solution.modify(x, y, basis[0])
        y = self.fetch_eq_index(truss.p2.name + "y")
        self.solution.modify(x, y, -basis[1])

    def truss_support_contribute(self, support: Support):
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

    def solve_frame(self, members: list[Member], supports: list[Support], forces: list[Force]):
        self.solution = AugMatrix()

        # check is the frame structure is solvable or not
        unknowns = 0
        capability = 0
        """
        unknowns:
            + frame -> investigate all the owned supports
                pin? += 2
                roller? += 1
                joint? += 2
                    (force*)joint? += 0?
                    how to know? (*)
                        just count it in
                        introducing 2 new unknowns
                        countered by a couple of joint contribution (Fx, Fy)
                    -> (force*)joint? += 2
            + truss * 1
                introduce tension as its owner unknown
                    at the same time, spew out two contributions to 2 linking suports

        capability:
            + len(support) * 2 
                (each support Fx, Fy = 0 -> 2 equations each support)
            + frame * 3
                (each frame requires us to contruct a FBD, including Fx, Fy, M equations -> 3 equations each frame)
            + truss * 0
                truss, unfortunately, doesn't count in capability checking
                    it still does it job by contributing its force into the support function mentioned above
                    it just that it is independent from the solvability of the frame structure
        """

            # calculating unknowns
        for member in members:
            member_type = member.type
            if (member_type == COMPONENT_TYPE.TRUSS):
                unknowns += 1

            elif (member_type == COMPONENT_TYPE.FRAME):
                member: Frame = member
                member_supports = [member.p1, member.p2] + member.binds

                for support in member_supports:
                    support_type = support.type

                    if (support_type == COMPONENT_TYPE.PIN):
                        unknowns += 2
                    elif (support_type == COMPONENT_TYPE.JOINT):
                        unknowns += 2
                    elif (support_type == COMPONENT_TYPE.ROLLER):
                        unknowns += 1
                    else:
                        print("who are you?", support_type)
                        assert(0)
            else:
                print("who tf are you?", member_type) 
                assert(0)


            # calculating capability 
        for support in supports:
            # discarding force generator
            if support.type == COMPONENT_TYPE.PIN:
                continue
            elif support.type == COMPONENT_TYPE.ROLLER:
                continue
            else:
                capability += 2

        for member in members: 
            if member.type == COMPONENT_TYPE.FRAME:
                capability += 3
            elif member.type == COMPONENT_TYPE.TRUSS:
                continue
            else:
                print("who are you buddy?", member.type)
                assert(0)

        print("capability:", capability, "unknowns:",unknowns)

        if (capability != unknowns):
            print(f"check again, too few, or too many unknowns ig ({unknowns} unknowns vs {capability} capability).")
            return

        # init solution matrix
        self.solution.b_A = [[0 for _ in range(capability + 1)] for _ in range(capability)]
        
        
        # spare the first column for scalar field
        self.coef_field_index += 1 

        # forces-(scalar) contribution model
        for force in forces:
            # at-joint constraint contribution

            """
            So apprently, inverting this vector make this whole thing works ig :D
            """
            vector = force.vector
                # Fx
            self.solution.add(
                0,
                self.fetch_eq_index(force.support.name + "x"), 
                -vector[0]
                # vector[0]
            )
                # Fy
            self.solution.add(
                0, 
                self.fetch_eq_index(force.support.name + "y"),
                vector[1]
                # -vector[1]
            )

            """
            # FBD contribution (<Support Name>_<Member Name>_< x | y | M >)
            if force.support.owning_member is not None:
                member: Member = force.support.owning_member
                if (member.type == COMPONENT_TYPE.FRAME):
                    # Fx
                    self.solution.add(
                        0, 
                        self.fetch_eq_index(member.name + "x"),
                        vector[0]
                    )
                    # Fy
                    self.solution.add(
                        0,
                        self.fetch_eq_index(member.name + "y"),
                        -vector[1]
                    )
                    # M
                    # (ax, -ay) x (bx, -by)
                    # = ax * -by - -ay * bx
                    a = vector2_relative(member.p1.point, force.support.point) 
                    b = vector
                    self.solution.add(
                        0, 
                        self.fetch_eq_index(member.name + "M"),
                        a[0] * -b[1] + a[1] * b[0]
                    )
                else:
                    print("who are you? ", member.type)
                    assert(0)
            """

        # members
        for member in members:
            member_type = member.type 

            if member_type == COMPONENT_TYPE.TRUSS:
                # unit = member.unit
                unit = vector2_unit(vector2_relative(member.p1.point, member.p2.point))
                # A_Fx                 
                self.solution.add(
                    self.fetch_coef_index(member.name),
                    self.fetch_eq_index(member.p1.name + "x"),
                    unit[0] 
                )
                # A_Fy
                self.solution.add(
                    self.fetch_coef_index(member.name),
                    self.fetch_eq_index(member.p1.name + "y"),
                    -unit[1]
                )

                unit = vector2_scale(unit, -1)
                # B_Fx
                self.solution.add(
                    self.fetch_coef_index(member.name),
                    self.fetch_eq_index(member.p2.name + "x"),
                    unit[0]
                )
                # B_Fy
                self.solution.add(
                    self.fetch_coef_index(member.name),
                    self.fetch_eq_index(member.p2.name + "y"),
                    -unit[1]
                )

            elif member_type == COMPONENT_TYPE.FRAME:
                frame: Frame = member 
                frame_supports = [frame.p1, frame.p2] + frame.binds

                # <>: 
                """
                force generators will skip the the contribution phase 
                joints will 
                """

                member_name_x = member.name + "x"
                member_name_y = member.name + "y"
                member_name_M = member.name + "M"

                for support in frame_supports:
                    if support.type == COMPONENT_TYPE.PIN:
                        # Fx 
                        self.solution.add(
                            self.fetch_coef_index(support.name + "rx"),
                            self.fetch_eq_index(member.name + "x"),
                            1
                        )
                        # Fy
                        self.solution.add(
                            self.fetch_coef_index(support.name + "ry"),
                            self.fetch_eq_index(member.name + "y"),
                            1
                        )
                        
                        # FM
                        relative = vector2_relative(member.p1.point, support.point)
                        """
                        (rx, -ry) x (Arx, -Ary) 
                        = rx * (-Ary) - (-ry) * Arx
                        = -rx * Ary + ry * Arx
                        = {Arx: ry, Ary: -rx}
                        """  
                        self.solution.add(
                            self.fetch_coef_index(support.name + "rx"),
                            self.fetch_eq_index(member.name + "M"),
                            relative[1]
                        )                        
                        self.solution.add(
                            self.fetch_coef_index(support.name + "ry"),
                            self.fetch_eq_index(member.name + "M"),
                            # -relative[0]
                            relative[0]
                        )                        

                    elif support.type == COMPONENT_TYPE.ROLLER:
                        # Fy
                        self.solution.add(
                            self.fetch_coef_index(support.name + "ry"),
                            self.fetch_eq_index(member.name + "y"),
                            1
                        )
                        # FM
                        """
                        (rx, -ry) x (0, -Bry) 
                        = rx * (-Bry) - (-ry) * 0
                        = {Bry: -rx}
                        """
                        relative = vector2_relative(member.p1.point, support.point)
                        self.solution.add(
                            self.fetch_coef_index(support.name + "ry"),
                            self.fetch_eq_index(member.name + "M"),
                            # -relative[0]
                            relative[0]
                        )

                    elif support.type == COMPONENT_TYPE.JOINT:
                        # Fx 
                        Fx_name = support.name + "_" + member.name + "_x"
                        Fy_name = support.name + "_" + member.name + "_y"

                        self.solution.add( 
                            self.fetch_coef_index(Fx_name),
                            self.fetch_eq_index(member.name + "x"),
                            1
                        )
                        # Fy
                        self.solution.add( 
                            self.fetch_coef_index(Fy_name),
                            self.fetch_eq_index(member.name + "y"),
                            1
                        )

                        # FM
                        """
                        (rx, -ry) x (E_AD_x, -E_AD_y)
                        = rx * (-E_AD_y) - (-ry) * E_AD_x
                        = {E_AD_x: ry, E_AD_y: -rx}
                        """
                        relative = vector2_relative(member.p1.point, support.point)
                        self.solution.add(
                            self.fetch_coef_index(Fx_name),
                            self.fetch_eq_index(member.name + "M"),
                            relative[1]
                        )
                        self.solution.add(
                            self.fetch_coef_index(Fy_name),
                            self.fetch_eq_index(member.name + "M"),
                            # -relative[0]
                            relative[0]
                        )

                        # joint contribute
                        self.solution.add(
                            self.fetch_coef_index(Fx_name),
                            self.fetch_eq_index(support.name + "x"), 
                            1
                        )
                        self.solution.add(
                            self.fetch_coef_index(Fy_name),
                            self.fetch_eq_index(support.name + "y"),
                            1
                        )
                        

                    else:
                        print("so who are you?", support_type)
                        assert(0)

            else:
                print("who are you again?", member_type)
                assert(0)

        print(self.eq_field)

        print(self.coef_field)

        self.debug()
        x = self.solution.solve()

        if (x is False):
            return

        translate: dict = {}
        for coef_name in self.coef_field:
            coef_index = self.coef_field[coef_name]
            translate[coef_index] = coef_name

        i = 1
        for ans in x:
            print(f"{translate[i]}: {ans}")
            i += 1 

    def frame_FBD(self, support, coef_name, eq_name_prefix: str, 
                  rx: float, ry: float, vx: float, vy: float):
        # Fx
        self.solution.add
        # Fy
        # FM (rx, ry)
        pass
            
    def frame_contribute_fxy(self, coef_name, eq_name_prefix: str, vx: float, vy: float):
        self.solution.add(
            self.fetch_coef_index(coef_name + "x"),
            self.fetch_eq_index(eq_name_prefix + "x"),
            vx
        )
        self.solution.add(
            self.fetch_coef_index(coef_name + "y"),
            self.fetch_eq_index(eq_name_prefix + "y"),
            vy
        )



        
        


