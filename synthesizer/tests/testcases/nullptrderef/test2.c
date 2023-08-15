#include<stdio.h>
int g1;
int *g2=&g1;

int foo(int p) {
    int b, **a = &g2;
    b = **a +1;
    return b;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
