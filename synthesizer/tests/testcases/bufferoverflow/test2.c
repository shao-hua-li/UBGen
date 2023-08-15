#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a, *b = &g1;
    a = *b + 1;
    int d[2] = {1, 2};
    if (p>a) {
        int c = 1;
        a = a + c;
    }
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
