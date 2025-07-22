#include <limits.h>
#include <stdio.h>
#include <assert.h>

/*@
requires x > INT_MIN; // Avoid undefined behavior for most negative number
ensures \result >= 0;
ensures x >= 0 ==> \result == x;
ensures x < 0 ==> \result == -x;
*/
int Abs(int x) {
    if (x < 0) {
        return -x;
    }
    return x;
}

int main() {
    // Test positive number
    assert(Abs(5) == 5);
    
    // Test zero
    assert(Abs(0) == 0);
    
    // Test negative number
    assert(Abs(-5) == 5);
    
    // Test near INT_MIN boundary (but not INT_MIN due to precondition)
    assert(Abs(INT_MIN + 1) == -(INT_MIN + 1));
    
    printf("All tests passed!\n");
    return 0;
}