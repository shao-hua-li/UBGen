#include<stdio.h>
int a;
int *b = &a;
int **c = &b;
int ***d = &c;
int ****e = &d;
int foo() {
  int *f;
  f = *e;
  return 1;
}

int main() {
    int x;
    x = foo();
    printf("checksum = %d\n", x);
}
