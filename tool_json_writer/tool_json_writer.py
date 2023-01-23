"""
JSON Writer for standard JSON tool output.
Author: Martin Benes (University of Innsbruck)
"""

# standard packages
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import Any, Dict, List, Union

VERSION = '1.0.0'  # tool version


@dataclass
class Detector:
    """General class for polymorphic detector. It is used for serialization into JSON format."""

    name: str
    """detector name"""
    labels: List[Any] = field(repr=False, default=None)
    """labels for outcome alternatives"""
    scores: Dict[str, float] = None
    """detector results"""
    decision: str = None
    """human readable decision, must be in labels"""

    def set_result(self, scores: Dict[str, float], decision: str):
        """Setter for decision result."""
        assert isinstance(scores, dict), 'detector requires score mapping'
        assert self.scores is None, 'score already set'
        assert self.decision is None, 'decision already set'
        self.scores = scores
        self.decision = decision

    def get_result(self) -> Dict[str, Any]:
        """Abstract method for serialization."""
        raise NotImplementedError

    def label_index(self, l: str = None) -> int:
        """Gives index of label. If label is not given, takes the internal decision."""
        decision = self.decision if l is None else l
        matching = [i for i, v in enumerate(self.labels) if v == decision]
        return matching[0]

@dataclass
class BinaryDetector(Detector):
    """Specific class for serialization of binary detector.

    Example:

    This is a detector that detects standard or custom quantization table.
    Let's say we want to produce a report in unified JSON format that a standard QT was found.
    >>> det = BinaryDetector(name='standard_qt', labels=['standard','custom'])
    >>> det.set_result(scores={'standard': 1.0, 'custom': 0.0}, decision='standard')
    >>> result = det.get_result()
    The result is a dictionary. For full output, use ToolJSONWriter.
    """

    def __postinit__(self):
        """After initialization, sets the labels (if not given)."""
        if self.labels is None:
            self.labels = [0, 1]

    def get_result(self) -> Dict[str, Any]:
        """Serializes binary detector."""
        score = self.scores[self.decision]
        if self.label_index(self.decision) == 0:
            score = 1-score
        return {
            'labels': self.labels,
            'score': [self.scores[k] for k in sorted(self.scores, key=self.label_index)],
            'decision': self.label_index(self.decision),
            'human_readable_decision': self.decision,
        }


@dataclass
class CategoricalDetector(Detector):
    """Specific class for serialization of categorical detector.

    Example:

    This is a detector that detects cover, stego, or watermarking.
    Let's say we want to produce a report in unified JSON format that a stego was found.
    >>> det = CategoricalDetector(name='cover_stego_watermarking', labels=['cover','stego','watermarking'])
    >>> det.set_result(scores={'cover': 0.2, 'stego': 0.7, 'watermarking': 0.1}, decision='stego')
    >>> result = det.get_result()
    The result is a dictionary. For full output, use ToolJSONWriter.
    """

    ascending: bool = field(repr=False, default=None)
    """output in ascending or descending score order, by default None (no ordering)"""
    only_flags:bool = field(repr=False, default=False)
    """show only labels of 1s, by default show all (False)"""

    def __postinit__(self):
        """After initialization, checks the labels were given."""
        assert self.labels is None, 'categorical detector requires labels'

    @staticmethod
    def argsort(seq):
        """Sorts a keys of dictionary in ascending order of the values and returns keys."""
        # list of keys
        keys = list(seq.keys())
        # sort
        indices = sorted(range(len(seq)), key=lambda i: seq[keys[i]])
        # return keys
        return [keys[i] for i in indices]

    def _ordered_labels(self):
        """Shortcut for returning ordered labels and keys."""
        # order of original labels
        if self.ascending is None:
            scores = [self.scores[k] for k in sorted(self.scores, key=self.label_index)]
            labels = self.labels
        # ascending or descending
        elif isinstance(self.ascending, bool):
            # fill missing
            if self.only_flags:
                for label in self.labels:
                    if label not in self.scores:
                        self.scores[label] = 0
            # get order
            keys = self.argsort(self.scores)
            if not self.ascending:
                keys = list(reversed(keys))
            # reorder
            scores = [self.scores[k] for k in keys]
            labels = keys
        else:
            raise TypeError('self.ascending must be bool or None')
        return scores, labels

    def get_result(self) -> Dict[str, Any]:
        """Serializes categorical detector."""
        # order by labels
        scores, labels = self._ordered_labels()
        # serialize output
        res = {
            'labels': labels,
            'scores': scores,
            'decision': self.label_index(self.decision),
            'human_readable_decision': self.decision,
        }
        # only leave ones, if only_flags mode is one
        if self.only_flags:
            # present labels
            true_labels = {
                label
                for label, score in zip(labels, scores)
                if score
            }
            # indices
            flagged = [i for i, label in enumerate(self.labels) if label in true_labels]
            # reorder
            res['labels'] = [self.labels[i] for i in flagged]
            res['scores'] = [1 for i in flagged]
        return res

