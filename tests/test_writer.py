
import json
import logging
import os
import tempfile
import unittest

from uncover_json_writer import BinaryDetector, CategoricalDetector, ToolJSONWriter


class TestWriter(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.tmp.close()

    def tearDown(self):
        os.remove(self.tmp.name)
        del self.tmp

    def test_demo(self):
        """Test on the demo from 1.0.0."""
        self.logger.info("test_demo")

        # === DEMO ===
        # tool contains following detectors
        tool = 'steganography_detector'
        detectors = [
            BinaryDetector(name='is_tampered', labels=['original', 'tampered']),
            CategoricalDetector(name='3valued_detector', labels=['cover', 'stego', 'not_sure'])
        ]
        # instantiate writer
        wrt = ToolJSONWriter(path=self.tmp.name, tool=tool, detectors=detectors, version='2023.03.02')
        # add score from one detector for the first file
        wrt.append('first.jpeg', 'is_tampered', {'original': .8, 'tampered': .2}, 'original')
        # add score from one detector for the second file
        wrt.append('second.jpeg', 'is_tampered', {'original': .3, 'tampered': .7}, 'tampered')
        # another approach (for start and end time actually meaning something) is to announce/prepend file record
        # this is called before processing of the file
        wrt.prepend(file='third.jpeg')
        import time
        time.sleep(.5)  # crunching, crunching
        # processing of third file done, writing the results
        wrt.append('third.jpeg', '3valued_detector', {'cover': 0.05, 'stego': 0.8, 'not_sure': .15}, 'stego')
        # writer writes on __del__ call, i.e., when the object is removed
        # this can be done explicitly with
        del wrt
        # ===========

        # load and parse result
        with open(self.tmp.name) as fp:
            res = json.load(fp)
        print(res)
        # check global structure
        self.assertIsInstance(res, dict)
        FILES = ['first.jpeg', 'second.jpeg', 'third.jpeg']
        for f in FILES:
            self.assertIn(f, res)
            self.assertIsInstance(res[f], dict)
            self.assertIn('tools', res[f])
            self.assertIsInstance(res[f]['tools'], dict)
            self.assertIn('steganography_detector', res[f]['tools'])
            self.assertIsInstance(res[f]['tools']['steganography_detector'], dict)
            self.assertIn('version', res[f]['tools']['steganography_detector'])
            self.assertIsInstance(res[f]['tools']['steganography_detector']['version'], str)
            self.assertIn('configuration', res[f]['tools']['steganography_detector'])
            self.assertIsInstance(res[f]['tools']['steganography_detector']['configuration'], dict)
            self.assertIn('filter', res[f]['tools']['steganography_detector'])
            self.assertIs(res[f]['tools']['steganography_detector']['filter'], None)
            self.assertIn('start_timestamp', res[f]['tools']['steganography_detector'])
            # TODO
            # self.assert(res[f]['tools']['steganography_detector']['start_timestamp'], None)
        print(res)
