# Testing on three levels

According to many test automation experts, testing should be done on 3 levels:
Unit tests, Integration tests, End-to-End tests.

This section provides a definition of the terms, how they relate and policies.

## The testing pyramid

[![The testing pyramid - Intro](https://upload.wikimedia.org/wikipedia/commons/a/a4/Testing_Pyramid.png)](https://en.wikipedia.org/wiki/Test_automation)

[![The Testing Pyramid: How to Structure Your Test Suite](https://semaphoreci.com/wp-content/uploads/2022/03/pyramid-progression.webp)](https://semaphoreci.com/blog/testing-pyramid)
References:

- <https://semaphoreci.com/blog/testing-pyramid>
- <https://web.dev/articles/ta-strategies>
- <https://semaphoreci.com/wp-content/uploads/2022/03/pyramid-progression.webp>

## Unit tests

The bulk of tests should be unit tests:

- Tests one unit of execution (one function, class, or even method of a class)
- Very easy to write and update (even AI can be used to generate ideas for them)
- Fast to execute (few milliseconds per unit test)
- Can be made to cover all branches of a function
- Mocks can be used, by should be used only outside the test target,
  because Mocks are lies to tell “all is fine” and thus may only be used outside
  the test target (function, class, or method).

## Integration tests

- These test the correct integration of a number of functional units
  (functions, classes, methods)
- Still easy to write and update
- Still very fast to execute (few milliseconds per unit test)

## End-to-End Tests

- These test an entire program end-to-end.
- Any test that runs a program as a whole to test its functionality is an E2E test.
  - Using a sufficient test environment, many E2E tests are possible without XenRT.
- The final E2E test for `xenserver-status-report` is to get a bug-report through
  the UI of XenCenter.
