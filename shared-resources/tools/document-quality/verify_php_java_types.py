#!/usr/bin/env python3
"""Run complete PHP/Java type tutorial examples through the shared strict runner."""
import verify_php_java_foundations as runner

runner.DOCUMENTS = {
    "07-php-mastery/basics/03-variables-types.md": ("php", 2),
    "08-java-revisited/basics/03-variables-types.md": ("java", 2),
    "08-java-revisited/basics/04-classes-records.md": ("java", 1),
}

if __name__ == "__main__":
    raise SystemExit(runner.main())
