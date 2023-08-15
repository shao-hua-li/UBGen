#include<stdio.h>
#include<stdint.h>
int g1, g2;

int foo(int p) {
    int64_t a = 10;
    int64_t b = 2;
    a = a >> b;
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
