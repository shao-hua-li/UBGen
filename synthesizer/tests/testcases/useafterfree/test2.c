#include<stdio.h>
#include<stdlib.h>

int foo(int p) {
    int a[1][1]={1};
    a[0][0] = (long)a[0][0] + 2;
    return a[0][0];
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
