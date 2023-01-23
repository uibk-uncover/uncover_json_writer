# Tool JSON Writer

**Author:** Martin Beneš (Universität Innsbruck)

This is a Python module for adoption of the unified JSON format.

This was proposed as a unified output for all tools from the UNCOVER project.

## Setup

Install the package from Github with following command.

```bash
pip3 install git+https://github.com/uibk-uncover/uncover_json_writer
```

## Usage

Test that the package was correctly installed with

```python
python -c 'import uncover_json_writer; print(uncover_json_writer.__version__)'
```

Follow the demo in order to see the basic functionality.


```python
from uncover_json_writer import BinaryDetector, CategoricalDetector, ToolJSONWriter
# tool contains following detectors
tool = 'steganography_detector'
detectors = [
    BinaryDetector(name='is_tampered', labels=['original', 'tampered']),
    CategoricalDetector(name='3valued_detector', labels=['cover', 'stego', 'not_sure'])
]
# instantiate writer
wrt = ToolJSONWriter(path='steganography_detector.json', tool=tool, detectors=detectors)
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
```

Proper documentation is vaguely planned. No promises though :)

## Extending the functionality

Although I plan to solve bugs affecting the main functionality of the module, if you want to extend the module, you are expected to do it yourself. If you think more people could profit from the extension you wrote, create a pull request.

## Credits

This code repository was developed within [UNCOVER project](https://www.uncoverproject.eu/), which received funding from the European Union's Horizon 2020 researcha and innovation program under grant agreement No. [101021687](https://cordis.europa.eu/project/id/101021687/).
