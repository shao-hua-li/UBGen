

#define _INTOPL0 
#define _INTOPR0 
#include<stdio.h>
int g1, g2;

int foo(int p) 

{
    



int a = 1;
    

if (p>a) 

{
        


int c = 1;
        


a = ((a) _INTOPL0) / ((1) -(1)/*UBFUZZ*/);
    }


    

return a;
}



int main() {
    
int x;
    x = foo(2);
    printf("checksum = %d\n", x);
}
