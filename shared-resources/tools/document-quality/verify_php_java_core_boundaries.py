#!/usr/bin/env python3
"""Verify the marked PHP attributes/Fiber and Java collection/resource programs.

Uses the common unchanged-source extractor, case-count guard, strict stdout/stderr
comparison and per-case temporary directories from the foundations verifier.
"""
import verify_php_java_foundations as runner

runner.DOCUMENTS = {
    "07-php-mastery/basics/07-advanced-features.md": ("php", 3),
    "08-java-revisited/reference/language-concepts/02-collections-generics.md": ("java", 3),
    "08-java-revisited/reference/language-concepts/06-exceptions-resources.md": ("java", 2),
}

if __name__ == "__main__":
    raise SystemExit(runner.main())
