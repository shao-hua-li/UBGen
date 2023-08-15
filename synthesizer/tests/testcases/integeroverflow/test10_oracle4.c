



int32_t MUT_VAR = +(2147483646)/*UBFUZZ*/;
#define _INTOPL0 +(MUT_VAR) 
#define _INTOPL1 
#define _INTOPR0 
#define _INTOPR1 
#include<stdint.h>
#include<stdio.h>
int g1, g2;

int foo(int p) 

{
    



int a = 1;
    

if (p>a) 

{
        


int c = 1;
        



a = ((((a++) _INTOPL1) + ((1) _INTOPL0)) _INTOPR1) + ((++c) _INTOPR0);
    }


    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
