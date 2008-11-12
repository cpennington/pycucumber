Feature:
  In order to test pycucumber

  Scenario:
    Given a feature file helper/features/more_examples.feature
    And a rules file helper/rules/simple.py
    When I run them
    Then the feature should fail
    And 2 tests should pass
    And 1 test should fail
    And 0 tests should be unimplemented
    And 1 test should be skipped
    And 0 tests should be ambiguous