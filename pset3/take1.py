import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                # loại bỏ các giá trị không phù hợp với độ dài của ô trống
                if len(word) is not var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #var để theo dõi các từ đã sửa đổi
        revisons = []
        # tìm nạp chồng chéo cho cả hai từ
        overlap = self.crossword.overlaps[x, y]
        # nếu các biến không trùng lặp thì k cần chỉnh sửa
        if overlap is None:
            return False
        # đối với mỗi tổ hợp từ phù hợp với miền của các biến
        for word_x in self.domains[x].copy():
            can_combine = False
            for word_y in self.domains[y]:
                #kiểm tra xem các từ có trùng lặp với 1 chữ cái hay không
                if word_x is not word_y and word_x[overlap[0]] is word_y[overlap[1]]:
                    can_combine = True
                    break
            # nếu không thể kết hợp hãy xoá các giá trị trong miền của self.domain[x]
            # mà không có giá trị tương ứng với y trong self.domain[y]
            if not can_combine:
                revisons.append(word_x)
                self.domains[x].remove(word_x)
            #trả về True nếu bản sửa được thực hiện cho miền của x nếu không sửa đổi trả
            # về False
        if len(revisons) > 0 :
            return True
        return False


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x,y))
        # nếu không, hãy sử dụng 'arcs' làm danh sáhc ban đầu của các cung để tạo sự nhật quán
        for x, y in arcs:
            # cập nhật 'self.domains sao cho mỗi biến đều nhất quán
            if self.revise(x, y):
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))
        # trả về True nếu tính nhất quán của cung được thực thi và không có miền nào trống
        # trả về False nếu một hoặc nhiều tên miền trống
        return len(self.domains[x]) > 0

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # đối với mỗi biến , hãy kiểm tra xem nó nằm trong các từ khoá hay nằm trong
        # các từ trong trò chơi ô chữ
        for var in self.crossword.variables:
            if var not in assignment.keys() or assignment[var] not in self.crossword.words:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # đối với mỗi biến, kiểm tra tất cả các vấn đề của tính nhất quán
        for var_1 in assignment:
            word_1 = assignment[var_1]
            #nếu độ dại không khớp
            if var_1.length is not len(word_1):
                return False
            # kiể tra kết hợp hai biến
            for var_2 in assignment:
                word_2 = assignment[var_2]
                if var_1 != var_2:
                    if word_1 is word_2:
                        return False
                    overlap = self.crossword.overlaps[var_1, var_2]
                    if overlap is not None:
                        x, y = overlap
                        # nếu các chữ cái chồng lên nhau không giống nhau
                        if word_1[x] is not word_2[y]:
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # trả lại bất kì biến nào còn lại sẽ được gám( không phải trong các khoá)
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return var
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Kiểm tra xem nó đã hoàn chỉnh chưa để kết thúc đệ quy
        if self.assignment_complete(assignment):
            return assignment
        # đối với mỗi biến chưa được gán còn lại
        var = self.select_unassigned_variable(assignment)
        # nhận csc giá trị có thể có trong miền
        for val in self.order_domain_values(var, assignment):
            # gắng giá trị và kiểm tra tính nhất quán
            assignment[var] = val
            if self.consistent(assignment):
                # đệ quy để tìm ra giải pháp - nếu phép gán khiến giải pháp không
                # thể thực hiện thì huỷ và bật khỏi giải pháp
                solution = self.backtrack(assignment)
                if solution is None:
                    assignment[var] = None
                else:
                    return solution
        # nếu không thể chuyển nhượng , trả về không
        return None




def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
