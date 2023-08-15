#include<stdio.h>
int a;
int *b = &a;
void(c)(int p) {}
int foo() {
  c(*b = 1);
  return 1;
}

int main() {
    int x;
    x = foo();
    printf("checksum = %d\n", x);
}
