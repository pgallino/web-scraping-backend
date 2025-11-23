Feature: Tools management
  As a client I want to manage a catalogue of tools so I can add, list,
  retrieve, update and remove tools from my collection.

  Background:
    Given the service is available

  Scenario: Create a tool
    When I create a tool with name "fastapi" and description "web framework"
    Then the tool is created
    And the created tool includes name "fastapi" and description "web framework"

  Scenario: List tools
    Given a tool named "fastapi" exists
    When I request the list of tools
    Then the list contains a tool with name "fastapi"

  Scenario: Retrieve a tool
    Given a tool named "fastapi" exists
    When I retrieve that tool
    Then I receive the tool details including name "fastapi"

  Scenario: Update a tool
    Given a tool named "fastapi" exists
    When I update the tool's name to "fastapi-updated" and set link "https://example.com" and description "web framework"
    Then the tool is updated
    And the updated tool includes name "fastapi-updated" and link "https://example.com"

  Scenario: Remove a tool
    Given a tool named "fastapi" exists
    When I remove that tool
    Then subsequently retrieving the tool indicates it no longer exists
