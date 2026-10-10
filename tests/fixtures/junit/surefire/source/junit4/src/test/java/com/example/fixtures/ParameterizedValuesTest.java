package com.example.fixtures;

import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.Collection;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

/** JUnit 4's Parameterized runner, whose test names carry the parameter index. */
@RunWith(Parameterized.class)
public class ParameterizedValuesTest {

    @Parameters(name = "{index}: value {0}")
    public static Collection<Object[]> data() {
        return Arrays.asList(new Object[][] {{1}, {2}, {3}});
    }

    @Parameter
    public int value;

    @Test
    public void rejectsTwo() {
        assertTrue("two is rejected", value != 2);
    }
}
