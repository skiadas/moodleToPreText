from moodle2pretext.question.coderunner_question import CodeRunnerQuestion, TestCase
import subprocess
import tempfile
import os.path

TestRunResult = tuple[str, str, str]


class PythonCodeRunner:
  """
  Class that is given a coderunner question and executes the
  test cases that are meant to be used as example, in a Python
  environment
  """

  def runExampleCases(self,
                      question: CodeRunnerQuestion) -> list[TestRunResult]:
    """Returns a list of results of a run: (testcode, input, result)"""
    correctCode = "\n".join([question.preamble or "", question.answer])
    exampleCases = [c for c in question.testCases if c.useAsExample]
    return [
        self.runCase(correctCode, case, question.datafiles)
        for case in exampleCases
    ]

  def runCase(
      self, code: str, case: TestCase, datafiles: dict[str,
                                                       str]) -> TestRunResult:
    with tempfile.TemporaryDirectory() as tempDir:
      for fname, contents in datafiles.items():
        with open(os.path.join(tempDir, fname), "w") as f:
          f.write(contents)
      testCode = "\n".join([code, case.testCode])
      try:
        res = subprocess.run(
            ["python3", "-c", testCode],
            cwd=tempDir,
            capture_output=True,
            text=True,
            input=case.stdInput,
            check=True)
        result = res.stdout.strip()
      except subprocess.CalledProcessError as error:
        print(error.stderr)
        print("Error!!!")
        result = "error"
    return (case.testCode, case.stdInput, result)
