#include<stdio.h>
int g1, *g2;

int foo(int p) {
    if (p>0) {
        int c;
        c = 1;
    }
    g2 = &g1;
    return *g2;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
