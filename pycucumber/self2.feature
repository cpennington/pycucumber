Feature:
  In order to test pycucumber

  Scenario:
    Given a feature file fail_given.feature
    And a rules file simple.py
    When I run them
    Then the feature should fail
    And 0 tests should pass
    And 1 tests should fail
    And 0 tests should be unimplemented
    And 2 tests should be skipped
    And 0 tests should be ambiguous
