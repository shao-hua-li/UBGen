#include<stdio.h>
int g1=1, g2[5];

int foo(int p) {
    int a = g1;
    int *b = &g2[2];
    for(int i=0; i<1;i++) {
        if(*(b+i)||g1)
            g1 = 1;
    }
    return a;
}

int main() {
    int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
