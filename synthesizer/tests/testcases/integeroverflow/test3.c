#include<stdint.h>
#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a = 10;
    int b = 100;
    a = a - b;
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
