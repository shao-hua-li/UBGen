



#define _INTOPL0 
uint32_t MUT_VAR = +(30)/*UBFUZZ*/;
#define _INTOPR0 +(MUT_VAR) 
#include<stdio.h>
#include<stdint.h>
int g1, g2;

int foo(int p) 

{
    



uint32_t a = 8;
    


uint32_t b = 2;
    


a = ((a) _INTOPL0) << ((b) _INTOPR0);
    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
