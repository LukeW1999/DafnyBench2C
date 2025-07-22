/*@ predicate IsUpperCase(char c) =
(int)c >= 65 && (int)c <= 90;
*/
/*@ predicate IsUpperLowerPair(char C, char c) =
(int)C == (int)c - 32;
*/
/*@ ensures \result == (char)((c + 32) % 128);
*/
char Shift32(char c) {
return (char)((c + 32) % 128);
}
/*@ requires s != NULL;
requires \strlen(s) < INT_MAX;
ensures \result != NULL ==> \strlen(\result) == \strlen(s);
ensures \result != NULL ==> (\forall int i; 0 <= i < \strlen(s) ==>
(IsUpperCase(s[i]) ? IsUpperLowerPair(s[i], \result[i]) : \result[i] == s[i]));
ensures \result != NULL ==> \result[\strlen(s)] == '\0';
*/
char* ToLowercase(const char* s) {
size_t length = strlen(s);
char* result = malloc(length + 1);
if (result == NULL) return NULL;
/*@ loop assigns i, result[0..length];
loop invariant 0 <= i <= length;
loop invariant \forall integer k; 0 <= k < i ==>
(IsUpperCase(s[k]) ? IsUpperLowerPair(s[k], result[k]) : result[k] == s[k]);
*/
for (size_t i = 0; i <= length; i++) {
if (i < length && IsUpperCase(s[i])) {
result[i] = Shift32(s[i]);
} else {
result[i] = s[i];
}
}
return result;
}

8. Fixed loop condition to properly handle string termination