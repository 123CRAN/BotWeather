class GeometryFigure:
    def __init__(self, name):
        self.name = name


class Triangle(GeometryFigure):
    """Подкласс от класса геометр.фигуры"""

    def __init__(self, name, side1, side2, side3):
        super().__init__(name)
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def ploshad(self):  # Через формулу Герона
        p = (self.side1 + self.side2 + self.side3) / 2
        pl = pow((p * (p - self.side1) * (p - self.side2) * (p - self.side3)), 0.5)
        triangle_pl = f'Площадь {self.name} равна - {pl}'
        return triangle_pl


class Rectangle(GeometryFigure):
    """Подкласс от класса геометр.фигуры"""

    def __init__(self, name, width, height):
        super().__init__(name)  # super. позволяет обращаться к родительскому классу
        self.width = width
        self.height = height

    def ploshad(self):
        pl = f'Площадь {self.name} равна - {self.width * self.height}'
        return pl
