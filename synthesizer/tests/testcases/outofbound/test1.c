#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a = 1;
    int *b = &g1;
    int d[2] = {1, 2};
    d[1]++;
    if (p>a) {
        int c = 1;
        a = a + c;
    }
    a = a + 1;
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
