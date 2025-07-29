package adaptive_huffman

// Implementation of adaptive Huffman coding with dynamic dictionary expansion

// HuffmanNode represents a node in the Huffman tree
type HuffmanNode struct {
	Symbol    byte
	Frequency int
	Left      *HuffmanNode
	Right     *HuffmanNode
	Parent    *HuffmanNode
	Order     int // Keeps track of node order for sibling property
	IsLeaf    bool
}

// HuffmanTree represents the Huffman tree
type HuffmanTree struct {
	Root       *HuffmanNode
	NodeLookup map[byte]*HuffmanNode // Map from symbols to leaf nodes
	NodeList   []*HuffmanNode        // List of all nodes in order of increasing frequency
	EscNode    *HuffmanNode          // Reference to the escape symbol node
	NextOrder  int                   // Used to maintain the ordering of nodes
}

// NewHuffmanTree initializes a new Huffman tree with just the escape symbol
func NewHuffmanTree() *HuffmanTree {
	escNode := &HuffmanNode{
		Symbol:    0,       // Escape symbol represented by byte 0
		Frequency: 0,
		Left:      nil,
		Right:     nil,
		Parent:    nil,
		Order:     0,
		IsLeaf:    true,
	}

	tree := &HuffmanTree{
		Root:       escNode,
		NodeLookup: make(map[byte]*HuffmanNode),
		NodeList:   []*HuffmanNode{escNode},
		EscNode:    escNode,
		NextOrder:  1,
	}

	return tree
}

// GetCode returns the Huffman code for a symbol (or ESC if not found)
func (tree *HuffmanTree) GetCode(symbol byte) ([]byte, bool) {
	node, found := tree.NodeLookup[symbol]
	if !found {
		// Return the code for the escape symbol
		return getPathToRoot(tree.EscNode), false
	}
	return getPathToRoot(node), true
}

// getPathToRoot returns the path from a node to the root (the Huffman code)
func getPathToRoot(node *HuffmanNode) []byte {
	var code []byte
	current := node
	for current.Parent != nil {
		parent := current.Parent
		if parent.Left == current {
			code = append([]byte{'0'}, code...)
		} else {
			code = append([]byte{'1'}, code...)
		}
		current = parent
	}
	return code
}

// AddSymbol adds a new symbol to the Huffman tree
func (tree *HuffmanTree) AddSymbol(symbol byte) {
	// Create a new internal node to replace the escape node
	newInternal := &HuffmanNode{
		Symbol:    0,
		Frequency: 0,
		Left:      nil,
		Right:     nil,
		Parent:    tree.EscNode.Parent,
		Order:     tree.NextOrder,
		IsLeaf:    false,
	}
	tree.NextOrder++

	// Create a new leaf node for the symbol
	newLeaf := &HuffmanNode{
		Symbol:    symbol,
		Frequency: 0,
		Left:      nil,
		Right:     nil,
		Parent:    newInternal,
		Order:     tree.NextOrder,
		IsLeaf:    true,
	}
	tree.NextOrder++

	// Create a new escape node
	newEscNode := &HuffmanNode{
		Symbol:    0,
		Frequency: 0,
		Left:      nil,
		Right:     nil,
		Parent:    newInternal,
		Order:     tree.NextOrder,
		IsLeaf:    true,
	}
	tree.NextOrder++

	// Update the Huffman tree
	newInternal.Left = newEscNode
	newInternal.Right = newLeaf

	// If the escape node was the root
	if tree.EscNode.Parent == nil {
		tree.Root = newInternal
	} else {
		// Replace the escape node with the new internal node in the parent
		if tree.EscNode.Parent.Left == tree.EscNode {
			tree.EscNode.Parent.Left = newInternal
		} else {
			tree.EscNode.Parent.Right = newInternal
		}
	}

	// Update the node list
	tree.NodeList = append(tree.NodeList, newInternal, newLeaf, newEscNode)
	
	// Update the node lookup
	tree.NodeLookup[symbol] = newLeaf
	
	// Update the escape node reference
	tree.EscNode = newEscNode

	// Increment the frequency of the new leaf node
	tree.IncrementFrequency(newLeaf)
}

