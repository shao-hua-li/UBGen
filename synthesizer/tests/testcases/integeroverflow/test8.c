#include<stdio.h>
#include<stdint.h>
int g1, g2;

int foo(int p) {
    int32_t a = 8;
    int32_t b = 2;
    a = a << b;
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
