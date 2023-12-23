from typing import Union

class GeometryFigure:
    def __init__(self, name: str):
        self.name = name


class Triangle(GeometryFigure):
    """Подкласс от класса геометр.фигуры"""

    def __init__(self, name: str, side1: float, side2: float, side3: float):
        super().__init__(name)
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def ploshad(self) -> str:  # Через формулу Герона
        p = (self.side1 + self.side2 + self.side3) / 2
        pl = pow((p * (p - self.side1) * (p - self.side2) * (p - self.side3)), 0.5)
        triangle_pl: str = f'Площадь {self.name} равна - {pl}'
        return triangle_pl


class Rectangle(GeometryFigure):
    """Подкласс от класса геометр.фигуры"""

    def __init__(self, name: str, width: float, height: float):
        super().__init__(name)  # super. позволяет обращаться к родительскому классу
        self.width = width
        self.height = height

    def ploshad(self) -> str:
        pl: str = f'Площадь {self.name} равна - {self.width * self.height}'
        return pl