// IncrementFrequency increments the frequency of a node and updates the tree
func (tree *HuffmanTree) IncrementFrequency(node *HuffmanNode) {
	for node != nil {
		// Increment the frequency
		node.Frequency++
		
		// Check and maintain sibling property
		tree.ReorderNodes(node)
		
		// Move up the tree
		node = node.Parent
	}
}

// ReorderNodes maintains the sibling property by reordering nodes if necessary
func (tree *HuffmanTree) ReorderNodes(node *HuffmanNode) {
	// Find the highest-ordered node with the same frequency
	var swapNode *HuffmanNode
	for _, n := range tree.NodeList {
		if n != node && n.Frequency == node.Frequency && n.Order > node.Order {
			if swapNode == nil || n.Order > swapNode.Order {
				swapNode = n
			}
		}
	}

	if swapNode != nil {
		// Don't swap if one node is an ancestor of the other
		if !isAncestor(node, swapNode) && !isAncestor(swapNode, node) {
			tree.SwapNodes(node, swapNode)
		}
	}
}

// isAncestor checks if node1 is an ancestor of node2
func isAncestor(node1, node2 *HuffmanNode) bool {
	current := node2
	for current != nil {
		if current == node1 {
			return true
		}
		current = current.Parent
	}
	return false
}

// SwapNodes swaps two nodes in the Huffman tree
func (tree *HuffmanTree) SwapNodes(node1, node2 *HuffmanNode) {
	// Swap the parents' children
	if node1.Parent != nil {
		if node1.Parent.Left == node1 {
			node1.Parent.Left = node2
		} else {
			node1.Parent.Right = node2
		}
	}
	
	if node2.Parent != nil {
		if node2.Parent.Left == node2 {
			node2.Parent.Left = node1
		} else {
			node2.Parent.Right = node1
		}
	}
	
	// Swap parents
	node1.Parent, node2.Parent = node2.Parent, node1.Parent
	
	// If either node was the root, update the root
	if tree.Root == node1 {
		tree.Root = node2
	} else if tree.Root == node2 {
		tree.Root = node1
	}
	
	// Swap orders
	node1.Order, node2.Order = node2.Order, node1.Order
}

// Compress encodes a string using adaptive Huffman coding
func Compress(input string) string {
	if len(input) == 0 {
		return ""
	}
	
	tree := NewHuffmanTree()
	var result []byte
	
	for i := 0; i < len(input); i++ {
		symbol := input[i]
		code, found := tree.GetCode(symbol)
		
		// Append the code to the result
		result = append(result, code...)
		
		if !found {
			// Append the fixed-length code for the new symbol (8-bit ASCII)
			for j := 7; j >= 0; j-- {
				bit := (symbol >> uint(j)) & 1
				if bit == 1 {
					result = append(result, '1')
				} else {
					result = append(result, '0')
				}
			}
			
			// Add the symbol to the tree
			tree.AddSymbol(symbol)
		} else {
			// Increment the frequency of the existing symbol's node
			tree.IncrementFrequency(tree.NodeLookup[symbol])
		}
	}
	
	return string(result)
}

// Decompress decodes a bitstream created by the Compress function
func Decompress(compressed string) string {
	if len(compressed) == 0 {
		return ""
	}
	
	tree := NewHuffmanTree()
	var result []byte
	var i int
	
	for i < len(compressed) {
		// Traverse the tree until a leaf node is reached
		node := tree.Root
		for !node.IsLeaf && i < len(compressed) {
			if compressed[i] == '0' {
				node = node.Left
			} else {
				node = node.Right
			}
			i++
		}
		
		// Check if we found the escape symbol
		if node == tree.EscNode {
			// Read the next 8 bits to get the new symbol
			if i+8 <= len(compressed) {
				var symbol byte
				for j := 0; j < 8; j++ {
					symbol = (symbol << 1)
					if compressed[i+j] == '1' {
						symbol |= 1
					}
				}
				i += 8
				
				// Add the symbol to the result
				result = append(result, symbol)
				
				// Add the symbol to the tree
				tree.AddSymbol(symbol)
			} else {
				// Not enough bits for a full symbol, this is an error
				break
			}
		} else {
			// Add the found symbol to the result
			result = append(result, node.Symbol)
			
			// Increment the frequency of the node
			tree.IncrementFrequency(node)
		}
	}
	
	return string(result)
}