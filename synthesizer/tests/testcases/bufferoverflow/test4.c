struct a {
  int x;
};
struct a b[2];
struct a *c = b, *d = b;
int e;

int g() {
  *c = *b;
  return c->x;
}

int main() { 
    g(); 
    printf("checksum = 0");
    return 0;
}