import unittest 
from calculator import Calculator 

class TestOperations(unittest.TestCase):

    def test_sum(self):
        calculation = Calculator(8,2)
        self.assertEqual(calculation.get_sum(), 10, 'The sum is wrong')

    def test_difference(self):
    calculation = Calculator(8,2)
    self.assertEqual(calculation.get_difference(), 10, 'The difference is wrong')

    def test_product(self):
        calculation = Calculator(8, 2)
        self.assertEqual(calculation.get_product(), 16, 'The product is wrong')

    def test_quotient(self):
        calculation = Calculator(8, 2)
        self.assertEqual(calculation.get_quotient(), 4.0, 'The quotient is wrong')

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            Calculator(8, 0).get_quotient()
            
if __name__== '__main__':
    unittest.main()