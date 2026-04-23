#include <stdio.h>

int main() {
    int a, b, sum;

    // Read two integers
    scanf("%d %d", &a, &b);

    // Calculate sum
    sum = a + b;

    // Check if sum is even or odd
    if (sum % 2 == 0) {
        printf("%d is even", sum);
    } else {
        printf("%d is odd", sum);
    }

    return 0;
}