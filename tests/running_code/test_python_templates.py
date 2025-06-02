import unittest
from moodle2pretext.utils.code_writer import CodeWriter
import subprocess


class TestPythonTemplate(unittest.TestCase):

  def test_with_basic_code(self):
    self.assertEqual(
        runWithCodeFilesAndInput("import sys\nsys.stdout.write('hello')", {}),
        "hello")

  def test_using_print(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
print('hello')
sys.stdout.write(_my_out)
""", {}),
        "hello")

  def test_using_input(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
_my_in = ['there', 'hello']
s1 = input()
s2 = input()
sys.stdout.write(s1)
sys.stdout.write(s2)
""", {}),
        "hellothere")

  def test_using_file_without_with(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
f = open("myfile", "r")
sys.stdout.write(f.read())
""", {"myfile": "hello"}),
        "hello")

  def test_using_file_with_with(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
with open("myfile", "r") as f:
    sys.stdout.write(f.read())
""", {"myfile": "hello"}),
        "hello")

  def test_using_file_open_with_implicit_mode(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
f = open("myfile")
sys.stdout.write(f.read())
""", {"myfile": "hello"}),
        "hello")

  def test_readline_seek0_readline(self):
    self.assertEqual(
        runWithCodeFilesAndInput(
            """
import sys
f = open("myfile")
sys.stdout.write(f.readline())
f.seek(0)
sys.stdout.write(f.readline())
sys.stdout.write("so")
""", {"myfile": "hello\nthere"}),
        "hello\nhello\nso")


def runWithCodeFilesAndInput(codeToRun: str, datafiles: dict[str, str]):
  writer = CodeWriter()
  writer.env.tests['is_python_program'] = lambda _: False
  template = writer.codeRunnerPreamble
  code = template.render(
      question={
          "datafiles": datafiles, "preamble": codeToRun
      }, testing=False)
  try:
    res = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        input="",
        check=True)
    return res.stdout.strip()
  except subprocess.CalledProcessError as error:
    print(error.stderr)
    return None
