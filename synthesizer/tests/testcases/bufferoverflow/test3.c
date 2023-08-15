#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a=0, *b = &g1;
    while (p>=a) {
        int c = 1;
        a = a + c;
        p--;
    }
    a = *b + 1;
    int d[2] = {1, 2};
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
