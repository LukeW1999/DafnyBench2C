#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

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

int main() {
    // Test empty string
    char* empty = ToLowercase("");
    if (strcmp(empty, "") != 0) {
        printf("Test 1 failed\n");
        free(empty);
        return 1;
    }
    free(empty);

    // Test all uppercase
    char* upper = ToLowercase("ABC");
    if (strcmp(upper, "abc") != 0) {
        printf("Test 2 failed\n");
        free(upper);
        return 1;
    }
    free(upper);

    // Test mixed case
    char* mixed = ToLowercase("AbC");
    if (strcmp(mixed, "abc") != 0) {
        printf("Test 3 failed\n");
        free(mixed);
        return 1;
    }
    free(mixed);

    // Test all lowercase
    char* lower = ToLowercase("abc");
    if (strcmp(lower, "abc") != 0) {
        printf("Test 4 failed\n");
        free(lower);
        return 1;
    }
    free(lower);

    // Test NULL input (shouldn't crash)
    char* null_test = ToLowercase(NULL);
    if (null_test != NULL) {
        printf("Test 5 failed\n");
        free(null_test);
        return 1;
    }

    printf("All tests passed\n");
    return 0;
}