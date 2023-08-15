#include<stdint.h>
#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a = 1;
    if (p>a) {
        int c = 1;
        a = a++ + 1 + ++c;
    }
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
