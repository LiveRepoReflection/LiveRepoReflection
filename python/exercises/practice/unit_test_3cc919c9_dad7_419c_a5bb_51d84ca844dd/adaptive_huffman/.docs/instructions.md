Okay, I'm ready to set a challenging coding problem. Here's the question:

## Problem: Adaptive Huffman Compression with Dynamic Tree Updates

### Question Description:

You are tasked with implementing an Adaptive Huffman compression algorithm. Unlike static Huffman coding where the tree is pre-computed, Adaptive Huffman coding dynamically updates the Huffman tree as it processes the input stream. This allows the algorithm to adapt to changing symbol frequencies, potentially achieving better compression ratios.

**Specific Requirements:**

1.  **NYT (Not Yet Transmitted) Node:** Implement the algorithm using a designated NYT node. Initially, the tree consists of only the NYT node. When a new symbol is encountered, the NYT node is replaced by a new NYT node and a leaf node for the new symbol. The weight of the new leaf node is 1. The weight of the new NYT node is 0.
2.  **Weight Update and Sibling Property:** After transmitting (or initially encountering) a symbol, increment the weight of the corresponding leaf node and all its ancestors towards the root. After each weight update, ensure that the sibling property is maintained. The sibling property states that nodes at each level must be arranged in non-decreasing order of their weights. If incrementing a node's weight violates the sibling property, swap the node with the rightmost node in its level that has a weight less than or equal to the incremented node's new weight.  Crucially, maintain the "block leader" principle - the *rightmost* node is the one chosen for swapping when multiple nodes have the same weight.
3.  **Encoding:** When a symbol is encountered for the first time, transmit the code for the NYT node *followed* by a fixed-length code for the symbol itself. You are to use 8-bit ASCII encoding for the symbols (i.e., each new symbol's initial code is its ASCII representation). When a known symbol is encountered, transmit the code for the corresponding leaf node.
4.  **Decoding:** Implement the corresponding decoding algorithm that reconstructs the original input stream from the adaptively Huffman-compressed bitstream.
5.  **Input:** A string of ASCII characters.
6.  **Output:**
    *   **Encoding:** A string of '0's and '1's representing the adaptively Huffman-encoded bitstream.
    *   **Decoding:** The original input string.
7.  **Optimization:** The core challenge lies in efficiently maintaining the Huffman tree and performing the necessary updates while meeting strict performance requirements.  The solution should be performant enough to handle reasonably large input strings (e.g., up to 1MB) within a reasonable time limit. (e.g., Encoding and Decoding each within 5 seconds).
8.  **Constraints:**
    *   Assume the input string consists only of ASCII characters (0-127).
    *   The solution must be memory-efficient. Avoid unnecessary memory allocations or copies, especially for large input strings.
    *   The solution must be robust and handle all possible input strings correctly.
9.  **Error Handling** The code should handle cases of empty input gracefully.

**Scoring:**

*   Correctness (primary): The solution must correctly encode and decode the input string.
*   Efficiency (secondary): Solutions will be evaluated based on their runtime performance and memory usage, with a strong emphasis on efficient tree updates and code generation.

This problem requires a solid understanding of Huffman coding, tree data structures, and bit manipulation. The dynamic nature of the algorithm and the need for efficient tree updates make it a challenging problem suitable for a high-level programming competition. Good luck!
