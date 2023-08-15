#include<stdint.h>

int foo(int p) {
    uint32_t a[3]={0}, b=1;
    if(b)
        b++;
    if(b)
        return b;
}

int main() {
    int x;
    x = foo(2);
}
