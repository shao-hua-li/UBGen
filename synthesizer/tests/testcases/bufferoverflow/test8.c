#include<stdio.h>
int g1, g2[5];

int foo(int p) {
    int a, *b = &g1;
    b = &g2[4];
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
