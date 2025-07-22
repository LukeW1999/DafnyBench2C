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