




#include<stdint.h>

int foo(int p) 

{
    




uint32_t a[3]={0}, b=1;
    
uint32_t UNINIT_var;//UBFUZZ 

if(UNINIT_var)
        

{


b++;
}


    


if(/*initS*/b/*initE*/)
        

{


return b;
}


}



int main() {
    
int x;
    x = foo(2);
}
