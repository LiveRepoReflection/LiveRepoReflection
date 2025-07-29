package timekeystore

type timeStoreTest struct {
    description string
    operations  []operation
    expected    []string
}

type operation struct {
    op        string
    key       string
    value     string
    timestamp int
}

var tests = []timeStoreTest{
    {
        description: "basic set and get operations",
        operations: []operation{
            {"set", "foo", "bar", 1},
            {"get", "foo", "", 1},
            {"get", "foo", "", 3},
            {"set", "foo", "bar2", 4},
            {"get", "foo", "", 4},
            {"get", "foo", "", 5},
            {"get", "foo", "", 2},
            {"get", "nonexistent", "", 5},
        },
        expected: []string{
            "",
            "bar",
            "bar",
            "",
            "bar2",
            "bar2",
            "bar",
            "",
        },
    },
    {
        description: "multiple keys with overlapping timestamps",
        operations: []operation{
            {"set", "key1", "value1", 1},
            {"set", "key2", "value2", 2},
            {"get", "key1", "", 2},
            {"get", "key2", "", 2},
            {"set", "key1", "value3", 3},
            {"get", "key1", "", 3},
            {"get", "key2", "", 3},
        },
        expected: []string{
            "",
            "",
            "value1",
            "value2",
            "",
            "value3",
            "value2",
        },
    },
    {
        description: "edge cases with timestamps",
        operations: []operation{
            {"set", "key", "value1", 1},
            {"get", "key", "", 0},
            {"get", "key", "", 1000000},
            {"set", "key", "value2", 2000000},
            {"get", "key", "", 1500000},
            {"get", "key", "", 2000000},
        },
        expected: []string{
            "",
            "",
            "value1",
            "",
            "value1",
            "value2",
        },
    },
    {
        description: "concurrent timestamp values",
        operations: []operation{
            {"set", "concurrent", "v1", 1},
            {"set", "concurrent", "v2", 2},
            {"set", "concurrent", "v3", 3},
            {"get", "concurrent", "", 1},
            {"get", "concurrent", "", 2},
            {"get", "concurrent", "", 3},
            {"get", "concurrent", "", 4},
        },
        expected: []string{
            "",
            "",
            "",
            "v1",
            "v2",
            "v3",
            "v3",
        },
    },
}