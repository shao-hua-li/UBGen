#include<stdio.h>
int a;
int *b = &a;
void(c)(short) {}
int foo() {
  for (int i=0;i<2;i++) {
    *b = 1;
  }
  return 1;
}

int main() {
    int x;
    x = foo();
    printf("checksum = %d\n", x);
}
