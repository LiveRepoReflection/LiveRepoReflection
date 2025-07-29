package nexus

import (
    "reflect"
    "sort"
    "strings"
    "testing"
)

func TestKCore(t *testing.T) {
    for _, tc := range kCoreTestCases {
        t.Run(tc.description, func(t *testing.T) {
            // Convert network strings to a reader
            reader := strings.NewReader(strings.Join(tc.network, "\n"))
            
            // Call the function being tested
            result, err := FindKCore(reader, tc.k)
            
            // Check error cases
            if tc.expectErr {
                if err == nil {
                    t.Errorf("Expected error but got none")
                }
                return
            }
            if err != nil {
                t.Errorf("Unexpected error: %v", err)
                return
            }
            
            // Sort both slices for comparison
            sort.Ints(result)
            expected := make([]int, len(tc.expected))
            copy(expected, tc.expected)
            sort.Ints(expected)
            
            // Compare results
            if !reflect.DeepEqual(result, expected) {
                t.Errorf("Expected %v but got %v", expected, result)
            }
        })
    }
}

func TestEdgeCases(t *testing.T) {
    tests := []struct {
        name     string
        input    string
        k        int
        wantErr  bool
    }{
        {
            name:     "Invalid format - missing colon",
            input:    "1,2,3\n",
            k:        2,
            wantErr:  true,
        },
        {
            name:     "Invalid format - non-numeric ID",
            input:    "a:1,2,3\n",
            k:        2,
            wantErr:  true,
        },
        {
            name:     "Invalid format - non-numeric friend ID",
            input:    "1:a,2,3\n",
            k:        2,
            wantErr:  true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            reader := strings.NewReader(tt.input)
            _, err := FindKCore(reader, tt.k)
            if (err != nil) != tt.wantErr {
                t.Errorf("FindKCore() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}

func BenchmarkKCore(b *testing.B) {
    // Create a medium-sized test network
    var networkBuilder strings.Builder
    for i := 1; i <= 1000; i++ {
        friends := make([]string, 0)
        for j := 1; j <= 10; j++ {
            if i != j {
                friends = append(friends, string(rune(j)))
            }
        }
        networkBuilder.WriteString(string(rune(i)))
        networkBuilder.WriteString(":")
        networkBuilder.WriteString(strings.Join(friends, ","))
        networkBuilder.WriteString("\n")
    }
    network := networkBuilder.String()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        reader := strings.NewReader(network)
        _, err := FindKCore(reader, 5)
        if err != nil {
            b.Fatal(err)
        }
    }
}