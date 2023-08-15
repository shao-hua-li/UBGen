



#define _INTOPL0 
int32_t MUT_VAR = +(26)/*UBFUZZ*/;
#define _INTOPR0 +(MUT_VAR) 
#include<stdio.h>
#include<stdint.h>
int g1, g2;

int foo(int p) 

{
    



int32_t a = 8;
    


int32_t b = 2;
    


a = ((a) _INTOPL0) << ((b) _INTOPR0);
    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
