



#define _INTOPL0 
int32_t MUT_VAR = +(30)/*UBFUZZ*/;
#define _INTOPR0 +(MUT_VAR) 
#include<stdint.h>
#include<stdio.h>
int g1, g2;

int foo(int p) 

{
    



char a = 10;
    


char b = 2;
    


a = ((a) _INTOPL0) >> ((b) _INTOPR0);
    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
