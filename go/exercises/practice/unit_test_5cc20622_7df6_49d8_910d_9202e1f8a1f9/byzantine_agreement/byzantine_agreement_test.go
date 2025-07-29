package byzantine_agreement

import (
	"testing"
)

func TestByzantineAgreement_AllHonest(t *testing.T) {
	n := 4
	f := 0
	initialValues := []int{1, 1, 1, 1}

	result := ByzantineAgreement(n, f, initialValues)
	if result != 1 {
		t.Errorf("Expected 1, got %d", result)
	}
}

func TestByzantineAgreement_AllHonestSplit(t *testing.T) {
	n := 4
	f := 0
	initialValues := []int{1, 0, 1, 0}

	result := ByzantineAgreement(n, f, initialValues)
	if result != 1 && result != 0 {
		t.Errorf("Expected 0 or 1, got %d", result)
	}
}

func TestByzantineAgreement_WithFaultyNodes(t *testing.T) {
	n := 7
	f := 2
	initialValues := []int{1, 1, 0, 1, 0, 1, 1}

	result := ByzantineAgreement(n, f, initialValues)
	if result != 1 && result != 0 {
		t.Errorf("Expected 0 or 1, got %d", result)
	}
}

func TestByzantineAgreement_MinimumNodes(t *testing.T) {
	n := 4
	f := 1
	initialValues := []int{1, 1, 0, 1}

	result := ByzantineAgreement(n, f, initialValues)
	if result != 1 && result != 0 {
		t.Errorf("Expected 0 or 1, got %d", result)
	}
}

func TestByzantineAgreement_AllFaulty(t *testing.T) {
	n := 3
	f := 1
	initialValues := []int{1, 0, 1}

	result := ByzantineAgreement(n, f, initialValues)
	if result != 1 && result != 0 {
		t.Errorf("Expected 0 or 1, got %d", result)
	}
}

func BenchmarkByzantineAgreement(b *testing.B) {
	n := 10
	f := 3
	initialValues := []int{1, 0, 1, 0, 1, 0, 1, 0, 1, 0}

	for i := 0; i < b.N; i++ {
		ByzantineAgreement(n, f, initialValues)
	}
}