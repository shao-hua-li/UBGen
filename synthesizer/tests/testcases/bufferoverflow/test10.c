#include<stdio.h>
int g1, g2[5];

int foo(int p) {
    int *a = &g1;
    int **b = &a;
    int c;
    c = **b + 1;
    return c;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
