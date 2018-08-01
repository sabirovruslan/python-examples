from unittest import TestCase, TestSuite, makeSuite, TextTestRunner
from ip2w import get_ip_info, get_weather_info


class Ip2wTest(TestCase):

    def test_receiving_of_ip_without_params(self):
        result = get_ip_info()
        self.assertTrue('error' not in result)

    def test_receiving_of_ip_wit_params(self):
        result = get_ip_info(ip_value='77.66.180.32')
        self.assertTrue(result.get('city') == 'Rostov-on-Don')

    def test_weather_info_without_coords(self):
        result = get_weather_info(coords=('a', 'b'))
        self.assertTrue(result['cod'] == '400')

    def test_weather_info_with_coords(self):
        result = get_ip_info(ip_value='77.66.180.32')
        lat, long = result.get('loc').split(',')
        weather = get_weather_info(coords=(float(lat), float(long)))
        self.assertTrue(weather['name'] == 'Rostov-on-Don')


def suite():
    test_suite = TestSuite()
    test_suite.addTest(makeSuite(Ip2wTest))
    return test_suite


if __name__ == '__main__':
    runner = TextTestRunner()
    runner.run(suite())
