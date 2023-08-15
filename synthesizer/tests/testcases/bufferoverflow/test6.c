struct a {
  int x;
};

int g() {
  struct a b[2];
  struct a *c = b, *d = b;
  int e;
  return c->x;
}

int main() { 
    g(); 
    printf("checksum = 0");
    return 0;
}