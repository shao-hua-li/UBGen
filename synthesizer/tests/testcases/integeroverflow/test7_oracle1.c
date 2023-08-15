



#define _INTOPL0 
int64_t MUT_VAR = +(62)/*UBFUZZ*/;
#define _INTOPR0 +(MUT_VAR) 
#include<stdio.h>
#include<stdint.h>
int g1, g2;

int foo(int p) 

{
    



int64_t a = 10;
    


int64_t b = 2;
    


a = ((a) _INTOPL0) >> ((b) _INTOPR0);
    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
