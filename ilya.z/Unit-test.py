import unittest
from unittest.mock import patch
from io import StringIO
from Geometry import Triangle, Rectangle


class TestGeometryFigures(unittest.TestCase):
    def test_triangle_pl(self):
        # with patch('builtins.input', side_effect=["1", "3 4 5"]):  # Моделируем ввод пользователя
        #     with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                triangle = Triangle('Треугольник', 3, 4, 5)
                triangle.ploshad()
                self.assertEqual(triangle.ploshad(), 'Площадь Треугольник равна - 6.0')

    def test_rectangle_pl(self):
        # with patch('builtins.input', side_effect=["2", "2 3"]):  # Моделируем ввод пользователя
        #     with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        rectangle = Rectangle('Прямоугольник', 2, 3)
        rectangle.ploshad()
        self.assertEqual(rectangle.ploshad(), 'Площадь Прямоугольник равна - 6')


if __name__ == '__main__':
    unittest.main()
