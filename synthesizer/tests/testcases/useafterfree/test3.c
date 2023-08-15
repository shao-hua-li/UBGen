#include<stdio.h>
#include<stdlib.h>

int g;
int foo(int p) {
    int *a[1][1]={&g};
    return *a[0][0];
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
