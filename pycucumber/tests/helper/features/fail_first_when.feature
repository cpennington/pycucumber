Feature: Success
  Scenario:
    Given pass
      And pass
    When fail
      And skip
    Then skip
      And skip
    When skip
    Then skip