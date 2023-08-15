




#include<stdint.h>

int foo(int p) 

{
    




uint32_t a[3]={0}, b=1;
    


if(/*initS*/b/*initE*/)
        

{


b++;
}


    
uint32_t UNINIT_var;//UBFUZZ 

if(UNINIT_var)
        

{


return b;
}


}



int main() {
    
int x;
    x = foo(2);
}
