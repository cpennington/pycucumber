Feature:
  In order to test pycucumber

  Scenario:
    Given a feature file success.feature
    And a rules file simple.py
    When I run them
    Then the feature should pass
    And 3 test should pass
    And 0 tests should fail
    And 0 tests should be unimplemented
    And 0 tests should be skipped
    And 0 tests should be ambiguous
