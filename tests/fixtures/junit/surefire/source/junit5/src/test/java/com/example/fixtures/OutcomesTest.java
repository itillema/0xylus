package com.example.fixtures;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** Every outcome Surefire reports for JUnit Jupiter, so the fixtures show how each is written. */
class OutcomesTest {

    @Test
    void passes() {
        assertTrue(true);
    }

    @Test
    void failsWithAssertion() {
        assertEquals(3, 1 + 1, "arithmetic is broken");
    }

    @Test
    void throwsUnexpectedError() {
        throw new IllegalStateException("unexpected state: 42");
    }

    @Test
    @Disabled("not supported on this platform")
    void disabled() {
    }

    @Test
    void writesOutput() {
        System.out.println("line written to stdout");
        System.err.println("line written to stderr");
    }

    @ParameterizedTest(name = "value {0}")
    @ValueSource(ints = {1, 2, 3})
    void parameterized(int value) {
        assertTrue(value != 2, "two is rejected");
    }

    @ParameterizedTest
    @ValueSource(strings = {
        "<script>alert(1)</script>",
        "pipe | in | a table",
        "@maintainer please look",
        "back`ticks`",
        "right-to-left \u202e override"
    })
    void hostileArguments(String text) {
        assertTrue(!text.isEmpty());
    }

    @Test
    @DisplayName("display name with <b>markup</b> | and @mention")
    void customDisplayName() {
    }

    @Test
    void failsWithHostileMessage() {
        throw new AssertionError("<b>bold</b> | @here `code` %0A \u202edesrever");
    }

    @Nested
    class WhenNested {
        @Test
        void passesInNestedClass() {
            assertTrue(true);
        }
    }
}
