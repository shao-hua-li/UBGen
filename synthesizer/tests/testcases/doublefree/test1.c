#include<stdio.h>
#include<stdlib.h>
#define free_1(arr)   free(arr);
int g;
int foo(int p) {
    int a[3];
    a[0] = a[1] = 2;
    g=1;
    return 1;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
