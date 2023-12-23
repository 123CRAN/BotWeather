import unittest
from unittest.mock import patch
from io import StringIO
from Geometry import Triangle, Rectangle


class TestGeometryFigures(unittest.TestCase):
    def test_triangle_pl(self):
                triangle = Triangle('Треугольник', 3, 4, 5)
                triangle.ploshad()
                self.assertEqual(triangle.ploshad(), 'Площадь Треугольник равна - 6.0')

    def test_rectangle_pl(self):
        rectangle = Rectangle('Прямоугольник', 2, 3)
        rectangle.ploshad()
        self.assertEqual(rectangle.ploshad(), 'Площадь Прямоугольник равна - 6')


def start_test():
    if __name__ == '__main__':
        unittest.main()
