#!/usr/bin/env python3
"""Validate marked PHP array/generator and Java stream/IO programs unchanged."""
import verify_php_java_foundations as runner

runner.DOCUMENTS = {
    "07-php-mastery/reference/language-concepts/05-arrays-patterns.md": ("php", 3),
    "07-php-mastery/reference/language-concepts/06-generators-iterators.md": ("php", 3),
    "08-java-revisited/reference/language-concepts/03-streams-optional.md": ("java", 3),
    "08-java-revisited/reference/library-guides/04-java-io.md": ("java", 3),
}

if __name__ == "__main__":
    raise SystemExit(runner.main())
