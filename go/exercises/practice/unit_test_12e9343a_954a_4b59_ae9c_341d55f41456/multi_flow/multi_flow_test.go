package multiflow

import (
    "reflect"
    "testing"
)

func TestMultiFlow(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            actual := MaxMultiFlow(tc.n, tc.edges, tc.commodities)
            if !reflect.DeepEqual(actual, tc.expected) {
                t.Errorf("MaxMultiFlow(%d, %v, %v) = %v; want %v",
                    tc.n, tc.edges, tc.commodities, actual, tc.expected)
            }
        })
    }
}

func BenchmarkMultiFlow(b *testing.B) {
    if testing.Short() {
        b.Skip("skipping benchmark in short mode.")
    }
    for i := 0; i < b.N; i++ {
        for _, tc := range testCases {
            MaxMultiFlow(tc.n, tc.edges, tc.commodities)
        }
    }
}