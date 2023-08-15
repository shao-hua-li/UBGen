#include<stdio.h>
int g1, *g2;

int foo(int p) {
    int *a[1] = {&g1};
    if (p>0) {
        int *c[2] = {&g1, &g1};
        int i;
    }
    return a[0][0];
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
