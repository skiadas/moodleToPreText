from moodle2pretext.question.coderunner_question import CodeRunnerQuestion, TestCase
import sys
import io

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
    return [self.runCase(correctCode, case) for case in exampleCases]

  def runCase(self, code: str, case: TestCase) -> TestRunResult:
    namespace = {}
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    old_stdin = sys.stdin
    redirected_input = sys.stdin = io.StringIO(case.stdInput)
    exec("\n".join([code, case.testCode]), namespace)
    sys.stdout = old_stdout
    sys.stdin = old_stdin
    redirected_output.seek(0)
    return (case.testCode, case.stdInput, redirected_output.read().strip())
