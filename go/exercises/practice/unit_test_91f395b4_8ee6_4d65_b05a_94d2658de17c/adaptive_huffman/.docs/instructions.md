Okay, here's a challenging Go programming competition problem designed to be difficult and sophisticated:

**Problem: Adaptive Huffman Compression with Dynamic Dictionary Expansion**

**Description:**

You are tasked with implementing an adaptive Huffman compression algorithm.  This algorithm dynamically builds a Huffman tree based on the frequencies of the symbols encountered in the input data stream. However, unlike standard adaptive Huffman, this implementation features a dynamic dictionary that can expand to accommodate new symbols *during* the compression process.

**Details:**

1.  **Initial State:** Start with a minimal Huffman tree containing a single "escape" symbol (ESC). This symbol represents any character *not* yet present in the tree. Assign it a frequency of 1.

2.  **Encoding Process:**
    *   For each input symbol:
        *   **If the symbol exists in the current Huffman tree:** Encode the symbol using its Huffman code.
        *   **If the symbol is NOT in the tree (new symbol):**
            *   Encode the ESC symbol using its Huffman code.
            *   Encode the new symbol using a fixed-length code (e.g., 8-bit ASCII).  This fixed-length code *immediately* follows the ESC code in the output.
            *   Add the new symbol to the Huffman tree with a frequency of 1.
        *   Increment the frequency of the encoded symbol (or ESC if a new symbol was encountered).
        *   Update the Huffman tree structure to maintain the Huffman property (symbols with higher frequencies should be closer to the root). Use the "sibling property" and "update procedure" (described below) to ensure this.

3.  **Huffman Tree Update Procedure:**

    *   **Sibling Property:** A Huffman tree must satisfy the sibling property:  nodes (both internal and leaf) can be arranged in order of non-decreasing frequency, and each node (except the root) has a sibling, and each pair of siblings are consecutive in the ordering.

    *   **Update Procedure:** After encoding a symbol and incrementing its frequency, traverse the path from the encoded node to the root. For each node on this path:
        *   **Check Sibling Property:** If the current node's frequency is less than a node *above* it (closer to the root) but to its *left* in the sibling ordering (meaning it's not on the path to the root of the currently considered symbol), swap the positions of these two nodes.  This preserves the sibling property.
        *   Increment the frequency of the current node.

4.  **Fixed-Length Encoding:** Use 8-bit ASCII for encoding new symbols after the ESC code.

5.  **Output:** Your program should output the compressed bitstream.  Since bitstreams are difficult to represent directly, output a string of '0's and '1's representing the bitstream.  For example, if the Huffman code for 'A' is '101' and the fixed-length code for 'B' is '01000010', the output string might be "10101000010"

**Constraints and Requirements:**

*   **Input:** A string of ASCII characters (length up to 100,000 characters).
*   **Output:** A string of '0's and '1's representing the compressed bitstream.
*   **Memory Limit:** 256 MB
*   **Time Limit:** 5 seconds
*   **Correctness:**  The output must be a valid adaptive Huffman encoding of the input string according to the rules above. While a perfect compression ratio isn't required, solutions that consistently produce *larger* outputs than the original input will be penalized.
*   **Efficiency:** The algorithm *must* be efficient enough to handle the given input size within the time and memory constraints. Naive tree implementations will likely time out. Consider efficient data structures for frequency tracking and tree traversal.
*   **Edge Cases:** Handle empty input strings gracefully. Ensure the code correctly handles all 256 ASCII characters, even if they appear infrequently or only at the end of the input.

**Grading Criteria:**

*   **Correctness (70%):** Does the code produce a valid adaptive Huffman encoding according to the problem description?
*   **Efficiency (20%):** How well does the code compress the input data, and how quickly does it execute?
*   **Code Clarity and Structure (10%):** Is the code well-organized, readable, and maintainable?

This problem requires a solid understanding of Huffman coding, tree data structures, and bit manipulation. Efficient implementations will likely involve using techniques like pointers (or equivalent in Go) to efficiently update the tree structure. The constraints are tight enough to encourage careful design and optimization. Good luck!
