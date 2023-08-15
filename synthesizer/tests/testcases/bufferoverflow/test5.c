void foo()
{
  int d[1][1];
  for (int a = 0; a < 1; a++)
    d[0][a] = 0;
}

int main()
{
  foo();
  printf("checksum = 0");
  return 0;
} 