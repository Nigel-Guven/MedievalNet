import sys
import os


SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SRC_PATH)

from objects.faction import CampaignFaction

import unittest
import parser
from objects.region import Region

class ParserTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        
        with open("../../input/descr_regions.txt", "r") as f:
            cls.regions_data = f.read()
    
        cls.regions = parser.parse_regions(cls.regions_data)
    
    def test_RegionNumber(self):
        self.assertEqual(len(self.regions), 195)
        
    def test_Religions(self):
        

        for region in self.regions:
            self.assertIsInstance(region, Region)
            
            religionTotal = 0        
            
            for key, value in region.religions.items():
                religionTotal+=value
                print(region.province_name)
                self.assertTrue(Religion(key))
            
            self.assertEqual(religionTotal, 100)
    
    
if __name__ == '__main__':
    unittest.main()