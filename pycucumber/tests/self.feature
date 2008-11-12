Feature:
  In order to test pycucumber

  Scenario: All Successes
    Given a new test
      And a feature file helper/features/success.feature
      And a rules file helper/rules/simple.py
    When I run them
    Then the feature should pass
      And 8 test should pass
      And 0 tests should fail
      And 0 tests should be unimplemented
      And 0 tests should be skipped
      And 0 tests should be ambiguous
    
    More Examples:
      | feature | rule | test_succeed | pass | pass | fail | fail | uimp | uimp | skip | skip | ambig | ambig |
      | helper/features/fail_first_given.feature | helper/rules/simple.py | fail | 0 | pass | 1 | fail | 0 | be unimplemented | 7 | be skipped | 0 | be ambiguous |
      | helper/features/fail_second_given.feature | helper/rules/simple.py | fail | 1 | pass | 1 | fail | 0 | be unimplemented | 6 | be skipped | 0 | be ambiguous |
      | helper/features/fail_first_when.feature | helper/rules/simple.py | fail | 2 | pass | 1 | fail | 0 | be unimplemented | 5 | be skipped | 0 | be ambiguous |
      | helper/features/fail_second_when.feature | helper/rules/simple.py | fail | 3 | pass | 1 | fail | 0 | be unimplemented | 4 | be skipped | 0 | be ambiguous |
      | helper/features/fail_first_then.feature | helper/rules/simple.py | fail | 5 | pass | 1 | fail | 0 | be unimplemented | 2 | be skipped | 0 | be ambiguous |
      | helper/features/fail_second_then.feature | helper/rules/simple.py | fail | 5 | pass | 1 | fail | 0 | be unimplemented | 2 | be skipped | 0 | be ambiguous |
      | helper/features/ambiguous_given.feature | helper/rules/simple.py | fail | 0 | pass | 0 | fail | 0 | be unimplemented | 2 | be skipped | 1 | be ambiguous |
      | helper/features/more_examples.feature   | helper/rules/simple.py | fail | 2 | pass | 1 | fail | 0 | be unimplemented | 1 | be skipped | 0 | be ambiguous |