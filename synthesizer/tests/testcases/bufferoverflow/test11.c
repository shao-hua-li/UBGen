struct a {
  long b;
  short c;
  int d;
  int e;
  long f;
  short g;
  long i;
  char j;
};
struct k {
  long b;
  struct a l;
  int e;
};
int foo() {
  struct k o[3];
  o[0].l.e = 0;
}
int main(){
    foo();
}
