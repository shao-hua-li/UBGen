struct a {
  int x;
};

int g() {
  struct a b;
  struct a c[1];
  int e;
  return b.x;
}

int main() { 
    g(); 
    printf("checksum = 0");
    return 0;
}