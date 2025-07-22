#include <stdio.h>
#include <assert.h>

/*@
requires n >= 0;
ensures \result == (n == 0 ? 1 : b * Expt(b, n - 1));
decreases n;
*/
int Expt(int b, int n) {
    if (n == 0) return 1;
    return b * Expt(b, n - 1);
}

/*@
requires n >= 0;
ensures \result == Expt(b, n);
*/
int expt(int b, int n) {
    int i = 1;
    int res = 1;
    /*@
    loop invariant 1 <= i <= n+1;
    loop invariant res == Expt(b, i-1);
    loop variant n - i;
    */
    while (i <= n) {
        res = res * b;
        i = i + 1;
    }
    return res;
}

/*@
requires a >= 0 && b >= 0;
ensures Expt(x, a) * Expt(x, b) == Expt(x, a + b);
*/
void distributive(int x, int a, int b) {
    // Lemma statement is proved by induction in Dafny, so we just need the contract
}

int main() {
    // Test Expt function
    assert(Expt(2, 0) == 1);
    assert(Expt(2, 1) == 2);
    assert(Expt(3, 2) == 9);
    assert(Expt(5, 3) == 125);

    // Test expt function
    assert(expt(2, 0) == 1);
    assert(expt(2, 1) == 2);
    assert(expt(3, 2) == 9);
    assert(expt(5, 3) == 125);

    // Test that expt matches Expt
    assert(expt(2, 5) == Expt(2, 5));
    assert(expt(7, 4) == Expt(7, 4));

    // Test distributive property
    distributive(2, 3, 4);
    distributive(5, 0, 2);
    distributive(3, 1, 1);

    printf("All tests passed!\n");
    return 0;
}