class ToolJSONWriter:
    """JSON Writer for tool standard output."""
    def __init__(
        self,
        path: str,
        tool: str,
        detectors: List[Detector],
        configuration: Dict[str, Any] = {},
        filter: str = None,
    ):
        """Constructor.

        Args:
            path (str): Path to write.
            tool (str): Name of tool (tool contains multiple detectors).
            detectors (list): List of detectors, objects of Detector class.
            configuration (dict): Dictionary of parameter-value pairs. Must be serializable.
            filter (str): Filter.
        """
        global VERSION
        self.fp = open(path, 'w')
        self.tool = tool
        self.detectors = detectors
        self.version = VERSION
        self.configuration = configuration
        self.filter = filter
        self.data = {}

    def create_file_data(self):
        """Creates empty result record for a file."""
        return {
            'tools': {
                self.tool: {
                    'version': self.version,
                    'configuration': self.configuration,
                    'filter': self.filter,
                    'start_timestamp': self.now(),
                    'end_timestamp': None,
                    'errors': [],
                    'detectors': {
                        d.name: deepcopy(d) for d in self.detectors
                    },
                }
            }
        }

    @staticmethod
    def now():
        """Get current time in ISO format."""
        return datetime.now().isoformat()

    def prepend(self, file: str):
        """Creates (empty) record for a file, set start timestamp.

        Args:
            file (str): Name of file to be processed.
        """
        assert file not in self.data, 'prepended existing file'
        self.data[file] = self.create_file_data()

    def append(self, file: str, detector: str, scores: Union[List[float], Dict[str, float]], decision: str):
        """Set score to a file record, sets end timestamp. Creates record, if prepend() not called before.

        Args:
            file (str): Name of processed file.
            detector (str): Name of detector.
            scores (str): List of scores (in order of labels) or dictionary of pairs label-score.
            decision (str): Label of the final decision.
        """
        if file not in self.data:
            self.data[file] = self.create_file_data()
        self.data[file]['tools'][self.tool]['detectors'][detector].set_result(scores, decision)
        self.data[file]['tools'][self.tool]['end_timestamp'] = self.now()

    def fail(self, file: str, message: str, detector: str = None):
        """Report failure during processing of a file.

        Args:
            file (str): File for which error occured.
            message (str): Error message.
            detector (str): Detector which raised the error. It is added to the message.
        """
        if file not in self.data:
            self.data[file] = self.create_file_data()
        if detector is not None:
            message = f'{detector} error: {message}'
        self.data[file]['tools'][self.tool]['errors'].append(message)

    def __del__(self):
        """Writes the result into file."""
        for f in self.data:
            self.data[f]['tools'][self.tool]['detectors'] = {
                detector_name: detector.get_result()
                for detector_name, detector in self.data[f]['tools'][self.tool]['detectors'].items()
                if detector.decision is not None
            }
        json.dump(self.data, self.fp, indent=2)
        self.fp.close()


if __name__ == '__main__':
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
