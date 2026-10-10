"""Replay the real CI layout race through Suite.tap/observe, replacing only ADB."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
import unittest

from suite import PACKAGE, Suite

FIXTURE = json.loads(Path(__file__).with_name('readiness-fixture.json').read_text())


class ReplaySuite(Suite):
    def __init__(self, out, observations):
        super().__init__([], {}, 'recorded-device', out, {}, {}, out, {})
        self.observations = iter(observations)
        self.touches = []
        self.case_deadline = self.suite_deadline = time.monotonic() + 5

    def shell(self, *args, **kwargs):
        if args == ('run-as', PACKAGE, 'cat', 'files/observation.json'):
            return json.dumps(next(self.observations))
        if args[:2] == ('input', 'tap'):
            self.touches.append(args)
            return ''
        raise AssertionError('Unexpected ADB operation: ' + str(args))


class InteractionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.unlaid = deepcopy(FIXTURE['unlaid'])
        self.laid = deepcopy(FIXTURE['laid'])

    def driver(self, observations=()):
        return ReplaySuite(Path(self.temp.name) / 'observations', observations)

    def test_real_ci_unlaid_frame_waits_for_actual_target_coordinates(self):
        driver = self.driver([self.laid])
        captured = driver.tap('new-game', self.unlaid)
        self.assertEqual(driver.touches, [('input', 'tap', '540', '1492')])
        self.assertEqual(captured, 1791605255091)

    def test_positive_bounds_do_not_make_an_invisible_target_ready(self):
        target = next(n for n in self.unlaid['nodes'] if n['name'] == 'new-game')
        target['bounds'] = [10, 20, 30, 40]
        driver = self.driver([self.laid])
        driver.tap('new-game', self.unlaid)
        self.assertEqual(driver.touches, [('input', 'tap', '540', '1492')])

    def test_visibility_does_not_make_zero_geometry_ready(self):
        next(n for n in self.unlaid['nodes'] if n['name'] == 'new-game')['visible'] = True
        driver = self.driver([self.laid])
        driver.tap('new-game', self.unlaid)
        self.assertEqual(driver.touches, [('input', 'tap', '540', '1492')])

    def test_readiness_cannot_switch_to_another_process_or_menu_state(self):
        other_process = deepcopy(self.laid)
        other_process['process'] = 'another-process'
        other_state = deepcopy(self.laid)
        other_state['state']['best'] = 128
        for observation in (other_process, other_state):
            next(n for n in observation['nodes'] if n['name'] == 'new-game')['bounds'] = [10, 20, 30, 40]
        driver = self.driver([other_process, other_state, self.laid])
        driver.tap('new-game', self.unlaid)
        self.assertEqual(driver.touches, [('input', 'tap', '540', '1492')])

    def test_ready_disabled_continue_is_still_physically_touched(self):
        driver = self.driver()
        captured = driver.tap('continue', self.laid)
        self.assertEqual(driver.touches, [('input', 'tap', '540', '1312')])
        self.assertEqual(captured, 1791605255091)

    def test_expired_case_never_taps_an_unlaid_target(self):
        driver = self.driver([self.laid])
        driver.case_deadline = time.monotonic() - 1
        with self.assertRaises(AssertionError):
            driver.tap('new-game', self.unlaid)
        self.assertEqual(driver.touches, [])


if __name__ == '__main__':
    unittest.main()
