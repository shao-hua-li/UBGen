



int32_t MUT_VAR = +(2147483646)/*UBFUZZ*/;
#define _INTOPL0 +(MUT_VAR) 
#define _INTOPR0 
#include<stdint.h>
#include<stdio.h>
int g1, g2;

int foo(int p) 

{
    



int a = 1;
    

if (p>a) 

{
        


int c = 1;
        


a = ((a) _INTOPL0) + ((1) _INTOPR0);
    }


    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
