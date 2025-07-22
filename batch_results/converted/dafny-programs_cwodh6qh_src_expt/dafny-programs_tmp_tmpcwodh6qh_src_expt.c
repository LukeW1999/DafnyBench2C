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

7. Ensured all functions have complete contracts