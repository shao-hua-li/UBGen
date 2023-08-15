#include<stdio.h>
int g1, g2;

int foo(int p) {
    int a = -1;
    int b = -1;
    if (p>a) {
        int c = 1;
        a = a % b;
    }
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
