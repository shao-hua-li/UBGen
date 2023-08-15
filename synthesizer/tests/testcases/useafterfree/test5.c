#include<stdio.h>
#include<stdlib.h>

int g;
int foo(int p) {
    int a[1][1]={g};
    int b[2]={a[0][0], a[0][0]};
    return 1;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
