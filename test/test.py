import unittest

import acwingcli


class TestAcwingCLI(unittest.TestCase):
    def test_submit(self):
        acwingcli.main()
    
    def test_get_problem_id(self):
        self.assertEqual(acwingcli.get_problem_id('https://www.acwing.com/problem/content/28/'), '28')
        self.assertRaises(NameError, acwingcli.get_problem_id, 'https://www.acwing.com/problem/content/1sds23/')
                         


if __name__ == '__main__':
    print('ahha')
    unittest.main()
