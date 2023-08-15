long a[24];
int b;
int *c = &b;
static int d;
int foo() {
  d = 2;
  for (; d >= 0; d--)
    b = a[d * 8];
}
int main() {
  foo();
}
