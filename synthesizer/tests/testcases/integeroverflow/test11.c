struct a {
  signed b : 1;
  signed c : 4;
};
int d, e, f = 2056809477, h;
int *g = &f, *i = &f;
int foo() {
  struct a j;
  for (; d >= 0; d -= 4) {
    for (; e <= 7; e++) {
      j.c = *i + 1;
      *g = 0;
    }
  }
}
int main(){
    foo();
}