"""
    Unit tests for class SandboxServer
"""

import unittest

# from sys import exit as sys_exit
from os.path import isfile as os_isfile
from shutil import rmtree
from pathlib import Path

from sandbox_server import SandboxServer

class TestSandboxServer(unittest.TestCase):
    """
        Sandbox server tests
    """

    TEST_DIR = 'test_sandbox_server'
    QUARANTINE_DIR = f'{TEST_DIR}/quarantine_dir'

    def setUp(self) -> None:
        self.sandbox_server = SandboxServer(
            threads_num = 10,
            quarantine_directory = self.QUARANTINE_DIR,
        )
        # Thread(target=self.server.start, daemon=True).start()
        self._create_test_dir(self.TEST_DIR)
        return super().setUp()

    def tearDown(self) -> None:
        self.sandbox_server.stop()
        self._delete_test_dir(self.TEST_DIR)
        return super().tearDown()

    def test_check_local_file(self):
        """
            Check file for shifts in right place
        """
        text = '\n'.join([
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed libero enim, ',
            'varius nec dapibus eget, vestibulum sit amet tellus. Integer varius, nunc ',
            'ornare porta tincidunt, orci neque vulputate nulla, non aliquam erat justo ',
            'in ipsum. Interdum et malesuada fames ac ante ipsum primis in faucibus. ',
            'Praesent sit amet leo pulvinar dui fermentum varius a vitae dolor. ',
            'Suspendisse scelerisque lobortis tellus, sit amet blandit elit ultricies quis.',
        ])
        shifts = '[6, 232, 275]'
        filename = 'test_check_local_file.txt'
        filepath = f'{self.TEST_DIR}/{filename}'
        self._create_file(filepath, text)
        result = self.sandbox_server.check_local_file(filepath, 'ipsum')
        self.assertEqual(result, shifts, 'Wrong shifts')

    def test_quarantine_local_file(self) -> None:
        """
            Check sending file to the quarantine
        """
        filename = 'test_quarantine_local_file.txt'
        filepath = f'{self.TEST_DIR}/{filename}'
        self._create_file(filepath, 'test_quarantine_local_file')
        self.sandbox_server.quarantine_local_file(filepath)
        self.assertTrue(os_isfile(f'{self.QUARANTINE_DIR}/{filename}'))

    def _create_test_dir(self, dirname:str) -> None:
        """
            Create directory for tests in current directory.
        """
        Path(dirname).mkdir(parents=True, exist_ok=True)

    def _delete_test_dir(self, dirname:str) -> None:
        """
            Delete directory for tests.
        """
        rmtree(dirname)

    def _create_file(self, filename:str, text:str=None) -> None:
        """
            Create file with given text for test in current directory
        """
        with open(filename, 'x', encoding='utf-8') as file:
            if text:
                file.write(text)
            file.close()



if __name__=='__main__':
    unittest.main()
