#include<stdio.h>
#include<stdlib.h>

int foo(int p) {
    int a[3];
    a[0] = a[1] = 2;
    return a[1];
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
